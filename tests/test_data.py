import unittest
from config import app_config
import handler
import classes
import json
import drop_database
import create_database
from py_event_mocks import create_event



class TestData(unittest.TestCase):
    
    

    def test_create_valid_club(self):
         print("test_create_valid_club")
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","short_name":"MUFCJrs","email":"r.hmeid@gmail.com","phone":"07973931840","admin":[{"name":"Reda Hmeid","role":"Chair","email":"r.hmeid@gmail.com"}]})}
                    )
         
         response = handler.create_club(event,None)
         
         self.assertEqual(response["statusCode"],200)
        
         self.assertIsNotNone(json.loads(response["body"])["result"]["club_id"])

    def test_create_missing_short_name_club(self):
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","email":"r.hmeid@gmail.com","phone":"07973931840","admin":[{"name":"Reda Hmeid","role":"Chair","email":"r.hmeid@gmail.com"}]})}
                    )
         
         response = handler.create_club(event,None)
         
         self.assertEqual(response["statusCode"],400)
         self.assertEqual(json.loads(response["body"])["errors"][0]["type"],"missing")
         self.assertEqual(json.loads(response["body"])["errors"][0]["field"],"short_name")

    def test_create_invalid_short_name_club(self):
         print("test_create_invalid_short_name_club")
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","short_name":"MUFC Jrs","email":"r.hmeid@gmail.com","phone":"07973931840","admin":[{"name":"Reda Hmeid","role":"Chair","email":"r.hmeid@gmail.com"}]})}
                    )
         
         response = handler.create_club(event,None)
         print(response)
         self.assertEqual(response["statusCode"],400)
         self.assertEqual(json.loads(response["body"])["errors"][0]["type"],"value_error")
         self.assertEqual(json.loads(response["body"])["errors"][0]["field"],"short_name")

    def test_create_missing_email_club(self):
         print("test_create_missing_email_club")
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","short_name":"MUFCJrs","phone":"07973931840"})}
                    )
         
         response = handler.create_club(event,None)
         print(response)
         self.assertEqual(response["statusCode"],400)
         self.assertEqual(json.loads(response["body"])["errors"][0]["type"],"missing")
         self.assertEqual(json.loads(response["body"])["errors"][0]["field"],"email")

    def test_create_invalid_email_club(self):
         print("test_create_invalid_email_club")
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","short_name":"MUFCJrs","email":"hjgjfadfs","phone":"07973931840","admin":[{"name":"Reda Hmeid","role":"Chair","email":"r.hmeid@gmail.com"}]})}
                    )
         
         response = handler.create_club(event,None)
         print(response)
         self.assertEqual(response["statusCode"],400)
         self.assertEqual(json.loads(response["body"])["errors"][0]["type"],"value_error")
         self.assertEqual(json.loads(response["body"])["errors"][0]["field"],"email")

    def test_create_missing_phone_club(self):
         event = create_event(
                event_type="aws:api-gateway-event",body={"body":json.dumps({"name":"Maidenhead United Juniors","short_name":"MUFCJrs","email":"r.hmeid@gmail.com"})}
                    )
         
         response = handler.create_club(event,None)
         print(response)
         self.assertEqual(response["statusCode"],400)
         self.assertEqual(json.loads(response["body"])["errors"][0]["type"],"missing")
         self.assertEqual(json.loads(response["body"])["errors"][0]["field"],"phone")