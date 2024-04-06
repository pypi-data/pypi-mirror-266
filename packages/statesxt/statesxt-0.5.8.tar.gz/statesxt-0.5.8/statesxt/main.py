import argparse
import shutil
import os


class StateSXT:
    def __init__(self) -> None:
        self.tree = [
            ".github",
            "base",
            "database",
            "testcases",
            "utils",
            ".env.template",
            ".gitignore",
            "named_ranges.py",
            "restate.py",
            "results.json",
            "pyproject.toml",
            "pytest.ini",
            "README.md",
            "tox.ini",
        ]
        self.deprs = {
            rf"testcases\_fixtures\login_fixture.py": rf"testcases\_fixtures\auth.py",
            rf"testcases\_fixtures\composition_fixture.py": rf"testcases\_fixtures\composition.py",
            rf"testcases\_fixtures\option_fixture.py": rf"testcases\_fixtures\option.py",
            rf"utils\explicit_wait.py": rf"utils\explicit.py",
            rf"utils\gsheet.py": rf"utils\service_account.py",
            rf".env-template": rf".env.template",
            rf"rename_named_ranges.py": rf"named_ranges.py",
            rf"execute_json.py": rf"restate.py",
            rf"retry.py": rf"restate.py",
            rf"track.json": rf"results.json",
            rf"last_run_data.json": rf"results.json",
            rf"testcases\fixtures": rf"testcases\_fixtures",
        }

        self.sourcedir = os.path.dirname(os.path.realpath(__file__))
        self.destdir = os.getcwd()
        self.destdirname = self.destdir.split("\\")[-1]
        self.ansi = {
            "error": "\033[91m\033[1m",
            "info": "\033[94m",
            "success": "\u001b[32m",
            "warn": "\u001b[33m",
            "bold": "\033[1m",
            "reset": "\033[0m",
            "underline": "\033[4m",
        }
        self.name = "StateSXT"
        self.optX = lambda oriColor, opt: f"[{self.ansi['success']}{opt}{self.ansi[oriColor]}]: {self.ansi['reset']}"
        self.opt1 = lambda oriColor, opt: f"({self.ansi['success']}{opt}{self.ansi[oriColor]})"
        self.opt2 = lambda oriColor, opt1, opt2: f"({self.ansi['success']}{opt1}{self.ansi[oriColor]}/{self.ansi['success']}{opt2}{self.ansi[oriColor]})"
        self.obj = lambda obj: f"'{obj}'"

    def toConfirm(self, input: input, adds: list[str] = []) -> bool:
        val = str(input).lower()
        res = True if (val in ["yes", "y"]) else False
        if adds:
            res = val if (val in adds) else res
        return res

    def warnVC(self) -> bool:
        print(
            f"\u2757{self.ansi['warn']} Before continuing the process, it is recommended that you have installed your project with a version control, e.g. Git/Github. This is to prevent your files/folders from being completely lost. {self.ansi['reset']}"
        )
        return self.toConfirm(input(f"\u2757{self.ansi['warn']} Do you want to proceed? {self.opt2('warn', 'yes', 'no')} {self.optX('warn', 'no')}"))

    def formatPath(self, path_name: str, isLower: bool = True, isName: bool = False) -> str:
        if isLower:
            path_name = path_name.lower()

        path_name = path_name.split("\\")[0].split("/")[0].strip()
        if not isName:
            path_name = path_name.replace(" ", "_")

        return path_name

    def getType(self, path: str, doWarn: bool = True) -> str | None:
        if any(type := [os.path.isdir(path), os.path.isfile(path)]):  # condition: when the folder/file already exists
            if type[0]:
                ptype = "folder"
            elif type[1]:
                ptype = "file"
            if doWarn:
                p = path.split("\\")[-1]
                print(f"{self.ansi['warn']}{ptype.capitalize()} {self.obj(p)} already exists{self.ansi['reset']}")
            return ptype

    def generate(self):
        print()
        rate = 0
        for p in self.tree:
            sourcepath = os.path.join(self.sourcedir, p)
            destpath = os.path.join(self.destdir, p)

            # generate the file/folder
            if self.getType(destpath):  # condition: when the folder/file already exists
                pass
            elif os.path.isdir(sourcepath):  # condition: when it's a folder
                shutil.copytree(sourcepath, destpath)
                rate += 1
            elif os.path.isfile(sourcepath):  # condition: when it's a file
                shutil.copy2(sourcepath, destpath)
                rate += 1
            else:  # condition: when the path does not exist
                print(f"{self.ansi['warn']}Path {self.obj(p)} does not exist{self.ansi['reset']}")

        # summary
        if rate == len(self.tree):
            print(f"{self.ansi['success']}All templates created in {self.obj(self.destdir)}{self.ansi['reset']}")
        elif rate == 1:
            print(f"\n{self.ansi['success']}A template created in {self.obj(self.destdir)}{self.ansi['warn']}, but {len(self.tree)-rate} failed.{self.ansi['reset']}")
        elif rate >= 1:
            print(f"\n{self.ansi['success']}{rate} templates created in {self.obj(self.destdir)}{self.ansi['warn']}, but {len(self.tree)-rate} failed.{self.ansi['reset']}")
        else:
            print(f"\n{self.ansi['error']}All templates failed to create in {self.obj(self.destdir)}{self.ansi['reset']}")

    def remove(self):
        isProceeded = self.warnVC()

        print()
        if isProceeded:
            rate = 0
            for p in self.tree:
                destpath = os.path.join(self.destdir, p)

                # remove the file/folder
                if os.path.isdir(destpath):  # condition: when it's a folder
                    shutil.rmtree(destpath)
                    rate += 1
                elif os.path.isfile(destpath):  # condition: when it's a file
                    os.remove(destpath)
                    rate += 1
                else:  # condition: when the path does not exist
                    print(f"{self.ansi['warn']}Path {self.obj(p)} does not exist{self.ansi['reset']}")

            # summary
            if rate == len(self.tree):
                print(f"{self.ansi['success']}All templates removed from {self.obj(self.destdir)}{self.ansi['reset']}")
            elif rate == 1:

                print(
                    f"\n{self.ansi['success']}{rate}A template has been removed from {self.obj(self.destdir)}{self.ansi['warn']}, but {len(self.tree)-rate} failed.{self.ansi['reset']}"
                )
            elif rate > 1:
                print(
                    f"\n{self.ansi['success']}{rate} templates have been removed from {self.obj(self.destdir)}{self.ansi['warn']}, but {len(self.tree)-rate} failed.{self.ansi['reset']}"
                )
            else:
                print(f"\n{self.ansi['error']}All templates failed to remove from {self.obj(self.destdir)}{self.ansi['reset']}")

    def update(self):
        isProceeded = self.warnVC()

        print()
        if isProceeded:
            # deep-loop over self.tree and gather the choices
            choices = []
            defaultSkippedSub = "C:\\"
            skippedSub = defaultSkippedSub
            for destpath, dirs, files in os.walk(self.destdir):
                sub = str(destpath).split(self.destdir + "\\")[-1] if (destpath != self.destdir) else ""
                subSplits = sub.split("\\")
                pathname = subSplits[-1]
                depth = len(subSplits) - 1

                if (skippedSub not in sub) or (skippedSub not in subSplits):
                    isRenamed = sub in self.deprs
                    if (os.path.exists(os.path.join(self.sourcedir, sub)) or isRenamed) and (
                        sub != ""
                    ):  # condition: check if the folder exists in source, and asking update to folder
                        updateOpt = self.toConfirm(
                            input(
                                " \u27b1 " * depth
                                + f"\u2753{self.ansi['info']} Do you want to update folder {self.obj(sub)} entirely? {self.opt2('info', 'yes', 'no')} or selectively? {self.opt1('info', 'select')} {self.optX('info', 'no')}"
                            ),
                            adds=["select"],
                        )
                        skippedSub = (
                            sub if (updateOpt != "select") else defaultSkippedSub
                        )  # if updateOpt is not 'select' then the next iteration will not check the files/folders within
                        if updateOpt == True:
                            choices.append([self.deprs[sub] if isRenamed else sub, "folder", sub if isRenamed else None])

                    if (skippedSub not in sub) and (skippedSub not in subSplits):  # condition: when updateOpt tells to update folder entirely
                        for file in files:  # condition: loop over files within destpath, and asking update to files
                            pathname = file
                            pSub = os.path.join(sub, pathname)
                            psubSplits = pSub.split("\\")
                            depth = len(psubSplits) - 1
                            isRenamed = pSub in self.deprs
                            if os.path.exists(os.path.join(self.sourcedir, pSub)) or isRenamed:  # condition: check if the file exists in source
                                updateOpt = self.toConfirm(
                                    input(
                                        " \u27b1 " * depth
                                        + f"\u2753{self.ansi['info']} Do you want to update file {self.obj(pSub)}? {self.opt2('info', 'yes', 'no')} {self.optX('info', 'no')}"
                                    ),
                                )
                                if updateOpt:
                                    choices.append([self.deprs[pSub] if isRenamed else pSub, "file", pSub if isRenamed else None])

            print()
            # loop over the choices and update
            for c in choices:
                sourcepath = os.path.join(self.sourcedir, c[0])
                destpath = os.path.join(self.destdir, c[0])

                if c[1] == "folder":
                    try:
                        shutil.rmtree(os.path.join(self.destdir, c[2]) if c[2] else destpath)
                        shutil.copytree(sourcepath, destpath)
                        print(f"{self.ansi['success']}Folder {self.obj(c[0])} updated successfully{self.ansi['reset']}")
                    except Exception as e:
                        print(f"{self.ansi['error']}Folder {self.obj(c[0])} failed to update{self.ansi['reset']}")
                elif c[1] == "file":
                    try:
                        os.remove(os.path.join(self.destdir, c[2]) if c[2] else destpath)
                        shutil.copy2(sourcepath, destpath)
                        print(f"{self.ansi['success']}File {self.obj(c[0])} updated successfully{self.ansi['reset']}")
                    except Exception as e:
                        print(f"{self.ansi['error']}File {self.obj(c[0])} failed to update{self.ansi['reset']}")
                else:
                    print(f"{self.ansi['error']}Type is invalid{self.ansi['reset']}")

    def createPage(self):
        nameX = "example"  # default name
        nameI = self.formatPath(  # input name
            str(input(f"\U0001F4D3{self.ansi['info']} Page name {self.optX('info', nameX)}")),
            isLower=False,
            isName=True,
        )
        page_name = nameI if nameI else nameX

        print()
        parent_folder = "testcases"
        if os.path.exists(os.path.join(self.destdir, parent_folder)):  # condition: when folder /testcases exists
            page_name_path = self.formatPath(page_name)
            if not os.path.exists(os.path.join(self.destdir, f"{parent_folder}\{page_name_path}")):  # condition: when folder with name page_name does not exist
                template_folder = os.path.join(self.sourcedir, "template")
                destpath = os.path.join(self.destdir, f"{parent_folder}\{page_name_path}")

                # Copy the template folder to the destination
                shutil.copytree(template_folder, destpath)

                # Rename files inside the copied folder and modify their content
                for root, dirs, files in os.walk(destpath):
                    if "__pycache__" in root:  # condition: skip the __pycache__ folder and its contents
                        continue

                    # loop over files in the dir, and change the contents
                    for name in files:
                        file_path = os.path.join(root, name)
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        content = content.replace("example", page_name.lower().replace(" ", "_"))
                        content = content.replace("Example", page_name.title().replace(" ", ""))
                        content = content.replace("EXAMPLE", page_name.upper().replace(" ", ""))
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)

                print(f"{self.ansi['success']}New page template created in {self.obj(self.destdir)}{self.ansi['reset']}")
            else:
                print(f"{self.ansi['error']}A page folder with name {self.obj(page_name_path)} already exists{self.ansi['reset']}")
        else:
            print(f"{self.ansi['error']}{self.name} could not find folder {self.obj(parent_folder)} in {self.obj(self.destdir)}{self.ansi['reset']}")

    def cli(self):
        parser = argparse.ArgumentParser(description="Generate Directories")
        parser.add_argument("opt", help="Action to perform: 'generate', 'remove', 'update', and 'create-page'", choices=["generate", "remove", "update", "create-page"])
        parser.add_argument("-v", "--version", action="version", version="StateSXT 0.5.8")
        args = parser.parse_args()

        if str(args.opt).lower() == "generate":
            self.generate()
        elif str(args.opt).lower() == "remove":
            self.remove()
        elif str(args.opt).lower() == "update":
            self.update()
        elif str(args.opt).lower() == "create-page":
            self.createPage()
        else:
            print("StateSXT does not has such command.")


def main():
    StateSXT().cli()


if __name__ == "__main__":
    main()
