import gspread

gc = gspread.service_account(
    filename="credentials/google-service-account.json"
)


def get_cell(cell_address):
    spreadsheet = gc.open_by_key("1xcW9QAXzRXV-KnTLkmffDGBKRgFYhVIO1ggpOAhWHmk")
    worksheet = spreadsheet.worksheet("Postacie")
    cell = worksheet.acell(cell_address)
    data = worksheet.get_all_values()

    character_index = None

    for row in data:
        if row[0] == "Imię":
            character_index = row.index("Dwalgin")
            break

    for row in data:
        print(row[0], row[character_index])

    return cell.value


value = get_cell("B27")
print("AAAAAAAAAAAAAAAAA")
print(value)
