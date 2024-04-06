from marshmallow import Schema, fields, ValidationError

class move_lead_schema(Schema):
    tpid = fields.String(required=True, description="true if all correctly")
    crmId = fields.String(required=True, description="true if all correctly")
    idBusinessUnit = fields.String(required=True, description="true if all correctly")

    class Meta:
        ordered = True

class move_lead_output_schema(Schema):
    success = fields.Boolean(required=True, description="true if all correctly")
    message = fields.String(required=True, description="lastname person to assigns transaction")
    payload = fields.Nested(move_lead_schema, required=False)
    
    class Meta:
        ordered = True

class move_lead_output:
    def create(body: move_lead_output_schema):
        try:
            return move_lead_output_schema().load(body)
        except ValidationError as err:
            raise Exception(err)