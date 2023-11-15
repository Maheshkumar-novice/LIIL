from dotenv import load_dotenv
from flask import Flask, render_template
from turbo_flask import Turbo

load_dotenv()

turbo = Turbo()


def create_app() -> Flask:
    from constants import CHANNEL_IDS
    from modules.birthdays import birthdays_blueprint
    from modules.liil import liil_blueprint

    app = Flask(__name__)
    turbo.init_app(app)

    app.context_processor(lambda: {"tags": CHANNEL_IDS.keys()})

    @app.route("/", methods=["GET"])
    def home() -> str:
        return render_template("home.html")

    app.register_blueprint(liil_blueprint, url_prefix="/liil")
    app.register_blueprint(birthdays_blueprint, url_prefix="/birthdays")

    return app
