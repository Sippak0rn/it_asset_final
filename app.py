from flask import Flask
from extensions import db, login_manager
from models import User
from config import Config   # ✅ เพิ่มบรรทัดนี้


def create_app():
    app = Flask(__name__)

    # ======================
    # CONFIG
    # ======================
    app.config.from_object(Config)   # ✅ ใช้ Config แทนการ hardcode

    # ======================
    # INIT EXTENSIONS
    # ======================
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    # ======================
    # USER LOADER
    # ======================
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ======================
    # IMPORT BLUEPRINTS
    # ======================
    from blueprints.auth import auth_bp
    from blueprints.dashboard.routes import dashboard_bp
    from blueprints.assets import assets_bp
    from blueprints.checkouts.routes import checkouts_bp
    from blueprints.tickets.routes import tickets_bp

    # ======================
    # REGISTER BLUEPRINTS
    # ======================
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)          # หน้า /
    app.register_blueprint(assets_bp, url_prefix="/assets")
    app.register_blueprint(checkouts_bp, url_prefix="/checkouts")
    app.register_blueprint(tickets_bp, url_prefix="/tickets")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

with app.app_context():
    db.create_all()
