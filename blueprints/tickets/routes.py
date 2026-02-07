from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from extensions import db

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.route("/", methods=["GET"])
@login_required
def list_tickets():
    sql = """
        SELECT
            t.id,
            a.name AS asset_name,
            t.issue,
            t.status
        FROM tickets t
        LEFT JOIN assets a ON a.id = t.asset_id
        ORDER BY t.id DESC
    """
    tickets = db.session.execute(db.text(sql)).fetchall()

    return render_template(
        "tickets_list.html",
        tickets=tickets
    )


@tickets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_ticket():
    if request.method == "POST":
        asset_id = request.form.get("asset_id")
        issue = request.form.get("issue")

        sql = """
            INSERT INTO tickets (asset_id, requester_id, issue, status)
            VALUES (:asset_id, :requester_id, :issue, 'open')
        """
        db.session.execute(
            db.text(sql),
            {
                "asset_id": asset_id,
                "requester_id": current_user.id,
                "issue": issue
            }
        )
        db.session.commit()

        return redirect(url_for("tickets.list_tickets"))

    assets = db.session.execute(
        db.text("SELECT id, name FROM assets ORDER BY name")
    ).fetchall()

    return render_template(
        "ticket_form.html",
        assets=assets
    )
