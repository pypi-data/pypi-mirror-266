import unittest
from unittest.mock import patch
from wknmi.subscriptions import Subscriptions


class TestSubscriptions(unittest.TestCase):

    @unittest.skip("skipped test")
    def test_add_with_custom_month_frequency_config(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.add_with_custom_month_frequency_config(
            {
                "userId": "1",
                "orderId": "test",
                "totalAmount": "0",  # 0 for subscription without an addition sale amount
                "customSubscriptionInfo": {
                    "planId": "test",
                    "planAmount": "10.00",
                    "planName": "test",
                    "monthFrequency": "1",
                    "dayOfMonth": "1",
                    "planPayments": "12",
                    "startDate": "2024/08/08",
                },
            }
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    # @unittest.skip("skipped test")
    def test_add_with_custom_day_frequency_config(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.add_with_custom_day_frequency_config(
            {
                "userId": "1",
                "org": "testOrg4",
                "orderId": "1",
                "totalAmount": "0",  # 0 for subscription without an addition sale amount
                "customSubscriptionInfo": {
                    "planPayments": "15",
                    "planAmount": "6",
                    "dayFrequency": "1",
                    "startDate": "20240808",
                },
            }
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    @unittest.skip("skipped test")
    def test_pause(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.pause("8963837207", "true")
        self.assertEqual(result["status_code"], 200)

    @unittest.skip("skipped test")
    def test_cancel(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.cancel("8963837207")
        self.assertEqual(result["status_code"], 200)

    @unittest.skip("skipped test")
    def test_by_user_id(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.by_user_id("1")
        print(result)
        self.assertEqual(result["status_code"], 200)

    @unittest.skip("skipped test")
    def test_id(self):
        subsObj = Subscriptions(url="http://127.0.0.1:8000", org="testOrg4")
        result = subsObj.id("9387376482")
        print(result)
        self.assertEqual(result["status_code"], 200)
