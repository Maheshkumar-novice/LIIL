from flask import Flask, request, render_template, redirect, url_for

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, Session
from sqlalchemy import String, create_engine, select

engine = create_engine('sqlite:///main.db', echo=True)

class Base(DeclarativeBase):
    pass

class LaterLink(Base):
    __tablename__ = 'later_links'

    id: Mapped[int] = mapped_column(primary_key=True)
    link: Mapped[str] = mapped_column(String(500))


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    links = []
    with Session(engine) as session:
        for link in session.scalars(select(LaterLink)):
            links.append(link)

    return render_template('home.html', links=links)


@app.route('/', methods=['POST'])
def create():
    link = request.form['link']
    with Session(engine) as session:
        session.add(LaterLink(link=link))
        session.commit()

    return redirect(url_for('home'))


@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    with Session(engine) as session:
        link = session.get(LaterLink, id)
        session.delete(link)
        session.commit()

    return redirect(url_for('home'))

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
