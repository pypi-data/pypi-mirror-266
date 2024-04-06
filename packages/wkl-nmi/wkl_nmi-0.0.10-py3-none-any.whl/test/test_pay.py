import unittest
from unittest.mock import patch
from wknmi.payment import Pay


class TestPayments(unittest.TestCase):
    # @unittest.skip("isolating testing")
    def test_with_token(self):
        pay = Pay(url="http://127.0.0.1:8000", org="testOrg4")
        result = pay.with_token(
            {
                "token": "00000000-000000-000000-000000000000",
                "total": "19",
                "billingInfo": {},
            }
        )
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    @unittest.skip("isolating testing")
    def test_with_customer_vault(self):
        # result = pay.with_customer_vault(
        #     {
        #         "customerVault": "1",
        #         "total": "4",
        #         "billingInfo": {},
        #     }
        # )
        pay = Pay(url="https://nmi-server-orkrbzqvda-uc.a.run.app", org="commonsense")

        payload = {
            "customerVault": "1367c100c27874b7a726c13c248c7391d2a8",
            "total": "194.91",
            "billingInfo": {
                "company": "",
                "address2": "",
                "fax": "",
                "shipping_id": "",
                "shipping_address1": "",
                "shipping_address2": "",
                "shipping_city": "",
                "shipping_country": "",
                "shipping_zip": "",
                "shipping_state": "",
                "shipping_first_name": "",
                "shipping_last_name": "",
                "shipping_phone": "",
                "shipping_email": "",
            },
        }

        result = pay.with_customer_vault(payload)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")

    @unittest.skip("isolating testing")
    def test_refund(self):
        pay = Pay(url="http://127.0.0.1:8000", org="testOrg4")
        result = pay.refund("9320577122")
        print(result)
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["response"]["nm_response"]["response_code"], "100")
