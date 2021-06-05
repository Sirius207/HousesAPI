from api.db import db


class House(db.Document):
    house_id = db.StringField(required=True, primary_key=True)
    title = db.StringField(max_length=20, required=True)
    city = db.StringField(max_length=6, required=True)
    district = db.StringField(max_length=6, required=True)
    lessor = db.StringField(max_length=10, required=True)
    lessor_identity = db.StringField(max_length=10, required=True)
    house_type = db.StringField(max_length=10, required=False)
    house_status = db.StringField(max_length=20, required=True)
    sold = db.StringField(max_length=15, required=False)
    phone = db.StringField(max_length=20, required=False)
    gender_requirement = db.StringField(max_length=15, required=False)
    house_condition = db.StringField(required=True)
