from marshmallow import Schema, fields, validate, EXCLUDE

class CounterAddSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "name is required"}
    )
    service_type = fields.Str(
        required=True,
        validate=validate.OneOf(["Passport", "License", "Aadhaar"]),
        error_messages={"required": "service_type is required"}
    )
