from datetime import datetime
import string
import random
from flask_mongoengine import MongoEngine
from marshmallow import Schema, fields, validate, ValidationError

db = MongoEngine()


class User(db.Document):
    firstName = db.StringField(Required=True)
    lastName = db.StringField(Required=True)
    email = db.EmailField()
    gender = db.StringField()
    password = db.StringField(Required=True)
    countryCode = db.StringField(Required=True, min=1, max=5)
    phone = db.StringField(Required=True, min=10, max=10)
    address = db.StringField()
    otp = db.StringField()
    verified = db.BooleanField(default=False)
    createdAt = db.DateTimeField(default=datetime.now())
    updatedAt = db.DateTimeField(default=datetime.now())

    def create(self):
        self.save()

    def generate_otp(self):
        otp = "".join(random.choices(string.digits, k=6))

        exist_otp = User.objects(otp=otp).first()

        if exist_otp:
            self.generate_otp()
        else:
            return otp

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.otp = str(self.generate_otp())

    def format_name(self):
        return f"{self.lastName} {self.firstName}"

    def user_profile(self, token=None, referesh_token=None):
        return {
            "id": str(self.pk),
            "firstName": self.firstName,
            "lastName": self.lastName,
            "email": self.email,
            "phone": self.phone,
            "address": self.address if self.address != None else "",
            "verified": self.verified,
            "createdAt": (str(self.createdAt)),
            "accessToken": token if token != None else "",
            "refreshToken": referesh_token if referesh_token != None else "",
            "tokenType": "bearer"
        }

    def is_verified(self):
        return self.verified


class UserSchema(Schema):
    firstName = fields.String(required=True)
    lastName = fields.String(required=True)
    email = fields.Email(required=False)
    password = fields.Str(
        required=True, validate=[validate.Length(min=6, max=36)], load_only=True
    )
    countryCode = fields.Str(
        required=True, validate=[validate.Length(min=1, max=5)], load_only=True
    )
    phone = fields.Str(
        required=True, validate=[validate.Length(min=10, max=10)], load_only=True
    )
    gender = fields.Str(validate=validate.OneOf(["male", "female", "lgbtq+"]))
    address = fields.String(required=False)

    def format_name(self, user):
        return f"{user.lastName}, {user.firstName}"

    # Custom validator
    def must_not_be_blank(data):
        if not data['firstName']:
            raise ValidationError("Please provide first name.")

        if not data['phone']:
            raise ValidationError("Please provide phone number.")


class LoginSchema(Schema):
    countryCode = fields.Str(
        required=True, validate=[validate.Length(min=1, max=5)], load_only=True
    )
    phone = fields.Str(
        required=True, validate=[validate.Length(min=10, max=10)], load_only=True
    )
    password = fields.Str(
        required=True, validate=[validate.Length(min=6, max=36)], load_only=True
    )


class VerifyOtpSchema(Schema):
    countryCode = fields.Str(
        required=True, validate=[validate.Length(min=1, max=5)], load_only=True
    )
    phone = fields.Str(
        required=True, validate=[validate.Length(min=10, max=10)], load_only=True
    )
    otp = fields.Str(
        required=True, validate=[validate.Length(min=6, max=6)], load_only=True
    )


class Bookmark(db.Document):
    name = db.StringField(Required=True)
    url = db.URLField(Required=True)
    user = db.ReferenceField(User, required=True)
    short_url = db.StringField(Required=True, min=3, max=3)
    createdAt = db.DateTimeField(default=datetime.now())
    updatedAt = db.DateTimeField(default=datetime.now())

    def generate_short_characters(self):
        picked_chars = ''.join(random.choices(
            string.digits+string.ascii_letters, k=3))

        link = Bookmark.objects(short_url=picked_chars).first()

        if link:
            self.generate_short_characters()
        else:
            return picked_chars

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.short_url = self.generate_short_characters()

    def __repr__(self) -> str:
        return 'Boomark>>> {self.url}'

    def object(self):
        return {
            "id": str(self.pk),
            "name": self.name,
            "url": self.url,
            "shortUrl": self.short_url,
            "createdAt": (str(self.createdAt)),
            "updatedAt": (str(self.updatedAt)),
        }


class BookmarkSchema(Schema):
    name = fields.String(required=True, error_messages={
        "required": "Name field is required."})
    url = fields.URL(required=True, error_messages={
        "invalid": "Please provide valid url."})
    # user = fields.Nested(UserSchema(only=("id",)))
    # fields.Nested(UserSchema(only=("pk")), required=True)
    # fields.Nested(UserSchema(only=("email",)))
