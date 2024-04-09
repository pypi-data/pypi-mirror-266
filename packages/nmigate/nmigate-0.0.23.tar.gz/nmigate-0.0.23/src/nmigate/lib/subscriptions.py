from nmigate.util.wrappers import postProcessXml, postProcessingOutput
import requests
from nmigate.lib.nmi import Nmi
from nmigate.lib.plans import Plans
from typing import Dict, Union, Any


class Subscriptions(Nmi):
    def __init__(self, token, org):
        super().__init__(token, org)
        self.plans = Plans(token, org)

    @postProcessingOutput
    def custom_sale_using_vault(
        self, plan_id, customer_vault_id, transaction_id, create_customer_vault=False
    ) -> Dict[str, Union[Any, str]]:

        plan = self.plans.get_plan(plan_id)

        plan_amount = plan["plan_amount"] if plan else None

        data = {
            "type": "sale",
            "recurring": "add_subscription",
            "initiated_by": "merchant",
            "stored_credential_indicator": "used",
            # "initial_transaction_id": transaction_id,
            "security_key": self.security_token,
            "amount": str(plan_amount),
            "customer_vault_id": customer_vault_id,
            "plan_id": plan_id,
        }
        data["customer_vault"] = "add_customer" if create_customer_vault else None

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": {
                "customer_vault_id": customer_vault_id,
                "plan_id": plan_id,
                "total": plan_amount,
            },
            "type": "set_subscription_with_sale_and_vault",
            "org": self.org,
        }

    """  if amount = 0 then its a simple subscription, if amount = 1 then its a subscription with sale """

    @postProcessingOutput
    def custom_sale_using_vault_month_frequency(
        self, request_sub
    ) -> Dict[str, Union[Any, str]]:

        data = {
            "type": "sale",
            "recurring": "add_subscription",
            "billing_method": "recurring",
            "initiated_by": "merchant",
            "stored_credential_indicator": "used",
            # "initial_transaction_id": request_sub["transaction_id"],
            "security_key": self.security_token,
            "customer_vault_id": request_sub["user_id"],
            "amount": request_sub["total_amount"],
            "plan_payments": request_sub["custom_subscription_info"]["plan_payments"],
            "plan_amount": request_sub["custom_subscription_info"]["plan_amount"],
            "month_frequency": request_sub["custom_subscription_info"][
                "month_frequency"
            ],
            "day_of_month": request_sub["custom_subscription_info"]["day_of_month"],
            "start_date": request_sub["custom_subscription_info"]["start_date"],
        }

        if float(request_sub["total_amount"]) == 0:
            del data["type"]
            del data["amount"]

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": request_sub,
            "type": "set_custom_subscription_with_sale_and_vault_month_config",
            "org": self.org,
        }

    @postProcessingOutput
    def custom_with_sale_and_vault_day_frequency(
        self, request_sub
    ) -> Dict[str, Union[Any, str]]:

        data = {
            "type": "sale",
            "recurring": "add_subscription",
            "billing_method": "recurring",
            "initiated_by": "merchant",
            "stored_credential_indicator": "used",
            # "initial_transaction_id": request_sub["transaction_id"],
            "security_key": self.security_token,
            "amount": request_sub["total_amount"],
            "customer_vault_id": request_sub["user_id"],
            "plan_payments": request_sub["custom_subscription_info"]["plan_payments"],
            "plan_amount": request_sub["custom_subscription_info"]["plan_amount"],
            "day_frequency": request_sub["custom_subscription_info"]["day_frequency"],
            "start_date": request_sub["custom_subscription_info"]["start_date"],
        }

        if float(request_sub["total_amount"]) == 0:
            del data["type"]
            del data["amount"]

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        return {
            "response": response,
            "req": request_sub,
            "type": "set_custom_subscription_with_sale_and_vault_day_frequency",
            "org": self.org,
        }

    @postProcessXml
    def get_info(self, id) -> Any:
        url = "https://secure.nmi.com/api/query.php"
        query = {
            "report_type": "recurring",
            "security_key": self.security_token,
            "subscription_id": id,
        }
        response = requests.post(url=url, data=query)
        return response

    @postProcessingOutput
    def delete(self, subscription_id):
        data = {
            "recurring": "delete_subscription",
            "security_key": self.security_token,
            "subscription_id": subscription_id,
        }
        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        del data["security_key"]
        return {
            "response": response,
            "req": data,
            "type": "delete_subscription",
            "org": self.org,
        }

    @postProcessingOutput
    def pause_subscription(self, subscription_id, pause):
        data = {
            "recurring": "update_subscription",
            "security_key": self.security_token,
            "subscription_id": subscription_id,
            "paused_subscription": str(pause).lower(),
        }
        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        del data["security_key"]
        return {
            "response": response,
            "req": data,
            "type": "pause_subscription",
            "org": self.org,
        }

    @postProcessingOutput
    def update_month_subscription(
        self,
        subscription_id: str,
        customer_vault_id: str,
        billing_id: str,
        billing_info,
        plan_payments: str,
        plan_amount: str,
        day_of_month: str,
        month_frequency: str,
        start_date: str,
    ):
        data = {
            "recurring": "update_subscription",
            "security_key": self.security_token,
            "subscription_id": subscription_id,
            "customer_vault_id": customer_vault_id,
            "billing_id": billing_id,
            "plan_payments": plan_payments,
            "plan_amount": plan_amount,
            "day_of_month": day_of_month,
            "month_frequency": month_frequency,
            "start_date": start_date,  # YYYYMMDD
        }
        data.update(billing_info)

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        del data["security_key"]
        return {
            "response": response,
            "req": data,
            "type": "update_month_subscription",
            "org": self.org,
        }

    @postProcessingOutput
    def update_day_subscription(
        self,
        subscription_id: str,
        customer_vault_id: str,
        billing_id: str,
        billing_info,
        plan_payments: str,
        plan_amount: str,
        day_frequency: str,
        start_date: str,
    ):
        data = {
            "recurring": "update_subscription",
            "security_key": self.security_token,
            "subscription_id": subscription_id,
            "customer_vault_id": customer_vault_id,
            "billing_id": billing_id,
            "plan_payments": plan_payments,
            "plan_amount": plan_amount,
            "day_frequency": day_frequency,
            "start_date": start_date,  # YYYYMMDD
        }
        data.update(billing_info)

        response = requests.post(
            url="https://secure.networkmerchants.com/api/transact.php", data=data
        )
        del data["security_key"]
        return {
            "response": response,
            "req": data,
            "type": "update_day_subscription",
            "org": self.org,
        }
