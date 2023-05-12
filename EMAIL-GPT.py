# Made by Jack Warren
# Thanks to EDGE GPT Team and contributors!!! @ https://github.com/acheong08/EdgeGPT
# You can Open pull requests and report issues for EdgeGPT's "BingImageCreator" at https://github.com/acheong08/BingImageCreator

# BUILT-IN MODULES #

# Server Related Modules
import imaplib  # Library for IMAP functionality
import ssl  # Library for SSL functionality

# General use modules
import time  # Library for time-related operations

# Personalized settings scripts in : ./Personalize
from Personlize import email_server  # Import personalized settings for email server and credentials
from Personlize import credentials # Import personalized credentials
from Personlize import prompt_templates # Import personalized prompt templates

# Functions for the emailing process and such: ./Email_Functions
from Personlize.Functions import *  # Import functions related to email processing


# ****************************** MAIN BEGINNING **************************** #

# Open API key for authentication
try:
    openai.api_key = credentials.open_api_key
except Exception as e:
    print(e)
    print('Your API Key may not be set, check credentials.py in Personalized folder.')

# Connection details to connect to email server
# IMAP connection details
imap_server = email_server.server_imap_address
imap_port = email_server.server_imap_port
imap_username = credentials.email_username
imap_password = credentials.email_app_password

# SMTP connection details
smtp_server = email_server.server_smtp_address
smtp_port = email_server.server_smtp_port
smtp_username = credentials.email_username
smtp_password = credentials.email_app_password

# Disable SSL certificate to avoid error (try with SSL first always)
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE


def main():
    print('Beginning loops')
    while True:
        try:
            unread_emails = fetch_unread_emails()  # Fetch unread emails
            if unread_emails:
                print(f'{len(unread_emails)} EMAIL(S) RECEIVED')
                with imaplib.IMAP4_SSL(imap_server, imap_port) as imap:
                    imap.login(imap_username, imap_password)
                    imap.select()
                    for num in unread_emails:
                        process_email(imap, num)  # Process each unread email
        except Exception as e:
            print(f'Error: {e}')
            print('Check personalized folder and edit credentials and email_server')
        time.sleep(5)  # Sleep for 5 seconds before repeating the loop


if __name__ == '__main__':
    main()

# ......................................... MAIN END ........................................ #
