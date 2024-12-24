import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import dotenv
from google.oauth2.credentials import Credentials

# Load environment variables
dotenv.load_dotenv()

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_credentials_from_env():
    """Get credentials from environment variables (for CI/CD)."""
    try:
        creds_json = os.getenv('GMAIL_CREDENTIALS_JSON')
        if not creds_json:
            return None
        
        creds_data = json.loads(creds_json)
        return Credentials.from_authorized_user_info(creds_data, SCOPES)
    except Exception as e:
        print(f"Error loading credentials from environment: {e}")
        return None

def get_gmail_service():
    """Authenticate and create Gmail service."""
    creds = None
    
    # First try to load from token.pickle
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, try environment variables
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Try to get credentials from environment first
            creds = get_credentials_from_env()
            
            # If no env credentials, try local file
            if not creds:
                credentials_path = os.path.join('credentials', 'creds_google.json')
                if not os.path.exists(credentials_path):
                    raise Exception(f"Google credentials not found in environment or at: {credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)
