from email_handler import EmailHandler
from ai_generator import generate_ai_response

class EmailResponder:
    def __init__(self):
        self.email_handler = EmailHandler()

    def process_emails(self):
        """Main method to process emails."""
        emails = self.email_handler.get_emails_by_label()
        
        for email in emails:
            # Get full email content
            email_details = self.email_handler.get_email_content(email['id'])
            
            if email_details:
                # Generate AI response
                ai_response = generate_ai_response(email_details['body'])
                
                if ai_response:
                    # Send the AI-generated response
                    self.email_handler.send_email(
                        to=email_details['sender'], 
                        subject=email_details['subject'], 
                        body=ai_response
                    )

def main():
    responder = EmailResponder()
    responder.process_emails()

if __name__ == '__main__':
    main()