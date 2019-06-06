import liteconfig
from fs.googledrivefs import GoogleDriveFS
from google.oauth2.credentials import Credentials
from requests_oauthlib import OAuth2Session


class GoogleDrive:
    """GoogleDrive instance"""
    def __init__(self, creds_file):
        creds = liteconfig.Config(creds_file)
        oauth = Credentials(creds.access_token,
                            refresh_token=creds.refresh_token,
                            token_uri=creds.token_uri,
                            client_id=creds.client_id,
                            client_secret=creds.client_secret)
        self.worker = GoogleDriveFS(oauth)


if __name__ == "__main__":
    """
    If there is no Google Drive credentials file in 'mediums' folder, run this script and follow the instructions. 
    """
    console_url = "https://console.developers.google.com/cloud-resource-manager"
    dashboard_url = "https://console.developers.google.com/apis/dashboard"
    print(f'We have to authorize this application to Google, so it can use your GoogleDrive.'
          f'1) Go to console ({console_url}) and create a project.'
          f'2) Go to API dashboard ({dashboard_url}) and turn on Google Drive API.'
          f'3) Return to dashboard and go to "Credentials", "OAuth consent screen", enter "Application name" and save.'
          f'4) Return to "Credentials" and click "Create credentials", "OAuth client ID".'
          f'5) Choose application type "other" and enter application name. You will get client ID and client secret!')
    client_id = input("Paste client ID here:")
    client_secret = input("Paste client secret here:")
    authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    scope = "https://www.googleapis.com/auth/drive"
    session = OAuth2Session(client_id=client_id, scope=scope, redirect_uri="https://localhost")
    authorization_url, _ = session.authorization_url(authorization_base_url, access_type="offline")
    print(f"Go to the following URL and authorize the app. When you'll authorize it, your browser will"
          f"try to redirect you to https://localhost?state=BLABLABLA page. It will fail, of course, because"
          f"such an URL your computer does not serve. Please copy it and paste a moment later: {authorization_url}")
    redirectResponse = input("Paste the full redirect URL here:")
    tokenUrl = "https://oauth2.googleapis.com/token"
    token = session.fetch_token(tokenUrl, client_secret=client_secret, authorization_response=redirectResponse)

    if 'access_token' in token.keys() and 'refresh_token' in token.keys():
        print("Everything seems to be OK! Credentials are saved to 'mediums/googledrive-credentials' file."
              "Please make sure you save this in your .ini file in section 'upload' under 'creds' keyword, like"
              "creds = mediums/googledrive-credentials")
        cfg = [f"token_uri = https://www.googleapis.com/oauth2/v4/token",
               f"client_id = {client_id}",
               f"client_secret = {client_secret}",
               f"access_token = {token['access_token']}",
               f"refresh_token = {token['refresh_token']}"]
        google_creds = liteconfig.Config(cfg)
        google_creds.write('googledrive-credentials')
    else:
        print("Something went wrong. Try again, and if problem persists, please contact developer.")
