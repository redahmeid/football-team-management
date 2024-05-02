import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import app_config
import json
from fcatimer import fcatimer

async def contact_us(event,context):
    body =json.loads(event["body"])
    email = body["email"]
    message = body["message"]
    await send_email("footballapp@openlight.io","",message,f"From {email}")


async def send_email(to,to_name,content,subject):

    message = Mail(
    from_email='The Football Coach App <footballapp@openlight.io>',
    to_emails=to,
    subject=subject)
    try:
        template_data = {
            "message": content,
            "subject":subject
        }
        sg = SendGridAPIClient(app_config.email_token)
        message.template_id = "d-b75dac7575684bfab1728867e27b8e42"
        message.dynamic_template_data=template_data
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)

@fcatimer
async def send_email_with_template(to,template_id,template_data):

    message = Mail(
    from_email='The Football Coach App <footballapp@openlight.io>',
    to_emails=to,)
    try:
        
        sg = SendGridAPIClient(app_config.email_token)
        message.template_id = template_id
        message.dynamic_template_data=template_data
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)