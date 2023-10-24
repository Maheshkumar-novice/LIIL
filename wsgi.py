from flask import Flask, Response, redirect, render_template, request, url_for
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

engine = create_engine("sqlite:///main.db", echo=True)


class Base(DeclarativeBase):
    pass


class LaterLink(Base):
    __tablename__ = "later_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(500))


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    with Session(engine) as session:
        return render_template("home.html", links=session.scalars(select(LaterLink)))


@app.route("/", methods=["POST"])
def create() -> Response:
    link = request.form["link"]
    with Session(engine) as session:
        session.add(LaterLink(link=link))
        session.commit()

    return redirect(url_for("home"))


@app.route("/delete/<int:id>", methods=["GET"])
def delete(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)
        session.delete(link)
        session.commit()

    return redirect(url_for("home"))


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
