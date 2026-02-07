from flask import Blueprint, render_template
from flask_login import login_required
from extensions import db
from models import Asset, Checkout

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def index():
    # =====================
    # ครุภัณฑ์ทั้งหมด
    # =====================
    total_assets = Asset.query.count()

    # =====================
    # กำลังใช้งาน
    # =====================
    in_use_assets = Checkout.query.filter_by(status="borrowed").count()

    # =====================
    # แจ้งซ่อม (ใช้ SQL ตรง ไม่แตะ user_id)
    # =====================
    open_tickets = db.session.execute(
        db.text("""
            SELECT COUNT(*) 
            FROM tickets 
            WHERE status = 'open'
        """)
    ).scalar()

    # =====================
    # รายการยืมล่าสุด
    # =====================
    recent_checkouts = (
        Checkout.query
        .order_by(Checkout.id.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_assets=total_assets,
        in_use_assets=in_use_assets,
        open_tickets=open_tickets,
        recent_checkouts=recent_checkouts
    )
