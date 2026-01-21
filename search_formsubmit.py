#!/usr/bin/env python3
import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    token_path = os.path.expanduser('~/.config/gcloud/legacy_credentials/mike.shipley@clemsonlittletheatre.com/adc.json')

    if not os.path.exists(token_path):
        # Try alternative token locations
        alt_paths = [
            os.path.expanduser('~/.config/gcloud/application_default_credentials.json'),
            'C:\\Users\\michael.shipley.QUARRY\\.config\\gcloud\\legacy_credentials\\mike.shipley@clemsonlittletheatre.com\\adc.json'
        ]
        for path in alt_paths:
            if os.path.exists(path):
                token_path = path
                break

    try:
        from google.oauth2.credentials import Credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception as e:
        print(f"Error loading credentials: {e}")
        return

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

    service = build('gmail', 'v1', credentials=creds)

    # Search for FormSubmit emails
    query = 'from:formsubmit.co OR from:forms@formsubmit.co OR subject:"activate" OR subject:"confirm"'
    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No FormSubmit verification emails found")
        print("\nSearching for any recent emails with 'form' in subject...")
        results = service.users().messages().list(userId='me', q='subject:form', maxResults=5).execute()
        messages = results.get('messages', [])

    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

        print(f"\nDate: {date}")
        print(f"From: {from_email}")
        print(f"Subject: {subject}")
        print(f"Message ID: {msg['id']}")
        print("-" * 80)

if __name__ == '__main__':
    main()
