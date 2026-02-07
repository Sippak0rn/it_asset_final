from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from extensions import db
from models import Checkout, Asset , User
from datetime import date

checkouts_bp = Blueprint("checkouts", __name__)

def admin_only():
    if current_user.role != "admin":
        abort(403)

@checkouts_bp.route("/")
@login_required
def index():
    checkouts = Checkout.query.order_by(Checkout.id.desc()).all()
    return render_template("checkouts_list.html", checkouts=checkouts)

@checkouts_bp.route("/history")
@login_required
def history():
    history = (
        db.session.query(Checkout)
        .join(Asset)
        .join(User, Checkout.borrower_id == User.id)
        .filter(Checkout.status.in_(["returned", "rejected", "approved"]))
        .order_by(Checkout.id.desc())
        .all()
    )

    return render_template(
        "history.html",
        history=history
    )

@checkouts_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    assets = Asset.query.all()

    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        if not asset_id:
            return redirect(url_for("checkouts.new"))

        # ✅ FIX ตัวจริงอยู่ตรงนี้
        checkout = Checkout(
            asset_id=asset_id,
            borrower_id=current_user.id,   # <<< ห้าม NULL
            checkout_date=date.today(),
            status="requested"
        )

        db.session.add(checkout)
        db.session.commit()

        return redirect(url_for("checkouts.index"))

    return render_template(
        "checkout_form.html",
          assets=assets,
          checkout=None
          )

@checkouts_bp.route("/<int:id>/approve", methods=["POST"])
@login_required
def approve(id):
    admin_only()
    checkout = Checkout.query.get_or_404(id)
    checkout.status = "approved"
    checkout.approved_by = current_user.id
    checkout.approved_at = date.today()
    db.session.commit()
    return redirect(url_for("checkouts.index"))

@checkouts_bp.route("/<int:id>/reject", methods=["POST"])
@login_required
def reject(id):
    admin_only()
    checkout = Checkout.query.get_or_404(id)
    checkout.status = "rejected"
    db.session.commit()
    return redirect(url_for("checkouts.index"))

@checkouts_bp.route("/<int:id>/return", methods=["POST"])
@login_required
def return_asset(id):
    admin_only()
    checkout = Checkout.query.get_or_404(id)
    checkout.status = "returned"
    checkout.return_date = date.today()
    db.session.commit()
    return redirect(url_for("checkouts.index"))
