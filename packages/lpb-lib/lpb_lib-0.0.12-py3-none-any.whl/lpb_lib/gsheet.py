from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from lpb_lib import compute_log as log
      
def API_GOOGLE_SHEET_UPDATE_LINES(account_google_secret, google_sheet_id, df, sheet_name="Sheet1", range = "A1:ZZ"):
    """
        Fonction permettant de mettre à jour un onglet Google Sheet avec un dataframe
        Args
            account_google_secret: str, chemin vers le fichier secret de l'API Google
            google_sheet_id: str, identifiant de la feuille Google
            sheet_name: str, nom de l'onglet à mettre à jour. default: "Sheet1"
            range: str, plage de cellules à mettre à jour. default: "A1:ZZ"
            df: DataFrame, dataframe à mettre à jour

        Returns
            None
    """
    

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = account_google_secret
    creds = None
    creds = service_account.Credentials.from_service_account_file(
			SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    
    spreadsheet_id = google_sheet_id
    sheet_name = sheet_name
    
    service = build('sheets', 'v4', credentials=creds)

    clear_request = service.spreadsheets().values().clear(
    spreadsheetId=spreadsheet_id,
    range=f'{sheet_name}!{range}',
)
    clear_response = clear_request.execute()

    # Conversion du dataframe en liste de listes
    header = list(df.columns)
    data = df.values.tolist()
    data.insert(0, header)

    #range_name = f'{sheet_name}!A1:{chr(ord("A") + df.shape[1] - 1)}{df.shape[0] + 1}'
    range_name = f'{sheet_name}!{range}'

    try:
        request = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body={'values': data}
        )

        response = request.execute()

        header = "API_GOOGLE_SHEET_UPDATE_LINES"
        msg = f"""
            Id Gsheet:\t\t{response['spreadsheetId']}
            Range:\t\t{response['updatedRange']}
            Row updated:\t\t{response['updatedRows']}
            Column updated:\t{response['updatedColumns']}
            Cells updated:\t{response['updatedCells']}
                """
        footer = "Fin de l'execution de la fonction"
        log.computelog(header, msg, footer)
    except HttpError as error:
        print(f"An error occurred: {error}")

def API_GOOGLE_SHEET_GET_FILE (account_google_secret, google_sheet_id, sheet_name = "Sheet1", range = "A1:ZZ"):
    """
    Fonction permettant de récupérer les données d'un onglet Google Sheet
    Args
        account_google_secret: str, chemin vers le fichier secret de l'API Google
        google_sheet_id: str, identifiant de la feuille Google
        sheet_name: str, nom de l'onglet à récupérer. default : "Sheet1"
        range: str, plage de cellules à récupérer. default : "A1:ZZ"
    Returns
        values: list, liste des valeurs récupérées
    """
    
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = account_google_secret
    creds = None
    creds = service_account.Credentials.from_service_account_file(
			SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    SAMPLE_SPREADSHEET_ID = google_sheet_id
    range_name=f'{sheet_name}!{range}'
    SAMPLE_RANGE_NAME = range_name
    
    try:
        service = build('sheets', 'v4', credentials=creds)
		# Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
								range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        print(f"{datetime.now()}\tExecution OK !")
        header_log = "API_GOOGLE_SHEET_GET_FILE"
        msg_log = f"{datetime.now()}\tExecution OK !\n {len(values)} lignes récupérées\n {values[0]} extrait header"
        footer_log = "Fin de l'execution de la fonction"
        log.computelog(header_log, msg_log, footer_log)
        return values
    except HttpError as error:
        print(f"An error occurred: {error}")