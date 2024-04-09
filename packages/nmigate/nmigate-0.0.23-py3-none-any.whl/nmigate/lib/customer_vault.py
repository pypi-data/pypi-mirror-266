from nmigate.util.wrappers import log, postProcessingOutput, postProcessXml
from nmigate.lib.nmi import Nmi
import requests
from typing import Union, Dict, Any
import uuid


class CustomerVault(Nmi):
    def __init__(self, token, org):
        super().__init__(token, org)

    @postProcessingOutput
    def create(self, vault_request) -> Dict[str, Union[Any, str]]:
        uid = (uuid.uuid4().hex,)

        data = {
            "customer_vault": "add_customer",
            # "type": "auth",
            "initiated_by": "customer",
            "stored_credential_indicator": "stored",
            "security_key": self.security_token,
            "customer_vault_id": vault_request["id"] if vault_request["id"] else uid,
            "payment_token": vault_request["token"],
            "billing_id": vault_request["billing_id"],
        }
        data.update(vault_request["billing_info"])
        response = requests.post(
            url="https://secure.nmi.com/api/transact.php", data=data
        )
        return {"response": response, "type": "create_customer_vault"}

    @postProcessingOutput
    def update(self, id: str, billing_info) -> Dict[str, Union[Any, str]]:
        data = {
            "customer_vault": "update_customer",
            "security_key": self.security_token,
            "customer_vault_id": id,
        }
        data.update(billing_info)
        response = requests.post(
            url="https://secure.nmi.com/api/transact.php", data=data
        )
        return {"response": response, "type": "update_customer_vault"}

    @postProcessingOutput
    def validate(self, user_id: str) -> Dict[str, Union[Any, str]]:
        url = "https://secure.networkmerchants.com/api/transact.php"
        query = {
            "security_key": self.security_token,
            "customer_vault_id": user_id,
            "amount": "0.00",
            "type": "validate",
        }
        response = requests.post(url=url, data=query)
        return {"response": response, "type": "create_customer_vault"}

    @postProcessXml
    def get_billing_info_by_transaction_id(self, transaction_id) -> Any:
        url = "https://secure.nmi.com/api/query.php"
        query = {
            "security_key": self.security_token,
            "transaction_id": transaction_id,
        }
        response = requests.post(url=url, data=query)
        return response

    @postProcessXml
    def get_customer_info(self, id) -> Any:
        url = "https://secure.nmi.com/api/query.php"
        query = {
            "report_type": "customer_vault",
            "security_key": self.security_token,
            "customer_vault_id": id,
        }
        response = requests.post(url=url, data=query)
        return response

    @postProcessingOutput
    def delete(self, id: str) -> Dict[str, Union[Any, str]]:
        data = {
            "customer_vault": "delete_customer",
            "security_key": self.security_token,
            "customer_vault_id": id,
        }
        response = requests.post(
            url="https://secure.nmi.com/api/transact.php", data=data
        )
        return {"response": response, "type": "delete_customer_vault"}
