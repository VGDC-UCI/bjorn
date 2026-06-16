# sheets.py
# Google Sheets data access layer

import json
import os

import gspread
from google.oauth2.service_account import Credentials


def get_workshops():
	raw = os.getenv('GOOGLE_CREDENTIALS')
	if not raw:
		raise RuntimeError("GOOGLE_CREDENTIALS environment variable is not set")
	creds_json = json.loads(raw)
	creds = Credentials.from_service_account_info(creds_json, scopes=[
		"https://www.googleapis.com/auth/spreadsheets.readonly",
		"https://www.googleapis.com/auth/drive.readonly"
	])
	gc = gspread.authorize(creds)
	sheet = gc.open("[VGDC Workshop Database (Officers)]").get_worksheet(1)
	return sheet.get_all_records(head=2)
