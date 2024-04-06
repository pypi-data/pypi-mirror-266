from marshmallow import Schema, fields, ValidationError

class customer_schema(Schema):
    tpid = fields.String(required=True, description="true if all correctly")
    crmId = fields.String(required=True, description="true if all correctly")
    firstName = fields.String(required=True, description="true if all correctly")
    lastName = fields.String(required=True, description="true if all correctly")
    phoneCode = fields.String(required=True, description="true if all correctly")
    phoneNumber = fields.String(required=True, description="true if all correctly")
    country = fields.String(required=True, description="true if all correctly")
    BussinessUnit = fields.String(required=True, description="true if all correctly")
    class Meta:
        ordered = True

class get_customer_output_schema(Schema):
    success = fields.Boolean(required=True, description="true if all correctly")
    message = fields.String(required=True, description="lastname person to assigns transaction")
    payload = fields.Nested(customer_schema, required=False)
    
    class Meta:
        ordered = True

class get_customer_output:
    def create(body: get_customer_output_schema):
        try:
            return get_customer_output_schema().load(body)
        except ValidationError as err:
            raise Exception(err)