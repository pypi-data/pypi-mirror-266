
from nmigate.lib.nmi import Nmi
from nmigate.util.wrappers import log, postProcessingOutput, postProcessXml
import requests
from typing import Dict, Union, Any

class Plans(Nmi):
    def __init__(self, token, org):
        super().__init__(token, org)

    @log
    @postProcessingOutput
    def add_plan_by_month_config(self, data)-> Dict[str, Union[Any, str]]: 
        data = {
            'recurring': 'add_plan',
            "security_key": self.security_token,
            'plan_amount': data['plan_amount'],
            'plan_name': data['plan_name'],
            'plan_id': data['plan_id'],
            'month_frequency': data['month_frequency'],
            'day_of_month': data['day_of_month'],
            'plan_payments': data['plan_payments']
        }
        response = requests.post(url="https://secure.nmi.com/api/transact.php", data=data)
        return {"response": response, "req": data, "type": 'add_plan_by_month_config', 'org': self.org}

    @log
    @postProcessingOutput
    def edit_plan_by_month_config(self, data)-> Dict[str, Union[Any, str]]: 
        data = {
            'recurring': 'edit_plan',
            "security_key": self.security_token,
            'plan_amount': data['plan_amount'],
            'plan_name': data['plan_name'],
            'current_plan_id': data['plan_id'],
            'month_frequency': data['month_frequency'],
            'day_of_month': data['day_of_month'],
            'plan_payments': data['plan_payments']
        }
        response = requests.post(url="https://secure.nmi.com/api/transact.php", data=data)
        return {"response": response, "req": data, "type": 'edit_plan_by_month_config', 'org': self.org}


    @log
    @postProcessingOutput
    def add_plan_by_day_frequency(self, data)-> Dict[str, Union[Any, str]]: 
        data = {
            'recurring': 'add_plan',
            "security_key": self.security_token,
            'plan_amount': data['plan_amount'],
            'plan_name': data['plan_name'],
            'plan_id': data['plan_id'],
            'day_frequency': data['day_frequency'],
            'plan_payments': data['plan_payments']
        }
        response = requests.post(url="https://secure.nmi.com/api/transact.php", data=data)
        return {"response": response, "req": data, "type": 'add_plan_by_day_frequency', 'org': self.org}


    @log
    @postProcessingOutput
    def edit_plan_by_day_frequency(self, data)-> Dict[str, Union[Any, str]]:
        data = {
            'recurring': 'edit_plan',
            "security_key": self.security_token,
            'plan_amount': data['plan_amount'],
            'plan_name': data['plan_name'],
            'current_plan_id': data['plan_id'],
            'day_frequency': data['day_frequency'],
            'plan_payments': data['plan_payments']
        }
        response = requests.post(url="https://secure.nmi.com/api/transact.php", data=data)
        return {"response": response, "req": data, "type": 'edit_plan_by_day_frequency', 'org': self.org}


    @postProcessXml
    def get_all_plans(self) -> Any:
        url = "https://secure.nmi.com/api/query.php"
        query = {
            "security_key": self.security_token,
            "report_type": "recurring_plans",
        }
        response = requests.post(url=url, data=query)        
        return response
    

    # @postProcessXml
    def get_plan(self, id) -> Union[None, Dict[str, Any]]:
        plans = self.get_all_plans()
        for plan in plans['nm_response']['plan']:
            if plan['plan_id'] == id:
                return plan
            
        return None
