import json
import os
from functools import lru_cache
from pathlib import Path

import gspread
from google.oauth2.service_account import Credentials

from config.settings import PROJECT_ROOT


WORKSHEET_NAME = "Postacie"

ID_ROW_LABELS = {
    "discord id",
    "id",
}

LIST_SECTIONS = {
    "Umiejętności",
    "Monety",
    "Zdolności",
    "Ekwipunek",
    "Broń",
    "Pancerz",
    "Magia",
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


class GoogleSheetsConfigurationError(RuntimeError):
    pass


class CharacterNotLinkedError(LookupError):
    pass


class CharacterNotFoundError(LookupError):
    pass


class CharacterSheetFormatError(RuntimeError):
    pass


def clean(value: str) -> str:
    return value.strip()


def _build_client():
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if service_account_json:
        try:
            credentials_info = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise GoogleSheetsConfigurationError(
                "GOOGLE_SERVICE_ACCOUNT_JSON nie jest poprawnym JSON-em."
            ) from exc

        credentials = Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )

        return gspread.authorize(credentials)

    credentials_path_raw = os.getenv(
        "GOOGLE_CREDENTIALS_PATH",
        "credentials/google-service-account.json",
    )

    credentials_path = Path(credentials_path_raw)

    if not credentials_path.is_absolute():
        credentials_path = PROJECT_ROOT / credentials_path

    if not credentials_path.exists():
        raise GoogleSheetsConfigurationError(
            f"Nie znaleziono credentials: {credentials_path}"
        )

    credentials = Credentials.from_service_account_file(
        str(credentials_path),
        scopes=SCOPES,
    )

    return gspread.authorize(credentials)


@lru_cache(maxsize=1)
def _get_worksheet():
    sheet_id = os.getenv("GOOGLE_SHEET_ID")

    if not sheet_id:
        raise GoogleSheetsConfigurationError(
            "Brakuje GOOGLE_SHEET_ID."
        )

    client = _build_client()
    spreadsheet = client.open_by_key(sheet_id)

    return spreadsheet.worksheet(WORKSHEET_NAME)


def _find_row(data: list[list[str]], label: str) -> list[str]:
    searched_label = label.strip().casefold()

    for row in data:
        if not row:
            continue

        if clean(row[0]).casefold() == searched_label:
            return row

    raise CharacterSheetFormatError(
        f"Nie znaleziono wiersza '{label}' w arkuszu."
    )


def find_character_index_by_discord_id(
    data: list[list[str]],
    discord_user_id: int,
) -> int:
    searched_id = str(discord_user_id)

    for label in ID_ROW_LABELS:
        try:
            row = _find_row(data, label)
        except CharacterSheetFormatError:
            continue

        for index, value in enumerate(row[1:], start=1):
            if clean(value) == searched_id:
                return index

        raise CharacterNotLinkedError(
            f"Discord ID {discord_user_id} nie ma przypisanej postaci."
        )

    raise CharacterSheetFormatError(
        "Nie znaleziono wiersza Discord ID w arkuszu."
    )


def find_character_index_by_name(
    data: list[list[str]],
    character_name: str,
) -> int:
    row = _find_row(data, "Imię")

    searched_name = character_name.strip().casefold()

    for index, value in enumerate(row[1:], start=1):
        if clean(value).casefold() == searched_name:
            return index

    raise CharacterNotFoundError(
        f"Nie znaleziono postaci: {character_name}"
    )


def _build_character_data(
    data: list[list[str]],
    character_index: int,
) -> dict:
    character_data = {}
    current_list_section = None

    for row in data:
        if not row:
            continue

        if character_index >= len(row):
            continue

        label = clean(row[0])
        value = clean(row[character_index])

        if label.casefold() in ID_ROW_LABELS:
            continue

        if label:
            if label in LIST_SECTIONS:
                current_list_section = label
                character_data[label] = []

                if value:
                    character_data[label].append(value)

                continue

            current_list_section = None

            if value:
                character_data[label] = value

            continue

        if current_list_section and value:
            character_data[current_list_section].append(value)

    return character_data


def get_character_by_discord_id(discord_user_id: int) -> dict:
    data = _get_worksheet().get_all_values()

    character_index = find_character_index_by_discord_id(
        data,
        discord_user_id,
    )

    return _build_character_data(
        data,
        character_index,
    )


def get_character_by_name(character_name: str) -> dict:
    data = _get_worksheet().get_all_values()

    character_index = find_character_index_by_name(
        data,
        character_name,
    )

    return _build_character_data(
        data,
        character_index,
    )