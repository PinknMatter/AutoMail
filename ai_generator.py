import os
import json
import time
from datetime import datetime
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')

class AIGenerator:
    def __init__(self):
        """Initialize AI Generator."""
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI()
        self.emails_received_dir = 'Emails_Received'
        self.emails_to_send_dir = 'Emails_To_Send'
        os.makedirs(self.emails_to_send_dir, exist_ok=True)
        self._load_processed_responses()

    def _load_processed_responses(self):
        """Load list of already processed email IDs."""
        self.processed_email_ids = set()
        for file in os.listdir(self.emails_to_send_dir):
            if file.endswith('.json'):
                self.processed_email_ids.add(file.split('_')[-1].replace('.json', ''))

    def get_unprocessed_emails(self):
        """Get list of emails that haven't been processed yet."""
        unprocessed_emails = []
        for file in os.listdir(self.emails_received_dir):
            if not file.endswith('.json'):
                continue
            
            email_id = file.split('_')[-1].replace('.json', '')
            if email_id not in self.processed_email_ids:
                try:
                    with open(os.path.join(self.emails_received_dir, file), 'r', encoding='utf-8') as f:
                        email_content = json.load(f)
                        unprocessed_emails.append(email_content)
                except Exception as e:
                    print(f"Error loading email from {file}: {e}")
        
        print(f"\nFound {len(unprocessed_emails)} unprocessed emails")
        return unprocessed_emails

    def generate_response(self, email_content):
        """Generate AI response using OpenAI Assistant."""
        try:
            if not ASSISTANT_ID:
                raise Exception("OPENAI_ASSISTANT_ID not found in environment variables")

            # Create a thread
            thread = self.client.beta.threads.create()

            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=
                        f"From: {email_content['sender']}\n"
                        f"Subject: {email_content['subject']}\n"
                        f"Message: {email_content['body']}"
            )

            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID
            )

            # Wait for completion
            while True:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                if run.status == 'completed':
                    break
                elif run.status in ['failed', 'cancelled', 'expired']:
                    raise Exception(f"Assistant run failed with status: {run.status}")
                time.sleep(1)

            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            for message in messages.data:
                if message.role == "assistant":
                    response_content = message.content[0].text.value
                    self.save_response(email_content, response_content)
                    
                    # Preview the response
                    print("\nGenerated Response:")
                    print("-" * 50)
                    print(response_content)
                    print("-" * 50)
                    
                    return response_content

            return None
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def save_response(self, email_content, response_content):
        """Save the generated response to a file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_response_{email_content['id']}.json"
            filepath = os.path.join(self.emails_to_send_dir, filename)

            response_data = {
                'email_id': email_content['id'],
                'thread_id': email_content['thread_id'],
                'original_email': {
                    'sender': email_content['sender'],
                    'subject': email_content['subject'],
                    'body': email_content['body'],
                    'message_id': email_content.get('message_id', '')  # Include Message-ID
                },
                'response': response_content,
                'timestamp': timestamp
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)

            self.processed_email_ids.add(email_content['id'])
            print(f"Saved response to {filepath}")
            return True
        except Exception as e:
            print(f"Error saving response: {e}")
            return False

    def process_pending_emails(self):
        """Process all pending emails and generate responses."""
        unprocessed_emails = self.get_unprocessed_emails()
        response_count = 0
        
        for email in unprocessed_emails:
            print(f"\nProcessing email from: {email['sender']}")
            print(f"Subject: {email['subject']}")
            response = self.generate_response(email)
            if response:
                print("Successfully generated and saved response")
                response_count += 1
            else:
                print("Failed to generate response")
        
        return response_count
