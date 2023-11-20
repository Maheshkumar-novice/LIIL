import datetime
from typing import Annotated

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

from db import Base, engine
from wsgi import turbo

birthdays_blueprint = Blueprint("birthdays", __name__)


class Birthday(Base):
    __tablename__ = "birthdays"

    _timestamp = Annotated[
        datetime.datetime,
        mapped_column(nullable=True),
    ]

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(500))
    date: Mapped[_timestamp]
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        server_default=expression.false(),
    )


@birthdays_blueprint.route("/", methods=["GET"])
def home() -> str:
    return render_template(
        "birthdays/home.html",
    )


@birthdays_blueprint.route("/birthdays", methods=["GET"])
def birthdays() -> str:
    with Session(engine) as session:
        return render_template(
            "birthdays/birthdays.html",
            birthdays=session.scalars(
                select(Birthday)
                .where(Birthday.is_deleted == False)  # noqa: E712
                .order_by(Birthday.date.desc()),
            ),
        )


@birthdays_blueprint.route("/current-birthdays", methods=["GET"])
def current_birthdays() -> str:
    current_date = datetime.datetime.now().replace(  # noqa: DTZ005
        year=2000,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    with Session(engine) as session:
        return render_template(
            "birthdays/current-birthdays.html",
            birthdays=session.scalars(
                select(Birthday).where(
                    Birthday.is_deleted == False,  # noqa: E712
                    Birthday.date == current_date,
                ),
            ),
        )


@birthdays_blueprint.route("/", methods=["POST"])
def create() -> Response:
    name = request.form["name"]
    date = request.form["date"]
    date = datetime.datetime.strptime(date, "%Y-%m-%d").astimezone().replace(year=2000)

    with Session(engine) as session:
        birthday = Birthday(name=name, date=date)
        session.add(birthday)
        session.commit()

        if turbo.can_stream():
            content = render_template("birthdays/birthday.html", birthday=birthday)

            if turbo.can_push():
                turbo.push(
                    turbo.append(content, target="birthdays"),
                )

            return turbo.stream(
                turbo.append(content, target="birthdays"),
            )

        return redirect(url_for("birthdays.home")), 303


@birthdays_blueprint.route("/delete/<int:id>", methods=["DELETE"])
def delete(id: int) -> Response:
    with Session(engine) as session:
        birthday = session.get(Birthday, id)
        birthday.is_deleted = True
        session.commit()

        if turbo.can_stream():
            if turbo.can_push():
                turbo.push(turbo.remove(id))
            return turbo.stream(turbo.remove(id))

    return redirect(url_for("birthdays.home")), 303
