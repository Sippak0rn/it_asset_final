from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

ASSET_STATUSES = [("new", "new"), ("in_use", "in_use"), ("repair", "repair"), ("retired", "retired")]

class AssetForm(FlaskForm):
    asset_tag = StringField("รหัสครุภัณฑ์ (asset_tag)", validators=[DataRequired(), Length(max=50)])
    name = StringField("ชื่อครุภัณฑ์", validators=[DataRequired(), Length(max=200)])
    category_id = SelectField("หมวดหมู่", coerce=int, validators=[DataRequired()])
    location_id = SelectField("สถานที่จัดเก็บ", coerce=int, validators=[DataRequired()])
    status = SelectField("สถานะ", choices=ASSET_STATUSES, validators=[DataRequired()])
    submit = SubmitField("บันทึก")
