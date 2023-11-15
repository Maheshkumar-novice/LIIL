import os
import traceback

import requests
from flask import (
    Blueprint,
    Response,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, Session, mapped_column
from sqlalchemy.sql import expression

from constants import CHANNEL_IDS
from db import Base, engine
from wsgi import turbo


class LaterLink(Base):
    __tablename__ = "later_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(500))
    tag: Mapped[str] = mapped_column(String(100))
    is_posted_to_discord: Mapped[bool] = mapped_column(
        default=False,
        server_default=expression.false(),
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default=expression.false(),
    )


liil_blueprint = Blueprint("liil", __name__)


@liil_blueprint.route("/", methods=["GET"])
def home() -> str:
    return render_template(
        "liil/home.html",
    )


@liil_blueprint.route("/links", methods=["GET"])
def links() -> str:
    with Session(engine) as session:
        return render_template(
            "liil/links.html",
            links=session.scalars(
                select(LaterLink).where(LaterLink.is_deleted == False),  # noqa: E712
            ),
        )


@liil_blueprint.route("/", methods=["POST"])
def create() -> Response:
    link = request.form["link"]
    tag = request.form["tag"]

    with Session(engine) as session:
        if not (link and tag and tag in CHANNEL_IDS):
            return redirect(url_for("liil.home"))

        link = LaterLink(link=link, tag=tag)
        session.add(link)
        session.commit()

        if turbo.can_stream():
            content = render_template("liil/link.html", link=link)

            if turbo.can_push():
                turbo.push(
                    turbo.append(content, target="links"),
                )

            return turbo.stream(
                turbo.append(content, target="links"),
            )

        return redirect(url_for("liil.home")), 303


@liil_blueprint.route("/delete/<int:id>", methods=["DELETE"])
def delete(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)
        link.is_deleted = True
        session.commit()

        if turbo.can_stream():
            if turbo.can_push():
                turbo.push(turbo.remove(id))
            return turbo.stream(turbo.remove(id))

    return redirect(url_for("lill.home")), 303


@liil_blueprint.route("/discord/<int:id>", methods=["POST"])
def discord(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)

        if link.is_posted_to_discord:
            return redirect(url_for("liil.home")), 303

        channel_id = CHANNEL_IDS.get(link.tag)
        token = os.environ.get("DISCORD_TOKEN")

        if not channel_id or not token:
            return redirect(url_for("liil.home")), 303

        headers = {
            "Authorization": f"Bot {token}",
            "User-Agent": "DiscordBot",
        }

        data = {"content": link.link}

        try:
            requests.post(
                f"https://discord.com/api/v9/channels/{channel_id}/messages",
                headers=headers,
                json=data,
                timeout=10,
            )
        except Exception as e:  # noqa: BLE001
            print(e, traceback.format_exc())  # noqa: T201
            return redirect(url_for("liil.home")), 303

        link.is_posted_to_discord = True
        session.commit()

        if turbo.can_stream():
            content = render_template("liil/link.html", link=link)
            if turbo.can_push():
                turbo.push(turbo.replace(content, id))

            return turbo.stream(turbo.replace(content, id))

    return redirect(url_for("liil.home")), 303


@liil_blueprint.route("/update/<int:id>", methods=["POST"])
def update(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)

        tag = request.form.get("item-tag")
        if (not tag) or (tag not in CHANNEL_IDS):
            return redirect(url_for("liil.home")), 303

        link.tag = tag

        if link.is_posted_to_discord:
            link.is_posted_to_discord = False

        session.commit()

        if turbo.can_stream():
            content = render_template("liil/link.html", link=link)
            if turbo.can_push():
                turbo.push(turbo.replace(content, id))

            return turbo.stream(turbo.replace(content, id))

    return redirect(url_for("liil.home")), 303
