from utils.service_account import ServiceAccount

from dotenv import load_dotenv
import os


def run():
    sa = ServiceAccount(
        spreadsheetName=os.getenv("SPREADSHEET_NAME"),
        folderId=os.getenv("FOLDER_ID"),
        testedFilesOnly=True,
    )
    print("Updating gsheet with json...")
    sa.update_all_values()
    sa.update_worksheet_colors()
    print("Updating complete!")


if __name__ == "__main__":
    """
    Basically this file is purposed to execute the results.json file (located on root), which contains the test result of the last test execution. This action is taken regarding to avoid 2 main problems, i.e. request limit and unexpected error during the gsheet upgrade process.
    """

    load_dotenv()
    run()
