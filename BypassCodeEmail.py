import datetime

import duo_client
import config
import smtplib

# Pull API settings from config.py
api = duo_client.Admin(
    ikey=config.IKEY,
    skey=config.SKEY,
    host=config.API_HOSTNAME
)

# Set the user you want to create a bypass code for
user_id = config.USER_ID_1

# Delete existing codes before adding new codes
try:
    bypass_codes = api.get_user_bypass_codes(user_id=user_id)
    # For loop since this can be a list of codes
    for bypass_code in bypass_codes:
        api.delete_bypass_code_by_id(bypass_code["bypass_code_id"])
    print("All existing bypass codes for user deleted.")
except RuntimeError as e:
    print(f'Error deleting existing bypass codes: {e}')

# Get current time
now = datetime.datetime.now()

# Get 604800 seconds from now
future = now + datetime.timedelta(seconds=604800)

# Create a new bypass code
try:
    bypass = api.add_user_bypass_codes(user_id=user_id, count=1, valid_secs=604800, remaining_uses=0)
    print(bypass)
except RuntimeError as e:
    print(f'Error creating bypass code: {e}')

# Get email settings from config.py
from_email = config.FROM_EMAIL
to_email = config.TO_EMAIL
smtp_server = config.SMTP_SERVER
smtp_port = 587

# Message and subject for email
message = f'Subject: {config.VENDOR} Duo bypass code\n\nHello,\n\n{config.VENDOR}\'s Duo bypass code for this week is: {bypass} and valid from {now.strftime("%Y-%m-%d %H:%M")} to {future.strftime("%Y-%m-%d %H:%M")} MST'

# Send email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.sendmail(from_email, to_email, message)
    print(f'Bypass code sent to {to_email}')
except smtplib.SMTPException as e:
    print(f'Error sending email: {e}')
