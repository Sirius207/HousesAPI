from db import db


class House(db.Document):
    url = db.StringField(required=True)
    title = db.StringField(max_length=20, required=True)
    lessor = db.StringField(max_length=10, required=True)
    lessor_identity = db.StringField(max_length=10, required=True)
    house_type = db.StringField(max_length=10, required=True)
    house_status = db.StringField(max_length=20, required=True)
    sold = db.StringField(max_length=15, required=True)
    phone = db.StringField(max_length=20, required=True)
    gender_requirement = db.StringField(max_length=15, required=True)
    house_condition = db.StringField(required=True)
