from marshmallow import Schema, fields, ValidationError, validate
from marshmallow.validate import Length, Regexp

bussinesUnitName = [
    'Profitbitz', 
    'FxIntegral', 
    'AscendingBull', 
    'Inverlion', 
    'Noimarkets', 
    'Solutraders', 
    'BearInvester', 
    'Fxtrategy', 
    'AllMarkets', 
    'UbmCapital'
]

countries = ["MX", "PE", "CL", "BR", "CR", "PA"]

class create_lead_input_schema(Schema):
    firstName = fields.String(required=True, description = "Phone email")
    lastName = fields.String(required=True, description = "Phone email")
    email = fields.Email(required=True, description="Email lead")
    password = fields.String(validate=[Regexp(regex=('^(?=\w*\d)(?=\w*[A-Z])(?=\w*[a-z])\S{8,15}$'))])      
    phoneCode = fields.Integer(required=True, description = "Phone email")
    phoneNumber = fields.String(required=True, description = "Phone email")
    country = fields.String(
        required=True, 
        validate=validate.OneOf(countries), 
        description = "Phone email")        
    page = fields.String(required=True, description = "Phone email")
    bussinesUnitName = fields.String(
        required=True, 
        validate=validate.OneOf(bussinesUnitName), 
        description="Bussines Unit name", 
    )    
    class Meta:
        ordered = True

class create_lead_input:
    def create(body: create_lead_input_schema):
        try:
            return create_lead_input_schema().load(body)
        except ValidationError as err:
            raise Exception(err)