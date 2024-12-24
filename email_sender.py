import os
import json
import base64
from email.mime.text import MIMEText
from gmail_service import get_gmail_service
import re

class EmailSender:
    def __init__(self):
        """Initialize EmailSender."""
        self.service = get_gmail_service()
        self.emails_to_send_dir = 'Emails_To_Send'
        self.sent_dir = os.path.join(self.emails_to_send_dir, 'Sent')
        os.makedirs(self.sent_dir, exist_ok=True)

    def get_or_create_label(self, label_name):
        """Get label ID by name or create if it doesn't exist."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Check if label exists
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            # Create new label if it doesn't exist
            label_object = {
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            return created_label['id']
            
        except Exception as e:
            print(f"Error getting/creating label: {e}")
            return None

    def apply_label_to_message(self, message_id, label_name):
        """Apply a label to a message."""
        try:
            # Get or create label
            label_id = self.get_or_create_label(label_name)
            if not label_id:
                return False
            
            # Modify the message to add the label
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            print(f"Applied label '{label_name}' to message {message_id}")
            return True
        except Exception as e:
            print(f"Error applying label: {e}")
            return False

    def get_all_labels(self):
        """Get all Gmail labels."""
        try:
            results = self.service.users().labels().list(userId='me').execute()
            return results.get('labels', [])
        except Exception as e:
            print(f"Error getting labels: {e}")
            return []

    def remove_all_labels_except(self, message_id, keep_label_name):
        """Remove all labels from a message except the specified one."""
        try:
            # Get current labels
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            current_labels = message.get('labelIds', [])
            
            # Get all labels to find the ID of the label to keep
            all_labels = self.get_all_labels()
            keep_label_id = next((label['id'] for label in all_labels if label['name'] == keep_label_name), None)
            
            # Determine which labels to remove
            remove_labels = [label_id for label_id in current_labels 
                           if label_id not in ['INBOX', keep_label_id]]  # Keep INBOX label
            
            if remove_labels:
                self.service.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': remove_labels}
                ).execute()
                print(f"Removed all labels except '{keep_label_name}' from message {message_id}")
            
            return True
        except Exception as e:
            print(f"Error removing labels: {e}")
            return False

    def process_label_command(self, response_content, message_id):
        """Process special label commands in the response."""
        # Check for label command pattern: $LabelName$
        match = re.match(r'^\$([^$]+)\$(.*)', response_content, re.DOTALL)
        if match:
            label_name = match.group(1)
            actual_content = match.group(2).strip()
            
            # Apply the label
            if self.apply_label_to_message(message_id, label_name):
                # Remove all other labels except this one
                self.remove_all_labels_except(message_id, label_name)
            
            # Return the content without the label command
            return actual_content if actual_content else None  # Return None if content is empty
        
        return response_content

    def create_email_message(self, response_data):
        """Create email message from response data."""
        try:
            # Extract original email info
            original_email = response_data['original_email']
            
            # Process the response content for label commands
            response_content = self.process_label_command(
                response_data['response'],
                response_data['email_id']
            )
            
            # If response_content is None (empty after label command), don't create message
            if response_content is None:
                print("Skipping empty response")
                return None
            
            # Create message
            message = MIMEText(response_content)
            message['to'] = original_email['sender']
            message['subject'] = f"Re: {original_email['subject']}"
            
            # Add threading headers if Message-ID is available
            if 'message_id' in original_email:
                message['References'] = original_email['message_id']
                message['In-Reply-To'] = original_email['message_id']
            
            # Encode in base64
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            # Create Gmail API message
            gmail_message = {
                'raw': raw,
                'threadId': response_data['thread_id']
            }
            
            return gmail_message
        except Exception as e:
            print(f"Error creating email message: {e}")
            return None

    def send_email(self, message):
        """Send an email message."""
        try:
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            print(f"Email sent successfully. Message ID: {sent_message['id']}")
            return sent_message['id']
        except Exception as e:
            print(f"Error sending email: {e}")
            return None

    def process_pending_responses(self):
        """Process all pending responses and send emails."""
        sent_count = 0
        pending_responses = []
        
        # Get list of pending responses
        for file in os.listdir(self.emails_to_send_dir):
            if file.endswith('.json') and not file.startswith('sent_'):
                pending_responses.append(file)
        
        print(f"\nFound {len(pending_responses)} pending responses to send\n")
        
        for file in pending_responses:
            try:
                # Load response data
                file_path = os.path.join(self.emails_to_send_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    response_data = json.load(f)
                
                print(f"Processing response to: {response_data['original_email']['sender']}")
                print(f"Subject: {response_data['original_email']['subject']}\n")
                print("Response content:")
                print("-" * 50)
                print(response_data['response'])
                print("-" * 50)
                
                # Create and send email
                message = self.create_email_message(response_data)
                if message and self.send_email(message):
                    print("Successfully sent email")
                    # Move to sent folder
                    sent_path = os.path.join(self.sent_dir, file)
                    os.rename(file_path, sent_path)
                    print(f"Moved response to {sent_path}")
                    sent_count += 1
                else:
                    print("Failed to send email")
            except Exception as e:
                print(f"Error processing response file {file}: {e}")
        
        print(f"Sent {sent_count} responses")
        return sent_count
