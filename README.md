# AI Email Auto-Responder

An intelligent email automation system that handles incoming emails with AI-powered responses.

## Setup Instructions

1. Create a `.env` file with the following variables (use `.env.template` as reference):
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
   - Download the credentials JSON and place it in the `credentials` directory
   - Set the path in `.env`

4. Run the auto-responder:
   ```
   python auto_email_responder.py
   ```

## Project Structure

- `auto_email_responder.py`: Main script that orchestrates the email response workflow
- `ai_generator.py`: Handles AI-powered response generation using OpenAI
- `email_handler.py`: Core email processing and management functionality
- `email_sender.py`: Handles composing and sending email responses
- `gmail_service.py`: Gmail API integration and authentication
- `cleanup_util.py`: Utility for cleaning up temporary files and managing storage
- `run_pipeline.py`: Script to run the complete email processing pipeline

## Features
- Checks Gmail for emails under a specific label
- Uses OpenAI to draft intelligent responses
- Automatically sends formatted replies
- Manages email attachments and threading
- Handles OAuth authentication securely
- Cleans up temporary files automatically

## Directory Structure
- `Emails_Received/`: Storage for downloaded email content
- `Emails_To_Send/`: Queue directory for outgoing emails
- `credentials/`: Directory for Gmail API credentials (gitignored)
- `token.pickle`: Gmail API authentication token (gitignored)

## Security Note
Sensitive files like `credentials/` directory and `token.pickle` are automatically excluded from git tracking for security. Make sure to back these up separately.
