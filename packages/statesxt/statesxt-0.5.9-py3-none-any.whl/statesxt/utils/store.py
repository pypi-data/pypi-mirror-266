import json


class Store:
    def __init__(self) -> None:
        self.__results = {"Scenario": {}, "Test Cases": {}}
        self.ansiPassed = "\u001b[32m"
        self.ansiFailed = "\033[91m\033[1m"
        self.ansiReset = "\033[0m"
        self.notifPassed = f"{self.ansiPassed}PASSED{self.ansiReset}"
        self.notifFailed = f"{self.ansiFailed}FAILED{self.ansiReset}"
        self.json_path = "results.json"

    def getResults(self):
        return self.__results

    def printUseCaseResults(self, class_name):
        print(f"\n\nTest Results of {class_name}")
        classResults = self.__results["Scenario"][class_name]
        for res in classResults:
            print(f"- {res}: {self.notifPassed if classResults[res] == 'PASSED' else self.notifFailed}")

    def setTestCasesResult(self, worksheet_name, named_range, result):
        try:
            self.__results["Test Cases"][worksheet_name][named_range] = result
        except:
            self.__results["Test Cases"][worksheet_name] = {named_range: result}

    def setScenarioResult(self, class_name, scenario, result):
        try:
            self.__results["Scenario"][class_name][scenario] = result
        except:
            self.__results["Scenario"][class_name] = {scenario: result}

    def updateJSON(self):
        try:
            with open(self.json_path, "w") as json_file:
                json.dump(self.__results, json_file, indent=4)
        except Exception as e:
            print(f"An error happened when trying to save the result data to {self.json_path}: \n{e}")
