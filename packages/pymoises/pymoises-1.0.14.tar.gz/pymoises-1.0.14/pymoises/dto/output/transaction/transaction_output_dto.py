from marshmallow import Schema, fields, ValidationError

class transaction_output_schema(Schema):
    success = fields.Boolean(required=True, description="true if all correctly")
    message = fields.String(required=True, description="lastname person to assigns transaction")
    
    class Meta:
        ordered = True

class transaction_output:
    def create(body: transaction_output_schema):
        try:
            return transaction_output_schema().load(body)
        except ValidationError as err:
            raise Exception(err)