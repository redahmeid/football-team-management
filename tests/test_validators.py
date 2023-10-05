import unittest
import validators



class TestValidatorMethods(unittest.TestCase):
    def test_validate_valid_email(self):
        valid = validators.validate_email("r.hmeid@gmail.com")
        self.assertTrue(valid)
    def test_validate_missing_at_email(self):
        valid = validators.validate_email("r.hmeidgmail.com")
        self.assertFalse(valid)
    def test_validate_missing_com_email(self):
        valid = validators.validate_email("r.hmeid@gmail")
        self.assertFalse(valid)

    def test_validate_valid_short_name(self):
        valid = validators.validate_short_name("MUFCJRs")
        self.assertTrue(valid)
    def test_validate_invalid_short_name_spaces(self):
        valid = validators.validate_email("MUFc JRs")
        self.assertFalse(valid)
    

        