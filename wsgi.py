import os
import traceback

import requests
from dotenv import load_dotenv
from flask import Flask, Response, redirect, render_template, request, url_for
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.sql import expression

load_dotenv()
engine = create_engine("sqlite:///main.db", echo=True)


CHANNEL_IDS = {
    "general": os.environ.get("GENERAL_CID"),
    "health": os.environ.get("HEALTH_CID"),
    "to-triage": os.environ.get("TO-TRIAGE_CID"),
    "ps-general": os.environ.get("PS-GENERAL_CID"),
    "ps-practice-sites": os.environ.get("PS-PRACTICE-SITES_CID"),
    "file-share": os.environ.get("FILE-SHARE_CID"),
    "career": os.environ.get("CAREER_CID"),
    "articles-blogs": os.environ.get("ARTICLES-BLOGS_CID"),
    "videos": os.environ.get("VIDEOS_CID"),
    "books": os.environ.get("BOOKS_CID"),
    "security": os.environ.get("SECURITY_CID"),
    "ui-ux-design": os.environ.get("UI-UX-DESIGN_CID"),
    "editing": os.environ.get("EDITING_CID"),
    "repos": os.environ.get("REPOS_CID"),
    "games": os.environ.get("GAMES_CID"),
    "cool-sites": os.environ.get("COOL-SITES_CID"),
    "learning-resources": os.environ.get("LEARNING-RESOURCES_CID"),
    "html": os.environ.get("HTML_CID"),
    "css": os.environ.get("CSS_CID"),
    "js": os.environ.get("JS_CID"),
    "react": os.environ.get("REACT_CID"),
    "flask": os.environ.get("FLASK_CID"),
    "typescript": os.environ.get("TYPESCRIPT_CID"),
    "web-gpu": os.environ.get("WEB-GPU_CID"),
    "python": os.environ.get("PYTHON_CID"),
    "c-cpp-asm": os.environ.get("C-CPP-ASM_CID"),
    "ruby": os.environ.get("RUBY_CID"),
    "go": os.environ.get("GO_CID"),
    "others": os.environ.get("OTHERS_CID"),
    "devops": os.environ.get("DEVOPS_CID"),
    "linux": os.environ.get("LINUX_CID"),
    "docker": os.environ.get("DOCKER_CID"),
    "kubernetes": os.environ.get("KUBERNETES_CID"),
    "git-github": os.environ.get("GIT-GITHUB_CID"),
    "vs-code": os.environ.get("VS-CODE_CID"),
    "vim-emacs": os.environ.get("VIM-EMACS_CID"),
    "db": os.environ.get("DB_CID"),
    "system-design": os.environ.get("SYSTEM-DESIGN_CID"),
    "auth": os.environ.get("AUTH_CID"),
    "api": os.environ.get("API_CID"),
    "tools": os.environ.get("TOOLS_CID"),
    "network": os.environ.get("NETWORK_CID"),
    "oops": os.environ.get("OOPS_CID"),
    "math": os.environ.get("MATH_CID"),
    "ml-ai": os.environ.get("ML-AI_CID"),
    "showcase": os.environ.get("SHOWCASE_CID"),
    "discussions": os.environ.get("DISCUSSIONS_CID"),
    "memes": os.environ.get("MEMES_CID"),
    "youtube": os.environ.get("YOUTUBE_CID"),
    "typing": os.environ.get("TYPING_CID"),
    "playground": os.environ.get("PLAYGROUND_CID"),
    "web-design": os.environ.get("WEB-DESIGN_CID"),
    "pop-talks-text": os.environ.get("POP-TALKS-TEXT_CID"),
    "solution-dump": os.environ.get("SOLUTION-DUMP_CID"),
    "academics": os.environ.get("ACADEMICS_CID"),
    "placement-general": os.environ.get("PLACEMENT-GENERAL_CID"),
    "resume": os.environ.get("RESUME_CID"),
    "dsa": os.environ.get("DSA_CID"),
}


class Base(DeclarativeBase):
    pass


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


app = Flask(__name__)


@app.route("/", methods=["GET"])
def home() -> str:
    with Session(engine) as session:
        return render_template(
            "home.html",
            links=session.scalars(
                select(LaterLink).where(LaterLink.is_deleted == False),  # noqa: E712
            ),
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
        link.is_deleted = True
        session.commit()

    return redirect(url_for("home"))


@app.route("/discord/<int:id>", methods=["GET"])
def discord(id: int) -> Response:
    with Session(engine) as session:
        link = session.get(LaterLink, id)

        if link.is_posted_to_discord:
            return redirect(url_for("home"))

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

        link.is_posted_to_discord = True
        session.commit()

    return redirect(url_for("home"))
