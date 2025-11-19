from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import base64
import json

# Scope d'accès pour lire les e-mails
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Authentification avec l'API Gmail
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    # Le fichier token.json stocke les jetons d'accès et de rafraîchissement de l'utilisateur, et est
    # créé automatiquement lorsque le flux d'autorisation se termine pour la première
    # fois.
    if os.path.exists('token.json'):
        with open('token.json', 'r') as token:
           creds_dict = json.load(token)
           creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)


    # Si aucune information d'identification (valide) n'est disponible, laissez l'utilisateur se connecter.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=1909)
        # Enregistrez les informations d'identification pour la prochaine exécution
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# Fonction pour télécharger les pièces jointes PDF
def download_attachments(service, user_id='me', query='has:attachment filename:pdf'):
    # Récupère les e-mails correspondant à la requête
    results = service.users().messages().list(userId=user_id, q=query).execute()
    messages = results.get('messages', [])
    print(f"Nombre d'emails trouvés : {len(messages)}")

    for msg in messages:
        msg_data = service.users().messages().get(userId=user_id, id=msg['id']).execute()
        for part in msg_data['payload'].get('parts', []):
            if part['filename'] and 'application/pdf' in part['mimeType']:
                data = part['body'].get('data')
                if not data:
                    data = service.users().messages().attachments().get(
                        userId=user_id, messageId=msg['id'], id=part['body']['attachmentId']).execute()['data']
                file_data = base64.urlsafe_b64decode(data)
                file_path = os.path.join("downloads", part['filename'])
                os.makedirs("downloads", exist_ok=True)
                with open(file_path, 'wb') as f:
                    f.write(file_data)
                print(f"PDF téléchargé : {file_path}")

# Main
if __name__ == '__main__':
    gmail_service = authenticate_gmail()
    download_attachments(gmail_service, query='has:attachment filename:pdf subject:(DHL)')