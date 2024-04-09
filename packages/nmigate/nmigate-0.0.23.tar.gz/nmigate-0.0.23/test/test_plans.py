import unittest
from unittest.mock import patch
from src.nmigate.lib.plans import Plans

class TestPlans(unittest.TestCase):
    def test_get_plans(self):
        plansObj = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plansObj.get_all_plans()
        plans = response['nm_response']['plan']
        self.assertGreater(len(plans), 0)

    def test_get_plan(self):
        plans = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plans.get_plan("swzshoppingonly")
        self.assertEqual(response['plan_id'], 'swzshoppingonly')


    def test_add_plan_by_day_frequency(self):
        plans = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plans.add_plan_by_day_frequency({
            'plan_amount': '10.00',
            'plan_name': 'test',
            'plan_id': 'test',
            'day_frequency': '1',
            'plan_payments': '0'
        })
        self.assertEqual(response['nm_response']['response_code'][0], '100')
        self.assertEqual(response['successfull'], True)


    def test_edit_plan_by_day_frequency(self):
        plans = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plans.edit_plan_by_day_frequency({
            "recurring": "edit_plan",
            'plan_amount': '10.00',
            'plan_name': 'test',
            'plan_id': 'test',
            'day_frequency': '2',
            'plan_payments': '0'
        })
        self.assertEqual(response['nm_response']['response_code'][0], '100')
        self.assertEqual(response['successfull'], True)




    def test_add_plan_by_month_config(self):
        plans = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plans.add_plan_by_month_config({
            'plan_amount': '10.00',
            'plan_name': 'test',
            'plan_id': 'test1',
            'month_frequency': '1',
            "day_of_month": '1',
            'plan_payments': '0'
        })

        self.assertEqual(response['nm_response']['response_code'][0], '100')
        self.assertEqual(response['successfull'], True)


    def test_edit_plan_by_month_config(self):
        plans = Plans('4QaH5w77U2k843fu68EuB34c4M5KJ7r3', 'testOrg')
        response = plans.edit_plan_by_month_config({
            'plan_amount': '10.00',
            'plan_name': 'test',
            'plan_id': 'test1',
            'month_frequency': '1',
            "day_of_month": '10',
            'plan_payments': '0'
        })

        self.assertEqual(response['nm_response']['response_code'][0], '100')
        self.assertEqual(response['successfull'], True)
    


if __name__ == '__main__':
    unittest.main()