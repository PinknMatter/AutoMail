# AI Email Auto-Responder

## Setup Instructions

1. Create a `.env` file with the following variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `GMAIL_CREDENTIALS_PATH`: Path to your Gmail OAuth credentials JSON

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Gmail API:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download the credentials JSON and set the path in `.env`

4. Run the auto-responder:
   ```
   python auto_email_responder.py
   ```

## Features
- Checks Gmail for emails under a specific label
- Uses OpenAI to draft intelligent responses
- Automatically sends formatted replies
