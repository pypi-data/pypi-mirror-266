from marshmallow import ValidationError

from ticketsdk.constants import LAMBDA_URI, LAMBDA_ENDPOINT_FOR_TICKET, LAMBDA_AUTHEN
from ticketsdk.client import ServiceHttpClient
from ticketsdk.validators import (
    NewTicketSchema,
    NewSellerSchema,
    ListTicketSchema,
    DetailTicketSchema,
    DetailCommentTicketSchema,
    CreateCommentTicketSchema,
)

headers = {
    "Authorization": LAMBDA_AUTHEN,
    "Content-Type": "application/json",
}


class Connection:
    def __init__(self, **kwargs):
        self.body = kwargs.get("body")

    def add_new_seller(self):
        try:
            NewSellerSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(base_url=LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")

    def add_new_ticket(self):
        try:
            NewTicketSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")

    def list_ticket(self):
        try:
            ListTicketSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")

    def detail_ticket(self):
        try:
            DetailTicketSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")

    def list_comment_ticket(self):
        try:
            DetailCommentTicketSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")

    def create_comment_ticket(self):
        try:
            CreateCommentTicketSchema().load(self.body)
        except ValidationError as err:
            raise ValueError(err.messages)
        response = ServiceHttpClient(LAMBDA_URI).execute(
            method="post",
            uri=LAMBDA_ENDPOINT_FOR_TICKET,
            body=self.body,
            headers=headers,
        )
        return response.get("response").get("result")
