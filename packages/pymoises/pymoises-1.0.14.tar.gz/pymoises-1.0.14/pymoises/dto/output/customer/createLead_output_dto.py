from marshmallow import Schema, fields, ValidationError

class create_customer_schema(Schema):
    id = fields.String(required=True, description="true if all correctly")
  
    class Meta:
        ordered = True

class create_customer_output_schema(Schema):
    success = fields.Boolean(required=True, description="true if all correctly")
    message = fields.String(required=True, description="lastname person to assigns transaction")
    payload = fields.Raw()
    
    class Meta:
        ordered = True

class create_customer_output:
    def create(body: create_customer_output_schema):
        try:
            return create_customer_output_schema().load(body)
        except ValidationError as err:
            raise Exception(err)