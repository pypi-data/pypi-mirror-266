from marshmallow import Schema, fields, ValidationError

class check_email_phone_input_schema(Schema):
    email = fields.Email(required=True, description="Email lead")
    phone = fields.String(required=True, description = "Phone email")
    
    class Meta:
        ordered = True

class check_email_phone_input:
    def create(body: check_email_phone_input_schema):
        try:
            return check_email_phone_input_schema().load(body)
        except ValidationError as err:
            raise Exception(err)