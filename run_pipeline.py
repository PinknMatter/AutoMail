from email_handler import EmailHandler
from ai_generator import AIGenerator
from email_sender import EmailSender
from cleanup_util import CleanupUtil
import time

def main():
    print("\n=== Starting Email Processing Pipeline ===\n")
    
    # Step 1: Fetch new emails
    print("Step 1: Fetching new emails...")
    handler = EmailHandler()
    emails = handler.process_unread_emails()
    print(f"Found and processed {len(emails)} new emails\n")
    
    # Step 2: Generate AI responses
    print("Step 2: Generating AI responses...")
    generator = AIGenerator()
    num_responses = generator.process_pending_emails()
    print(f"Generated {num_responses} responses\n")
    
    # Step 3: Send responses
    print("Step 3: Sending responses...")
    sender = EmailSender()
    num_sent = sender.process_pending_responses()
    print(f"Sent {num_sent} responses\n")
    
    # Step 4: Cleanup
    print("Step 4: Cleaning up...")
    cleanup = CleanupUtil()
    
    # Delete processed emails and responses
    cleanup.cleanup_processed_files('Emails_Received', 'Emails_To_Send')
    
    # Remove test files
    cleanup.cleanup_test_files()
    
    print("\n=== Pipeline Complete ===")

if __name__ == '__main__':
    main()
