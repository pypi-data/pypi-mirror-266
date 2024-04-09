from nmigate.src.nmigate.lib.transactions import Transactions
import unittest


class TestTransactions(unittest.TestCase):
    def test_pay_with_token(self):
        transactions = Transactions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        result = transactions.pay_with_token({
            "token": "00000000-000000-000000-000000000000",
            "total": 5,
            "billing_info":{
                "first_name": "test",
                "last_name": "test",
                "company": "test",
                "address1": "test",
                "city": "test",
                "state": "test", 
                "zip": "test",
                "country": "test",
                "phone": "test",
                "email": "test",
            }
        })
        self.assertEqual(result['nm_response']['response_code'], "100")


    def test_pay_with_customer_vault(self):
        transactions = Transactions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        result = transactions.pay_with_customer_vault({
            "user_id": "1",
            "total": 10,
        })
        self.assertEqual(result['nm_response']['response_code'], "100")


    def test_refound(self):
        transactions = Transactions('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        result = transactions.refund("8926614344")
        self.assertEqual(result['nm_response']['response_code'], "100")

    
    