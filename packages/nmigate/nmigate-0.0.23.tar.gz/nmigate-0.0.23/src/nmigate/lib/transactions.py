from nmigate.util.wrappers import log, postProcessingOutput
from nmigate.lib.nmi import Nmi
import requests
from typing import Dict, Union, Any


class Transactions(Nmi):
    def __init__(self, token, org):
        super().__init__(token, org)

    @log
    @postProcessingOutput
    def pay_with_token(self, payment_request) -> Dict[str, Union[Any, str]]:
        data = {
            "type": "sale",
            "security_key": self.security_token,
            "payment_token": payment_request["token"],
            "amount": payment_request["total"],
        }
        data.update(payment_request["billing_info"])
        response = requests.post(
            "https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": payment_request,
            "type": "pay_with_token",
            "org": self.org,
        }

    @log
    @postProcessingOutput
    def pay_with_customer_vault(self, payment_request) -> Dict[str, Union[Any, str]]:
        data = {
            "security_key": self.security_token,
            "customer_vault_id": payment_request["user_id"],
            "amount": payment_request["total"],
            "initiated_by": "merchant",
            "stored_credential_indicator": "used",
            # "initial_transaction_id": payment_request["transaction_id"]
        }
        response = requests.post(
            "https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": payment_request,
            "type": "pay_with_customer_vault",
            "org": self.org,
        }

    @log
    @postProcessingOutput
    def refund(self, transaction_id) -> Dict[str, Union[Any, str]]:

        data = {
            "type": "refund",
            "payment": "creditcard",
            "amount": 0,
            "security_key": self.security_token,
            "transactionid": transaction_id,
        }

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": {"transaction_id": transaction_id},
            "type": "refund",
            "org": self.org,
        }
