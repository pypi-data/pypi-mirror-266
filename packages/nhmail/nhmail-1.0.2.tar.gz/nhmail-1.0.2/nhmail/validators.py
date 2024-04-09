from marshmallow import Schema, fields, validate


class SendEmailSchema(Schema):
    _email_validator = validate.Email()
    _url_validator = validate.URL()
    _name_validator = validate.Length(min=1)
    to = fields.Str(required=True, validate=_email_validator)
    template_id = fields.Str(required=True)
    template_data = fields.Nested(
        {
            "redirect_link": fields.Str(required=True, validate=_url_validator),
            "user_name": fields.Str(required=True, validate=_name_validator),
        },
        required=True,
    )
