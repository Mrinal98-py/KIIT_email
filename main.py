from pymongo import MongoClient
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from pymongo import MongoClient
import base64
from gridfs import GridFS
import time
from subprocess import call
from email import message_from_bytes
from dateutil.parser import parse as date_parse
from bs4 import BeautifulSoup

# Create a MongoDB client and connect to the server
client = MongoClient("mongodb+srv://Mrinal:getdataold@mrinal.8kbejgd.mongodb.net/?retryWrites=true&w=majority")

# Specify the database
db = client['email_database']

# Specify the collection within the database for original emails
collection = db['email_collection']

# Create a new collection to store generated emails
generated_collection = db['generated_email_collection']

# Load the GPT-2 model and tokenizer
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

# Set the necessary scopes for reading Gmail messages
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Function to parse the date
def parse_date(date_str):
    try:
        return date_parse(date_str)
    except ValueError:
        return None  # Return None if date parsing fails

# Function to store attachments in MongoDB
def store_attachment_to_mongodb(attachment_data, filename, email_id):
    try:
        fs = GridFS(db)

        # Decode the attachment data from base64
        decoded_data = base64.urlsafe_b64decode(attachment_data.encode('UTF-8'))

        # Store the attachment in MongoDB GridFS
        attachment_id = fs.put(decoded_data, filename=filename, email_id=email_id)

    except Exception as e:
        print("Error storing attachment:", str(e))

# Function to check if an email with the given ID already exists in the database
def is_email_exist(email_id):
    existing_email = collection.find_one({'email_id': email_id})
    return existing_email is not None

# Function to store an email in MongoDB
def store_email_to_mongodb(email_data):
    existing_email = collection.find_one({'email_id': email_data['email_id']})

    if existing_email:
        # Update the existing record with the new email data
        collection.update_one({'email_id': email_data['email_id']}, {'$set': email_data})
        print("Email details updated for ID:", email_data['email_id'])
    else:
        # Insert the email data as a new record
        result = collection.insert_one(email_data)
        print("Email details stored with ID:", result.inserted_id)

# Function to authenticate with Gmail and read emails
# ...

