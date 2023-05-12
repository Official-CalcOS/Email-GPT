#BUILT IN MODULES#
import sys
P_path = ['Personlize\\','output\\', 'previous_images\\']
for A_path in P_path:
    print('Added to path: ' + A_path)
    sys.path = [A_path] + sys.path
    
# Server Related Modules
import imaplib
import smtplib
import ssl

#Email Related Modules
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

#General use modules
import random
import string

#OS dependent modules (may need to change, since this project is made around windows 10)
import os
import shutil
import subprocess

# Externals (i.e. Pip installs)
import openai
# Command: pip install openai

# Personalized settings scripts in : ./Personalize
from email_server import *  # Import personalized settings for email server and credentials
from credentials import * # Import personalized credentials
from prompt_templates import *  # Import personalized prompt templates

# Disable SSL certificate to avoid error (try with SSL first always)
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE



#***********************************FUNCTIONS START********************************#


def generate_random_name():
    """Generate a random 15-digit filename."""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(15))



def move_img():
    source_dir = 'output\\'
    destination_dir = 'previous_images\\'

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Get a list of all image files in the source directory
    image_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

    # Move each image file to the destination directory with a random name
    for file_name in image_files:
        source_path = os.path.join(source_dir, file_name)
        destination_path = os.path.join(destination_dir, generate_random_name() + '.jpg')  # Change the extension if necessary
        shutil.move(source_path, destination_path)

    print("Generated images moved successfully to storage folder.")



def generate_response(prompt):
    try:
        completion = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=2048,
        )
        response = completion.choices[0].text.strip()
        print(response)
        return response
    except Exception as e:
        response = str(e)
        print(response)
        return response


def process_email(imap, num):
    images_generated = False  # Flag to track if images were generated
    typ, msg_data = imap.fetch(num, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            sender_email = msg.get('Reply-To') or msg.get('From')

            text_content = ""
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text':
                    payload = part.get_payload(decode=True)
                    if payload:
                        text_content += payload.decode()


            text_low = text_content.lower()
            if 'image' in text_low:
                images_generated = True
                prompt = img_prompt(sender_email, text_content)

                print(prompt)
            else:
                images_generated = False
                prompt = text_prompt(sender_email, text_content)
                print(prompt)

            response = generate_response(prompt)  # Use regular model

            with smtplib.SMTP_SSL(server_smtp_address, server_smtp_port, context=context) as server:
                server.login(email_username, email_app_password)
                msg = MIMEMultipart()
                msg['From'] = email_username
                msg['To'] = sender_email
                msg['Subject'] = 'Response'

                if 'image' in text_low:
                    images_generated = True
                    print('Generating images for email')
                    # Generate images
                    image_generation_process = subprocess.Popen(['python', 'ImageGen.py', '--cookie-file', 'cookies.json',
                                                                 '--prompt', text_content, '--output-dir', './output/'])
                    image_generation_process.wait()  # Wait for image generation process to finish
                    # Get the list of image files in the images folder
                    image_files = [f for f in os.listdir('./output') if os.path.isfile(os.path.join('./output', f))]

                    if image_files:
                        # Add a plain text message
                        full_response = f'''{response}
------------------------------------------------
Please find the attached images.'''

                        msg.attach(MIMEText(full_response, 'plain'))

                        # Attach each image file
                        for image_file in image_files:
                            with open('./output/' + image_file, 'rb') as file:
                                image_data = file.read()
                            image = MIMEImage(image_data)
                            image.add_header('Content-Disposition', 'attachment', filename=image_file)
                            msg.attach(image)

                        server.send_message(msg)

                        print('Images attached and email sent...')

                        # Move the generated images to the previous_images folder
                        move_img()

                elif not images_generated:
                    with smtplib.SMTP_SSL(server_smtp_address, server_smtp_port, context=context) as server:
                        server.login(email_username, email_app_password)
                        msg = MIMEMultipart()
                        msg['From'] = email_username
                        msg['To'] = sender_email
                        msg['Subject'] = 'Response'
                        msg.attach(MIMEText(response, 'plain'))
                        server.send_message(msg)

                    imap.store(num, '+FLAGS', '\\Seen')

    print('\nAll emails processed...\n')





def fetch_unread_emails():
    with imaplib.IMAP4_SSL(server_imap_address, server_imap_port) as imap:
        imap.login(email_username, email_app_password)
        _, data = imap.select(mailbox='INBOX', readonly=True)
        typ, response = imap.search(None, 'UNSEEN', 'NOT', 'FROM', 'emaillmofficial@gmail.com')
        if typ == 'OK':
            return response[0].split()
        return []






#.........................................FUNCTIONS END........................................#
