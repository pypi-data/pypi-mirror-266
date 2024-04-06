from marshmallow import Schema, fields, ValidationError

class create_transaction_input_schema(Schema):
    idPsp = fields.String(required=True)
    crmId = fields.String(required=True)
    amount = fields.Integer(required=True)
    
    class Meta:
        ordered = True

class create_transaction_input:
    def create(body: create_transaction_input_schema):
        try:
            return create_transaction_input_schema().load(body)
        except ValidationError as err:
            raise Exception(err)