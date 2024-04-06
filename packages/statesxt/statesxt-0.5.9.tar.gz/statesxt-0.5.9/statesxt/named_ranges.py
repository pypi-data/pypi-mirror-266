from dotenv import load_dotenv
import gspread
import os

load_dotenv()


class NamedRanges:
    def __init__(self) -> None:
        self.spreadsheetName = os.getenv("SPREADSHEET_NAME")
        self.sa = gspread.service_account()
        self.ss = self.sa.open(self.spreadsheetName)
        self.ansi = {
            "error": "\033[91m\033[1m",
            "info": "\033[94m",
            "success": "\u001b[32m",
            "warn": "\u001b[33m",
            "reset": "\033[0m",
        }
        self.optX = lambda oriColor, opt: f"[{self.ansi['success']}{opt}{self.ansi[oriColor]}]: {self.ansi['reset']}"
        self.obj = lambda obj: f"'{obj}'"

    def opt(self, oriColor: str, *args) -> str:
        if args:
            printed = "("
            for arg in args:
                printed += f"{self.ansi['success']}{arg}{self.ansi[oriColor]}/"

            printed = printed.rsplit("/", 1)
            printed = "".join(printed)
            printed += ")"

            return printed

    def WrongOpt(self, opt, obj="option"):
        print(f"{nr.ansi['error']}There is no such '{opt}' {obj}{nr.ansi['reset']}")

    def Warn(self):
        ans = (
            str(
                input(
                    f"{self.ansi['warn']}Warning: Once the process finished, the action can't be undone!! Are you sure you want to proceed? {self.opt('warn', 'yes', 'no')} {self.optX('warn', 'no')}"
                )
            )
            .lower()
            .strip()
        )
        print()
        return True if ans in ["yes", "y", "true", "t"] else False

    def getNamedRanges(self):
        # Retrieve the named ranges
        named_ranges = self.ss.list_named_ranges()
        nonr = len(named_ranges)
        print(f"{self.ansi['info']}In total, there {'are ' + str(nonr) + ' named ranges' if nonr > 1 else 'is 1 named range'}")
        if nonr:
            print(f"{self.ansi['info']}Example: {self.ansi['reset']}{named_ranges[0]}")
        print()
        return named_ranges

    def create(self):
        if self.Warn():
            named_ranges = self.getNamedRanges()
            named_range_names = [str(named_range["name"]) for named_range in named_ranges]

            worksheet = None
            while not worksheet:
                I = str(input(f"{self.ansi['info']}Input the worksheet name: {self.ansi['reset']}"))
                try:
                    worksheet = self.ss.worksheet(I)
                except Exception:
                    self.WrongOpt(I, "worksheet")
                    worksheet = None

            nonr = input(f"{self.ansi['info']}How many scenarios do you want to create the named ranges? (max: 999) {self.optX('info', '1')}")
            nonr = int(nonr) if nonr else 1
            nonr = nonr if nonr <= 999 else 999

            start = input(f"{self.ansi['info']}What is the first scenario? {self.optX('info', '1')}")
            start = int(start) if start else 1

            print(f"\n{self.ansi['info']}Processing: {self.ansi['reset']}")

            requests = []
            for i in range(start, nonr + start):
                iter_name = str(i).zfill(3)
                for j in ["Data", "Form"]:
                    name = f"_SN_{I.replace('-', '').replace('.', '_')}_Scenario_{iter_name}_{j}"
                    if name not in named_range_names:
                        print(f"{self.ansi['info']}- {name}{self.ansi['reset']}")
                        requests.append(
                            {
                                "addNamedRange": {
                                    "namedRange": {
                                        "name": name,
                                        "range": {
                                            "sheetId": worksheet.id,
                                            "startRowIndex": 0,
                                            "endRowIndex": 10,
                                            "startColumnIndex": 0,
                                            "endColumnIndex": 2,
                                        },
                                    }
                                }
                            }
                        )

            # Execute the batch update request
            if requests:
                self.ss.batch_update({"requests": requests})

            print(f"\n{self.ansi['success']}Creating finished with {len(requests)} has/have been processed. {self.ansi['reset']}")

    def delete(self):
        if self.Warn():
            named_ranges = self.getNamedRanges()
            named_range_names = [str(named_range["name"]) for named_range in named_ranges]
            opt = (
                str(
                    input(
                        f"{self.ansi['info']}Do you want to input the named ranges manually one by one or by words filter? {self.opt('info', 'manual', 'filter')} {self.optX('info', 'filter')}"
                    )
                )
                .lower()
                .strip()
            )
            opt = opt if opt else "filter"
            requests = []

            # Select the named ranges
            if opt == "manual":
                nrs = []
                while nr := str(input(f"{self.ansi['info']}Input the named range name (left it blank to stop inputting): {self.ansi['reset']}")).strip():
                    if nr in named_range_names:
                        nrs.append(nr)
                    else:
                        self.WrongOpt(nr, "named range")
                nrs = list(dict.fromkeys(nrs))
            elif opt == "filter":
                search = str(input(f"{self.ansi['info']}Input the word to be used for filtering: {self.ansi['reset']}")).lower().strip()
                nrs = list(filter(lambda x: search in x.lower(), named_range_names))
            else:
                self.WrongOpt(opt)
                return

            print(f"\n{self.ansi['info']}Processing: {self.ansi['reset']}")

            for nr in nrs:
                named_range = named_ranges[named_range_names.index(nr)]
                print(f"{self.ansi['info']}- {named_range['name']}{self.ansi['reset']}")
                request = {
                    "deleteNamedRange": {
                        "named_range_id": named_range["namedRangeId"],
                    },
                }
                requests.append(request)

            # Execute the batch update request
            if requests:
                self.ss.batch_update({"requests": requests})

            print(f"\n{self.ansi['success']}Deleting finished with {len(requests)} has/have been processed. {self.ansi['reset']}")

    def rename(self):
        if self.Warn():
            # Retrieve the named ranges
            named_ranges = self.getNamedRanges()
            named_range_names = [str(named_range["name"]) for named_range in named_ranges]

            # filter
            search = str(input(f"{self.ansi['info']}Input the word to be replaced: {self.ansi['reset']}"))
            replace = str(input(f"{self.ansi['info']}Input the replace: {self.ansi['reset']}"))
            nrs = list(filter(lambda x: search in x, named_range_names))

            print(f"\n{self.ansi['info']}Processing: {self.ansi['reset']}")

            # Iterate through the named ranges and update if needed
            requests = []
            for nr in nrs:
                named_range = named_ranges[named_range_names.index(nr)]
                print(f"{self.ansi['info']}- {named_range['name']}{self.ansi['reset']}")
                request = {
                    "updateNamedRange": {
                        "namedRange": {
                            "named_range_id": named_range["namedRangeId"],
                            "name": str(named_range["name"]).replace(search, replace),
                            "range": {
                                "sheetId": named_range["range"]["sheetId"],
                                "startRowIndex": named_range["range"]["startRowIndex"],
                                "endRowIndex": named_range["range"]["endRowIndex"],
                                "startColumnIndex": named_range["range"]["startColumnIndex"],
                                "endColumnIndex": named_range["range"]["endColumnIndex"],
                            },
                        }
                    }
                    | {"fields": "*"},
                }
                requests.append(request)

            # Execute the batch update request
            if requests:
                self.ss.batch_update({"requests": requests})

            print(f"\n{self.ansi['success']}Renaming finished with {len(requests)} has/have been processed. {self.ansi['reset']}")


if __name__ == "__main__":
    """
    This file is used to automatically handle named ranges, e.g. rename, and delete all named ranges automatically
    """

    nr = NamedRanges()

    # ask for the task option
    default_task = "create"
    inputted_task = str(input(f"{nr.ansi['info']}What task you want to do? {nr.opt('info', 'create', 'delete', 'rename')} {nr.optX('info', 'create')}")).lower().strip()
    task = inputted_task if inputted_task else default_task

    # do the task
    if task == "create":
        nr.create()
    elif task == "delete":
        nr.delete()
    elif task == "rename":
        nr.rename()
    else:
        nr.WrongOpt(task)
