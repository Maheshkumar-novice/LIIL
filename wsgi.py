import os
import traceback

import requests
from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()
engine = create_engine("sqlite:///main.db", echo=True)


CHANNEL_IDS = {
    "general": os.environ.get("GENERAL_CID"),
    "linux": os.environ.get("LINUX_CID"),
    "python": os.environ.get("PYTHON_CID"),
}


class Base(DeclarativeBase):
    pass


class LaterLink(Base):
    __tablename__ = "later_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(500))
    tag: Mapped[str] = mapped_column(String(100))


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    with Session(engine) as session:
        return render_template(
            "home.html",
            links=session.scalars(select(LaterLink)),
            tags=CHANNEL_IDS.keys(),
        )


@app.route("/", methods=["POST"])
def create() -> Response:
    link = request.form["link"]
    tag = request.form["tag"]
    with Session(engine) as session:
        session.add(LaterLink(link=link, tag=tag))
        session.commit()

    return redirect(url_for("home"))


@app.route("/delete/<int:id>", methods=["GET"])
def delete(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)
        session.delete(link)
        session.commit()

    return redirect(url_for("home"))


@app.route("/discord/<int:id>", methods=["GET"])
def discord(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)

        channel_id = CHANNEL_IDS.get(link.tag)
        token = os.environ.get("DISCORD_TOKEN")

        if not channel_id or not token:
            return redirect(url_for("home"))

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

    return redirect(url_for("home"))


if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
