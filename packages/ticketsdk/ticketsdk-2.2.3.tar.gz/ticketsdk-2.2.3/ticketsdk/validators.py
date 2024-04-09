from marshmallow import RAISE, Schema, ValidationError, fields

list_issue_code = ["INBOUND", "OUTBOUND", "RETURN_GOODS", "INVENTORY_CHECKING"]

list_from_system = ["WMS", "OMS"]


def validate_issue_code(val):
    if val not in list_issue_code:
        raise ValidationError(f"issue_code in : {list_issue_code}")


def validate_from_system(val):
    if val not in list_from_system:
        raise ValidationError(f"from_system in : {list_from_system}")


def validate_type_list(val):
    if val not in ["list"]:
        raise ValidationError(f"lambda_type not exists")


def validate_type_detail(val):
    if val not in ["detail"]:
        raise ValidationError(f"lambda_type not exists")


class NewTicketSchema(Schema):
    issue_code = fields.Str(required=True, validate=validate_issue_code)
    from_system = fields.Str(required=True, validate=validate_from_system)
    ref_code = fields.Str(required=True)
    partner_code = fields.Str(required=True)
    ticket_name = fields.Str(required=True)
    requested_email = fields.Str(required=True)
    ticket_description = fields.Str(required=True)
    attachments = fields.List(fields.Str(), allow_none=False, allow_empty=True)
    lambda_type = fields.Str(required=True)

    class Meta:
        strict = True
        unknown = RAISE


class NewSellerSchema(Schema):
    partner_code = fields.Str(required=True)
    email = fields.Str(required=True)
    cs_email = fields.Str(required=True)
    lambda_type = fields.Str(required=True)

    class Meta:
        strict = True
        unknown = RAISE


class ListTicketSchema(Schema):
    lambda_type = fields.Str(required=True, validate=validate_type_list)
    page = fields.Int(required=True)
    code = fields.Str(required=False)
    created_at_from = fields.Float(required=False)
    created_at_to = fields.Float(required=False)
    page = fields.Int(required=False)
    status = fields.Str(required=False)
    partner_code = fields.Str(required=False)

    class Meta:
        strict = True
        unknown = RAISE


class DetailTicketSchema(Schema):
    lambda_type = fields.Str(required=True, validate=validate_type_detail)
    ticket_id = fields.Int(required=True)

    class Meta:
        strict = True
        unknown = RAISE