# Function to authenticate with Gmail and read emails
def read_emails_and_store_in_mongodb():
    while True:
        try:
            creds = gmail_authenticate()
            service = build('gmail', 'v1', credentials=creds)

            # Call the Gmail API to fetch a list of messages
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10).execute()
            messages = results.get('messages', [])

            if not messages:
                print("No new messages found.")
            else:
                print("Recent emails:")
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                    headers = msg['payload']['headers']

                    # Extract subject, date, time, sender, and 'To' field from headers
                    subject = [header['value'] for header in headers if header['name'] == 'Subject']
                    subject = subject[0] if subject else 'No subject'
                    date = [header['value'] for header in headers if header['name'] == 'Date']
                    date = date[0] if date else 'Unknown date'
                    time = [header['value'] for header in headers if header['name'] == 'Received']
                    time = time[0].split(';')[1].strip() if time else 'Unknown time'
                    sender = [header['value'] for header in headers if header['name'] == 'From']
                    sender = sender[0] if sender else 'Unknown sender'
                    to = [header['value'] for header in headers if header['name'] == 'To']
                    to = to[0] if to else 'Unknown recipient'

                    email_date = parse_date(date)

                    if email_date is None:
                        print(f"Failed to parse date: {date}")
                        continue  # Skip this email if date parsing fails

                    searching_date = datetime(2023, 6, 1, tzinfo=email_date.tzinfo)

                    if (
                            "dean.it@kiit.ac.in" in sender
                            or "director.csit@kiit.ac.in" in sender
                            or "registrar@kiit.ac.in" in sender
                            or "director.csit@kiit.ac.in" in sender
                            or "dean.cs@kiit.ac.in" in sender
                            or "dean.ccm@kiit.ac.in" in sender
                            or "dean.it@kiit.ac.in" in sender
                            or "vashishthafcs@kiit.ac.in" in sender
                            or "acoe.csit@kiit.ac.in" in sender
                            or "acoe.cese@kiit.ac.in" in sender
                            or "dycoe.csit@kiit.ac.in" in sender
                            or "dean.cs@kiit.ac.in" in sender
                            or "vicechancellor@kiit.ac.in" in sender
                            or "registrar@kiit.ac.in" in sender
                            or "robotics.society@kiit.ac.in" in sender
                            or "academics@kiit.ac.in" in sender
                            or "technical.cse@kiit.ac.in" in sender
                            or "fic.examcell.cse@kiit.ac.in" in sender
                            or "caas.kiit@kiit.ac.in" in sender
                            or "placement@kiit.ac.in" in sender
                            or "tnp.set@kiit.ac.in" in sender
                            or "elabs.electronics@kiit.ac.in" in sender
                            or "r.panda@kiit.ac.in" in sender
                            or "training@kiit.ac.in" in sender
                            or "evaluationcell.cse@kiit.ac.in" in sender
                            or "admission@kiit.ac.in" in sender
                            or "admission5@kiit.ac.in" in sender
                            or "admission6@kiit.ac.in" in sender
                            or "admission10@kiit.ac.in" in sender
                            or "sameer.das@kiit.ac.in" in sender
                            or "kiit.languages@kiit.ac.in" in sender
                            or "compliance.cse@kiit.ac.in" in sender
                            or "helpdesk@kiit.ac.in" in sender
                            or "office.founder@kiit.ac.in" in sender
                            or "noticeboard@kiit.ac.in" in sender
                            or "kiit.sol@kiit.ac.in" in sender
                            or "iot.lab@kiit.ac.in" in sender
                            or "kodewreck.cse@kiit.ac.in" in sender
                            or "director.counseling@kiit.ac.in" in sender
                            or "hostel@kiit.ac.in" in sender
                            or "pulak.rath@kiit.ac.in" in sender
                            or "appliedsciences.kiit@kiit.ac.in" in sender
                            or "exam.ksas@kiit.ac.in" in sender
                            or "deansas@kiit.ac.in" in sender
                            or "laptop.service@kiit.ac.in" in sender
                            or "provicechancellor@kiit.ac.in" in sender
                            or "centrallibrary@kiit.ac.in" in sender
                            or "hi@ecell.org.in" in sender
                            or "21051774@kiit.ac.in" in sender
                            or "rnd@ecell.org.in" in sender
                            or "21051724@kiit.ac.in" in sender
                            or "21051729@kiit.ac.in" in sender
                    ):
                        # if email_date > searching_date:
                            end_date = (email_date + timedelta(days=30)).strftime('%Y-%m-%d')

                            email_id = message['id']

                            # Extract the plain text email body from the message parts
                            email_body = extract_text_from_email_parts([msg['payload']])

                            # Generate the email body using GPT-2
                            generated_email_body = generate_email_body(email_body)

                            email_data = {
                                'email_id': email_id,
                                'subject': subject,
                                'sender': sender,
                                'to': to,
                                'date': date,
                                'end_date': end_date,
                                'time': time,
                                # 'body': email_body,
                                'new_body': generated_email_body,
                                'year' : "4th",
                            }

                            if 'parts' in msg['payload']:
                                for part in msg['payload']['parts']:
                                    if part.get('filename'):
                                        attachment_data = part['body'].get('data', '')
                                        if attachment_data:
                                            decoded_data = base64.urlsafe_b64decode(attachment_data.encode('UTF-8'))
                                            store_attachment_to_mongodb(decoded_data, part['filename'], message['id'])

                            if not is_email_exist(email_id):
                                store_email_to_mongodb(email_data)

                                # Store the generated email in the new collection
                                store_generated_email_to_mongodb(email_data)

                                # Print email details
                                print("Subject:", subject)
                                print("From:", sender)
                                print("To:", to)
                                print("Date:", date)
                                print("Time:", time)
                                print("End Date:", end_date)
                                # print("Original Body:", email_body)  # Print the original email body
                                print("Generated Body:", generated_email_body)  # Print the generated email body
                                print("--------------------------------------------END OF MAIL------------------------------------------------")

            time.sleep(300)  # Sleep for 5 minutes

        except Exception as e:
            print("An error occurred:", str(e))

# ...

# Function to store the generated email in the new collection
def store_generated_email_to_mongodb(email_data):
    generated_collection.insert_one(email_data)

# Function to authenticate with Gmail
def gmail_authenticate():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:\\Users\\Buddy\\Documents\\Downloads\\rawdata\\kiit_mrinal_45_client_secret_599437280540-ch41a8aau7nt2qdltf5ldg80hi9oe3b2.apps.googleusercontent.com.json'
                ,  # Replace with the path to your JSON file
                SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return creds

# Function to extract text from email parts
def extract_text_from_email_parts(parts):
    text = ''
    for part in parts:
        if 'mimeType' in part:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                decoded_data = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                text += decoded_data
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data', '')
                html_content = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                soup = BeautifulSoup(html_content, 'html.parser')
                plain_text = soup.get_text()
                text += plain_text

        if 'parts' in part:
            text += extract_text_from_email_parts(part['parts'])

    return text

# Function to generate email body using GPT-2
def generate_email_body(input_text):
    # Maximum sequence length for the GPT-2 model
    max_sequence_length = 1024

    inputs = tokenizer.encode(input_text[:max_sequence_length], return_tensors='pt')
    outputs = model.generate(
        inputs,
        max_length=400,
        do_sample=True,
        temperature=1.0,
        top_k=50,
        top_p=0.95,
        num_return_sequences=1,
        pad_token_id=model.config.eos_token_id
    )
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return generated_text

# Function to store the generated email in the new collection
def store_generated_email_to_mongodb(email_data):
    generated_collection.insert_one(email_data)

if __name__ == "__main__":
    read_emails_and_store_in_mongodb()
