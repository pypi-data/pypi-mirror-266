from nmigate.src.nmigate.lib.billing import Billing
import unittest


class TestBilling(unittest.TestCase):
    def test_add(self):
        billing = Billing('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        res = billing.add({
            "user_id": "1",
            "billing_id": "132",
            "token": "00000000-000000-000000-000000000000",
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
        self.assertEqual(res["nm_response"]["response_code"], "100")

    def test_update(self):
        billing = Billing('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        res = billing.update({
            "user_id": "1",
            "billing_id": "132",
            "token": "00000000-000000-000000-000000000000",
            "billing_info": {
                "first_name": "Peter", 
                "last_name": "1", 
                "address1": "1", 
                "city": "12", 
                "state": "1", 
                "zip": "1", 
                "country": "1", 
                "phone": "1", 
                "email": "1"
            }
        })
        print(res)
        self.assertEqual(res["nm_response"]["response_code"], "100")

    def test_delete(self):
        billing = Billing('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        res = billing.delete("1", "132")
        self.assertEqual(res["nm_response"]["response_code"], "100")


    def test_change_subscription_billing(self):
        billing = Billing('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        res = billing.change_subscription_billing({
            "user_id": "1",
            "billing_id": "12",
            "subscription_id": "8965562207",
        })
        print(res)
        self.assertEqual(res["nm_response"]["response_code"], "100")    

    def test_set_priority(self):
        billing = Billing('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        res = billing.set_priority("1", "f00da1e2689d4dbca6d8c611e62e824d", "1")
        print(res)
        self.assertEqual(res["nm_response"]["response_code"], "100")