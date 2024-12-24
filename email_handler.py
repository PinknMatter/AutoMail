import os
import base64
import json
import glob
from email.mime.text import MIMEText
from gmail_service import get_gmail_service
from datetime import datetime

class EmailHandler:
    def __init__(self):
        self.service = get_gmail_service()
        self.emails_dir = 'Emails_Received'
        os.makedirs(self.emails_dir, exist_ok=True)
        self._load_processed_emails()

    def _load_processed_emails(self):
        """Load list of already processed email IDs."""
        self.processed_email_ids = set()
        for file_path in glob.glob(os.path.join(self.emails_dir, '*.json')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    email_data = json.load(f)
                    if 'id' in email_data:
                        self.processed_email_ids.add(email_data['id'])
            except Exception as e:
                print(f"Error loading processed email from {file_path}: {e}")

    def get_label_ids(self, label_names):
        """Get Gmail label IDs for given label names."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            label_ids = []
            label_map = {}  # For debugging
            for label in labels:
                label_map[label['name']] = label['id']
            
            print("\nAll available labels and their IDs:")
            for name, id in label_map.items():
                print(f"{name}: {id}")
            
            for label_name in label_names:
                label_id = label_map.get(label_name)
                if label_id:
                    label_ids.append(label_id)
                    print(f"\nFound label '{label_name}' with ID: {label_id}")
                else:
                    print(f"\nLabel '{label_name}' not found.")
            
            return label_ids
        except Exception as e:
            print(f"Error fetching labels: {e}")
            return []

    def get_unread_emails_by_labels(self, label_names=['Beginner', 'Transfers'], unread_only=True):
        """Retrieve emails with specific labels."""
        try:
            label_ids = self.get_label_ids(label_names)
            print(f"\nSearching for emails with label IDs: {label_ids}")
            
            if not label_ids:
                print("No valid label IDs found.")
                return []

            # Build the query
            query = 'is:unread' if unread_only else ''
            print(f"Using query: {query}")
            
            all_messages = []
            # Search for each label separately and combine results
            for label_id in label_ids:
                results = self.service.users().messages().list(
                    userId='me',
                    labelIds=[label_id, 'UNREAD'] if unread_only else [label_id],  # Only get unread messages
                    q=query
                ).execute()
                messages = results.get('messages', [])
                print(f"\nFound {len(messages)} emails with label ID: {label_id}")
                
                # Get full message details including thread ID
                for msg in messages:
                    full_msg = self.service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    msg['threadId'] = full_msg['threadId']
                
                all_messages.extend(messages)

            # Remove duplicates based on message ID
            unique_messages = {msg['id']: msg for msg in all_messages}.values()
            print(f"\nTotal found {len(unique_messages)} unique matching emails")
            return list(unique_messages)
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def get_email_content(self, msg_id, thread_id=None):
        """Retrieve full email content."""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=msg_id, 
                format='full'
            ).execute()
            
            # Extract email body
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            parts = payload.get('parts', [])
            
            # Get body content
            if parts:
                body = parts[0].get('body', {}).get('data', '')
            else:
                body = payload.get('body', {}).get('data', '')
            
            # Decode base64 encoded body
            if body:
                body = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
            
            # Extract email metadata
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            message_id = next((h['value'] for h in headers if h['name'].lower() == 'message-id'), '')
            
            return {
                'id': msg_id,
                'thread_id': thread_id or message['threadId'],  # Use provided thread ID or get from message
                'message_id': message_id,  # Add Message-ID
                'body': body,
                'sender': sender,
                'subject': subject,
                'date': date,
                'labels': message.get('labelIds', [])
            }
        except Exception as e:
            print(f"Error getting email content: {e}")
            return None

    def save_email_to_file(self, email_content):
        """Save email content to a file in the Emails_Received directory."""
        try:
            if not email_content:
                return False

            # Check if email has already been processed
            if email_content['id'] in self.processed_email_ids:
                print(f"Email {email_content['id']} has already been processed, skipping...")
                return False

            # Create a filename using timestamp and email ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{email_content['id']}.json"
            filepath = os.path.join(self.emails_dir, filename)

            # Save email content to JSON file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(email_content, f, indent=2, ensure_ascii=False)

            # Add to processed emails set
            self.processed_email_ids.add(email_content['id'])
            print(f"Saved new email to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving email: {e}")
            return False

    def process_unread_emails(self):
        """Process all unread emails with specified labels."""
        try:
            processed_emails = []
            messages = self.get_unread_emails_by_labels()
            
            for message in messages:
                email_content = self.get_email_content(message['id'], message.get('threadId'))
                if email_content and self.save_email_to_file(email_content):
                    # Mark the email as read after processing
                    try:
                        self.service.users().messages().modify(
                            userId='me',
                            id=message['id'],
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()
                        print(f"Marked email {message['id']} as read")
                    except Exception as e:
                        print(f"Error marking email as read: {e}")
                    
                    processed_emails.append(email_content)
            
            return processed_emails
        except Exception as e:
            print(f"Error processing emails: {e}")
            return []

    def send_email(self, to, subject, body):
        """Send an email via Gmail API."""
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = f"Re: {subject}"
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            print(f"Email sent to {to}")
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
