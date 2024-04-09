import unittest
from nmigate.src.nmigate.lib.subscriptions import Subscriptions

class TestSubs(unittest.TestCase):
    def test_get_plans(self):
        subscriptions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        info = subscriptions.get_info("8462293105")
        self.assertEqual(info['nm_response']['subscription']["subscription_id"], "8462293105")
    

    def test_custom_sale_using_vault(self):
        subscriptions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        result = subscriptions.custom_sale_using_vault(plan_id = "swzpremiumyear", customer_vault_id="1", create_customer_vault=False)
        self.assertEqual(result['nm_response']['response_code'], "100")


    def test_custom_sale_using_vault_month_frequency(self):
        subscriptions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
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
        self.assertEqual(result['nm_response']['response_code'], "100")


    def test_custom_with_sale_and_vault_day_frequency(self):
        subscriptions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
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
        self.assertEqual(result['nm_response']['response_code'], "100")


    def test_delete_subscription(self):
        subscriptions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        info = subscriptions.delete_subscription("8462218027")
        self.assertEqual(info['nm_response']['response_code'], 100)
    
    
    def test_pause_subscription(self):
        transactions = Subscriptions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        result = transactions.pause_subscription("8926648990", True)
        print(result)
        self.assertEqual(result['nm_response']['response_code'], "100")


if __name__ == '__main__':
    unittest.main()