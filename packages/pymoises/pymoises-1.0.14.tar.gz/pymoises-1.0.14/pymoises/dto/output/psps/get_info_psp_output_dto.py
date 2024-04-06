from marshmallow import Schema, fields, ValidationError

class get_info_psp_settings(Schema):
    available = fields.Boolean(required=True, description="true if all correctly")
    maxAmount = fields.Integer(required=True, description="true if all correctly")
    minAmount = fields.Integer(required=True, description="true if all correctly")
    selectedCountries = fields.List(required=True, description="true if all correctly")
    availableCountries = fields.List(required=True, description="true if all correctly")
    availableBusinessUnits = fields.List(required=True, description="true if all correctly")
    notAvailableBusinessUnit = fields.List(required=True, description="true if all correctly")

    class Meta:
        ordered = True

class get_info_psp_schema(Schema):
    idCrmPspCat = fields.Integer(required=True, description="true if all correctly")
    name = fields.String(required=True, description="true if all correctly")
    settings = fields.Nested(get_info_psp_settings, required=False)

    class Meta:
        ordered = True

class get_info_psps(Schema):
    success = fields.Boolean(required=True, description="true if all correctly")
    message = fields.String(required=True, description="lastname person to assigns transaction")
    payload = fields.Nested(get_info_psp_schema, required=False)
    
    class Meta:
        ordered = True

class get_info_psps_output:
    def create(body: get_info_psps):
        try:
            return get_info_psps().load(body)
        except ValidationError as err:
            raise Exception(err)