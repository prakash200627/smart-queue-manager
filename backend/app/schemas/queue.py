from marshmallow import Schema, fields, validate, EXCLUDE

class QueueNewSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    service_type = fields.Str(
        required=True,
        validate=validate.OneOf(["Passport", "License", "Aadhaar"]),
        error_messages={"required": "service_type is required"}
    )

class AiDetectSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    message = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "message is required"}
    )
