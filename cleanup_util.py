import os
import shutil
from datetime import datetime

class CleanupUtil:
    def cleanup_processed_files(self, emails_received_dir, emails_sent_dir):
        """Delete processed emails and their responses."""
        try:
            # Delete processed emails
            for file in os.listdir(emails_received_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(emails_received_dir, file)
                    os.remove(file_path)
                    print(f"Deleted processed email: {file}")

            # Delete sent responses and pending responses
            # First delete files in the root of emails_sent_dir
            for file in os.listdir(emails_sent_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(emails_sent_dir, file)
                    os.remove(file_path)
                    print(f"Deleted pending response: {file}")

            # Then delete files in the Sent subdirectory
            sent_dir = os.path.join(emails_sent_dir, 'Sent')
            if os.path.exists(sent_dir):
                for file in os.listdir(sent_dir):
                    if file.endswith('.json'):
                        file_path = os.path.join(sent_dir, file)
                        os.remove(file_path)
                        print(f"Deleted sent response: {file}")

            print("Successfully cleaned up processed files")
            return True
        except Exception as e:
            print(f"Error cleaning up files: {e}")
            return False

    def cleanup_test_files(self):
        """Remove test files from the project directory."""
        test_files = [
            'test_email_sender.py',
            'test_fetch_emails.py',
            'test_ai_generator.py',
            'test_auth.py',
            'list_labels.py'
        ]
        
        for file in test_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
                    print(f"Removed test file: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")
