from marshmallow import Schema, fields, validate, EXCLUDE

class RegisterSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={"required": "username is required"}
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=255),
        error_messages={"required": "password is required"}
    )
    role = fields.Str(
        validate=validate.OneOf(["customer", "operator", "admin"]),
        load_default="customer"
    )

class LoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(
        required=True,
        error_messages={"required": "username is required"}
    )
    password = fields.Str(
        required=True,
        error_messages={"required": "password is required"}
    )
