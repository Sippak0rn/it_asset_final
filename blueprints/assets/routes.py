import csv
from io import BytesIO, StringIO
from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, Response, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Asset, Category, Location
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from . import assets_bp
from .forms import AssetForm

def admin_required():
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("ต้องเป็น admin เท่านั้น", "danger")
        return False
    return True

@assets_bp.route("/")
@login_required
def list_assets():
    q = request.args.get("q", "").strip()
    query = Asset.query
    if q:
        like = "%" + q + "%"
        query = query.filter(db.or_(Asset.asset_tag.like(like), Asset.name.like(like)))
    assets = query.order_by(Asset.id.desc()).all()
    return render_template("assets_list.html", assets=assets, q=q)

@assets_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_asset():
    if not admin_required():
        return redirect(url_for("assets.list_assets"))

    form = AssetForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form.location_id.choices = [(l.id, l.label) for l in Location.query.order_by(Location.building, Location.room).all()]

    if form.validate_on_submit():
        if Asset.query.filter_by(asset_tag=form.asset_tag.data.strip()).first():
            flash("asset_tag นี้มีอยู่แล้ว", "danger")
            return render_template("asset_form.html", form=form, title="เพิ่มครุภัณฑ์")

        asset = Asset(
            asset_tag=form.asset_tag.data.strip(),
            name=form.name.data.strip(),
            category_id=form.category_id.data,
            location_id=form.location_id.data,
            status=form.status.data,
            created_by=current_user.id
        )
        db.session.add(asset)
        db.session.commit()
        flash("เพิ่มครุภัณฑ์สำเร็จ", "success")
        return redirect(url_for("assets.list_assets"))

    return render_template("asset_form.html", form=form, title="เพิ่มครุภัณฑ์")

@assets_bp.route("/<int:asset_id>/edit", methods=["GET", "POST"])
@login_required
def edit_asset(asset_id):
    if not admin_required():
        return redirect(url_for("assets.list_assets"))

    asset = Asset.query.get_or_404(asset_id)
    form = AssetForm(obj=asset)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    form.location_id.choices = [(l.id, l.label) for l in Location.query.order_by(Location.building, Location.room).all()]

    if form.validate_on_submit():
        new_tag = form.asset_tag.data.strip()
        if new_tag != asset.asset_tag and Asset.query.filter_by(asset_tag=new_tag).first():
            flash("asset_tag นี้มีอยู่แล้ว", "danger")
            return render_template("asset_form.html", form=form, title="แก้ไขครุภัณฑ์")

        asset.asset_tag = new_tag
        asset.name = form.name.data.strip()
        asset.category_id = form.category_id.data
        asset.location_id = form.location_id.data
        asset.status = form.status.data

        db.session.commit()
        flash("แก้ไขสำเร็จ", "success")
        return redirect(url_for("assets.list_assets"))

    return render_template("asset_form.html", form=form, title="แก้ไขครุภัณฑ์")

@assets_bp.route("/<int:asset_id>/delete", methods=["POST"])
@login_required
def delete_asset(asset_id):
    if not admin_required():
        return redirect(url_for("assets.list_assets"))

    asset = Asset.query.get_or_404(asset_id)
    db.session.delete(asset)
    db.session.commit()
    flash("ลบครุภัณฑ์แล้ว", "info")
    return redirect(url_for("assets.list_assets"))

@assets_bp.route("/export/csv")
@login_required
def export_csv():
    assets = Asset.query.order_by(Asset.id.asc()).all()

    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["id", "asset_tag", "name", "category", "location", "status"])
    for a in assets:
        writer.writerow([a.id, a.asset_tag, a.name, a.category.name, a.location.label, a.status])

    output = sio.getvalue().encode("utf-8-sig")
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=assets.csv"}
    )

@assets_bp.route("/export/pdf")
@login_required
def export_pdf():
    assets = Asset.query.order_by(Asset.id.asc()).all()

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica", 14)
    c.drawString(50, y, "IT Assets Report")
    y -= 20

    c.setFont("Helvetica", 10)
    c.drawString(50, y, "Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    y -= 25

    c.setFont("Helvetica", 9)
    c.drawString(50, y, "id")
    c.drawString(80, y, "asset_tag")
    c.drawString(160, y, "name")
    c.drawString(330, y, "category")
    c.drawString(420, y, "status")
    y -= 15

    for a in assets:
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)

        c.drawString(50, y, str(a.id))
        c.drawString(80, y, a.asset_tag[:12])
        c.drawString(160, y, a.name[:28])
        c.drawString(330, y, a.category.name[:15])
        c.drawString(420, y, a.status)
        y -= 13

    c.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="assets.pdf",
        mimetype="application/pdf"
    )
