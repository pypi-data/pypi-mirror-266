# NMI Gateway

This is a nmi handy package to interact with the nmi gateway endpoints, you can find the original documentation here:
https://secure.networkmerchants.com/gw/merchants/resources/integration/integration_portal.php#cv_variables

This package was build with the unique intention to make the integration with the gateway easy.

## Examples

### Customer Vault methods

#### Create customer vault

```python
from nmigate.lib.customer_vault import CustomerVault

secret_key = 'your secret key'
org = 'your org'
token = 'your test token here' # test token "00000000-000000-000000-000000000000"

customer_vault = CustomerVault(secret_key, org)
    result = customer_vault.create_customer_vault({
        "id": "",
        "token": token,
        "billing_id": "",
        "billing_info": {
            "first_name": "1",
            "last_name": "1",
            "address1": "1",
            "city": "1",
            "state": "1",
            "zip": "1",
            "country": "1",
            "phone": "1",
            "email": "1"
        }
    })
```

#### Get billing info by transaction id

```python
from nmigate.lib.customer_vault import CustomerVault

secret_key = 'your secret key'
org = 'your org'
transaction_id = 'transaction id '

customer_vault = CustomerVault(secret_key, org)
result = customer_vault.get_billing_info_by_transaction_id(transaction_id)
```

### Plans

### Get all plans

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'

plansObj = Plans(secret_key, org)
response = plansObj.get_all_plans()
plans = response['nm_response']['plan']

```

### Get plan

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'
plan_id = 'your plan id'

plans = Plans(secret_key, org)
response = plans.get_plan(plan_id)

```

### Add plan using frequency configuration

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'

plans = Plans(secret_key, org)
response = plans.add_plan_by_day_frequency({
    'plan_amount': '10.00',
    'plan_name': 'test',
    'plan_id': 'test',
    'day_frequency': '1',
    'plan_payments': '0'
})

```

### Edit day frequency plan

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'

plans = Plans(secret_key, org)
response = plans.edit_plan_by_day_frequency({
    "recurring": "edit_plan",
    'plan_amount': '10.00',
    'plan_name': 'test',
    'plan_id': 'test',
    'day_frequency': '2',
    'plan_payments': '0'
})

```

### Add plan using month config

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'

plans = Plans(secret_key, org)
response = plans.add_plan_by_month_config({
    'plan_amount': '10.00',
    'plan_name': 'test',
    'plan_id': 'test1',
    'month_frequency': '1',
    "day_of_month": '1',
    'plan_payments': '0'
})

```

### Edit plan using month config

```python
from nmigate.src.nmigate.lib.plans import Plans

secret_key = 'your secret key'
org = 'your org'

plans = Plans(secret_key, org)
response = plans.edit_plan_by_month_config({
    'plan_amount': '10.00',
    'plan_name': 'test',
    'plan_id': 'test1',
    'month_frequency': '1',
    "day_of_month": '10',
    'plan_payments': '0'
})
```

### Subscriptions

#### Get Subscriptions

```python
from nmigate.lib.customer_vault import CustomerVault

secret_key = 'your secret key'
org = 'your org'
subscription_id='customer vault id'

subscriptions = Subscriptions(secret_key, org)
info = subscriptions.get_info(subscription_id)
print(result)
```

#### Subscription + sale, using plan_id and customer vault

If total_amount = 0 then its a simple subscription, if total_amount > 0 then its a subscription with sale

```python
from nmigate.lib.customer_vault import CustomerVault

secret_key = 'your secret key'
org = 'your org'
customer_vault_id='customer vault id'

subscriptions = Subscriptions(secret_key, org)
result = subscriptions.custom_sale_using_vault(plan_id = customer_vault_id, customer_vault_id=customer_vault_id, create_customer_vault=False)
print(result)
```

#### Custome Subscription + sale, using vault number and month frequency configuration

```python
from nmigate.lib.subscriptions import Subscriptions

secret_key = 'your secret key'
org = 'your org'

subscriptions = Subscriptions(secret_key, org)
result = subscriptions.custom_sale_using_vault_month_frequency(request_sub = {
    "user_id": "1",
    "total_amount": "11",
    "custom_subscription_info": {
        "plan_payments": "13",
        "plan_amount": "12",
        "month_frequency": "1",
        "day_of_month": "1"
    }
})
print(result)

```

#### Custome Subscription + sale, using vault number and day frequency configuration

```python
from nmigate.lib.subscriptions import Subscriptions

secret_key = 'your secret key'
org = 'your org'

subscriptions = Subscriptions(secret_key, org)
result = subscriptions.custom_with_sale_and_vault_day_frequency(request_sub = {
    "user_id": "1",
    "total_amount": "14",
    "custom_subscription_info": {
        "plan_payments": "15",
        "plan_amount": "6",
        "day_frequency": "1"
    }
})
print(result)
```

#### Delete subscription

```python
from nmigate.lib.subscriptions import Subscriptions

secret_key = 'your secret key'
org = 'your org'
subscription_id = 'your subscription_id'

subscriptions = Subscriptions(secret_key, org)
info = subscriptions.delete_subscription(subscription_id)
```

#### Pause/resume Subscription

```python
from nmigate.lib.subscriptions import Subscriptions

secret_key = 'your secret key'
org = 'your org'
subscription_id = 'your subscription_id'
pause=True # True to pause, False to unpause

transactions = Subscriptions(secret_key, org)
result = transactions.pause_subscription(subscription_id, pause)
```
