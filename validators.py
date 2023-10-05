import re

def validate_short_name(value):
    print("In validate short name")
    if not re.search(r'\s', value):
        return True
    else:
        return False
    
def validate_email(value):
     print("In validate email")
     pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
     if re.match(pattern, value) is not None:
        return True
     else:
        return False