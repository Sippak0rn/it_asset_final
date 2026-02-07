from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager

ASSET_STATUSES = ("new", "in_use", "repair", "retired")
CHECKOUT_STATUSES = ("requested", "approved", "returned", "rejected")
TICKET_STATUSES = ("open", "in_progress", "resolved", "closed")

# ===== Human-friendly labels (TH) =====
ASSET_STATUS_LABELS = {
    "new": "พร้อมใช้งาน",
    "in_use": "กำลังใช้งาน",
    "repair": "ส่งซ่อม",
    "retired": "ปลดระวาง",
}

CHECKOUT_STATUS_LABELS = {
    "requested": "รออนุมัติ",
    "approved": "อนุมัติแล้ว",
    "returned": "คืนแล้ว",
    "rejected": "ปฏิเสธ",
}

TICKET_STATUS_LABELS = {
    "open": "เปิดเรื่อง",
    "in_progress": "กำลังดำเนินการ",
    "resolved": "แก้ไขแล้ว",
    "closed": "ปิดงาน",
}

# ===== Badge style class mapping =====
STATUS_BADGE_CLASS = {
    # assets
    "new": "pill-success",
    "in_use": "pill-info",
    "repair": "pill-warning",
    "retired": "pill-danger",

    # checkouts
    "requested": "pill-warning",
    "approved": "pill-info",
    "returned": "pill-success",
    "rejected": "pill-danger",

    # tickets
    "open": "pill-warning",
    "in_progress": "pill-info",
    "resolved": "pill-success",
    "closed": "pill-muted",
}


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="staff")  # admin/staff
    is_active = db.Column(db.Boolean, default=True)

    assets_created = db.relationship("Asset", backref="creator", lazy=True, foreign_keys="Asset.created_by")
    checkouts = db.relationship("Checkout", backref="borrower", lazy=True, foreign_keys="Checkout.borrower_id")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    assets = db.relationship("Asset", backref="category", lazy=True)


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    building = db.Column(db.String(120), nullable=False)
    room = db.Column(db.String(120), nullable=False)

    assets = db.relationship("Asset", backref="location", lazy=True)

    @property
    def label(self):
        return self.building + " / " + self.room


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    asset_tag = db.Column(db.String(50), unique=True, index=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)

    status = db.Column(db.String(20), nullable=False, default="new")  # new/in_use/repair/retired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    checkouts = db.relationship("Checkout", backref="asset", lazy=True)

    @property
    def status_th(self):
        return ASSET_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_badge(self):
        return STATUS_BADGE_CLASS.get(self.status, "pill-muted")


class Checkout(db.Model):
    __tablename__ = "checkouts"

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    checkout_date = db.Column(db.Date, default=date.today)
    due_date = db.Column(db.Date, nullable=True)
    return_date = db.Column(db.Date, nullable=True)

    status = db.Column(db.String(20), nullable=False, default="requested")  # requested/approved/returned/rejected
    approved_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)

    approver = db.relationship("User", foreign_keys=[approved_by], lazy=True)

    @property
    def status_th(self):
        return CHECKOUT_STATUS_LABELS.get(self.status, self.status)

    @property
    def status_badge(self):
        return STATUS_BADGE_CLASS.get(self.status, "pill-muted")


from datetime import datetime
from extensions import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)

    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    problem = db.Column(db.Text, nullable=False)

    status = db.Column(
        db.String(20),
        nullable=False,
        default='open'
    )

    asset = db.relationship('Asset')   # ✅ ฝั่งเดียวพอ
    user = db.relationship('User')


class TicketLog(db.Model):
    __tablename__ = "ticket_logs"

    id = db.Column(db.Integer, primary_key=True)

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("tickets.id"),
        nullable=False
    )

    changed_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)

    note = db.Column(db.String(255), nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("Ticket", lazy=True)
    changer = db.relationship("User", lazy=True)

    def __repr__(self):
        return f"<TicketLog ticket={self.ticket_id} {self.old_status}->{self.new_status}>"
