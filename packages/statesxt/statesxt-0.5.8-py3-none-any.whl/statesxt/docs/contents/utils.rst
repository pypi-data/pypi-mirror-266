######
/utils
######

This is where all common functions are placed.


__init__.py
===========

crypter.py
==========

``generateKey``
---------------

.. code-block:: python

    def generateKey(self):
        return Fernet(Fernet.generate_key())

``encrypt``
-----------

.. code-block:: python

    def encrypt(self, key, message):
        return key.encrypt(message.encode())

``decrypt``
-----------

.. code-block:: python

    def decrypt(self, key, encryptedMessage):
        return key.decrypt(encryptedMessage).decode()


email.py
========

.. code-block:: python

    class Email(ABC):
        """Class to send emails"""

        @abstractmethod
        def send(self):
            pass


.. code-block:: python

    class EmailScheduler(Email):
        """Class to send all emails related to scheduler test cases"""

        context = ssl.create_default_context()
        testResult = {}
        emailSubject = ""
        emailBody = None
        num_of_successes = None
        num_of_fails = None

        def __init__(self, sender_email, sender_password, receiver_email, receiver_name) -> None:
            self.__senderEmail = sender_email
            self.__senderPassword = sender_password
            self.__receiverEmail = receiver_email
            self.__receiverName = receiver_name

``calculateFailsSuccesses``
---------------------------

.. code-block:: python

    def calculateFailsSuccesses(self):
        self.num_of_successes = len(list(filter(lambda x: self.testResult[x][-1] == "PASSED", self.testResult)))
        self.num_of_fails = len(self.testResult) - self.num_of_successes


``generateEmailSubject``
------------------------

.. code-block:: python

    def generateEmailSubject(self):
        self.calculateFailsSuccesses()
        if self.num_of_successes > 1 and self.num_of_fails > 1:
            self.emailSubject = (
                f"{self.emailSubject} - There were {self.num_of_successes} successes and {self.num_of_fails} failures"
            )
        elif self.num_of_successes > 1 and self.num_of_fails <= 1:
            self.emailSubject = (
                f"{self.emailSubject} - There were {self.num_of_successes} successes and {self.num_of_fails} failure"
            )
        elif self.num_of_successes <= 1 and self.num_of_fails > 1:
            self.emailSubject = (
                f"{self.emailSubject} - There were {self.num_of_successes} success and {self.num_of_fails} failures"
            )
        else:
            self.emailSubject = (
                f"{self.emailSubject} - There were {self.num_of_successes} success and {self.num_of_fails} failure"
            )


``generateEmailBody``
---------------------

.. code-block:: python

    def generateEmailBody(self, receiverName):
        self.emailBody = f"""
            Hi {receiverName}-san,
            <br><br>
            I hope this email finds you well. Attached table is the Selenium Test Automation Report for Daily Scheduler, providing an overview of the test results and performance for our software application.
            <br><br>
            Below is a summary table highlighting the key metrics from the Selenium test suite:
            {
                build_table(
                    pd.DataFrame.from_dict(self.testResult),
                    "blue_dark"
                )
            }
            Thank you for your attention to this matter.
            <br><br>
            Best regards,<br>
            QA-Team
        """


``send``
--------

.. code-block:: python

    def send(self):
        if len(self.__receiverName) == len(self.__receiverEmail):
            for receiverName, receiverEmail in zip(self.__receiverName, self.__receiverEmail):
                # create an email object
                lib = EmailMessage()

                # generate the email body and email subject
                self.generateEmailSubject()
                self.generateEmailBody(receiverName)

                # set up email
                lib["From"] = self.__senderEmail
                lib["To"] = receiverEmail
                lib["Subject"] = self.emailSubject
                lib.add_alternative(self.emailBody, subtype="html")

                # send email
                with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=self.context) as smtp:
                    smtp.login(self.__senderEmail, self.__senderPassword)
                    smtp.send_message(lib)
                    smtp.close()
        else:
            raise Exception("number of receiverName does not fit with the number of receiverEmail")


faker.py
========

.. code-block:: python

    class FakerGenerator:
        """Generating fake values"""

        def __init__(self) -> None:
            self.faker = Faker()

``generate_name``
-----------------

.. code-block:: python

    def generate_name(self):
        return self.faker.name()


``generate_title``
------------------

.. code-block:: python

    def generate_title(self):
        return self.faker.company()


``generate_sentence``
---------------------

.. code-block:: python

    def generate_sentence(self, num_of_sentences: int = 1):
        return self.faker.paragraph(nb_sentences=num_of_sentences)


file_opener.py
==============

.. code-block:: python

    class FileOpener:
        """To import, open, and read file"""

``openCSV``
-----------

.. code-block:: python

    @staticmethod
    def openCSV(path, withHeader=False):
        dataList = []
        reader = csv.reader(open(path, "r"))
        if withHeader:
            next(reader)
        for row in reader:
            dataList.append(row)
        return dataList


formatter.py
============

.. code-block:: python

    class Formatter:
        """Converting values into desired format result"""


``convert_query_result``
------------------------

.. code-block:: python

    def convert_query_result(
        self, query_result, rounding_columns=None, rounding_option=None, toList=False
    ):
        result = []

        # converting result to both decimal and datetime if it's possible
        for i in range(len(query_result)):
            for col in query_result[i]:
                query_result[i][col] = self.convert_decimal(query_result[i][col])
                query_result[i][col] = self.convert_datetime(query_result[i][col])
            result.append(query_result[i])

        # rounding number in result
        if rounding_columns:
            result = self.rounding(result, rounding_columns, rounding_option)

        # converting result into a single dimension list
        if toList:
            listResult = []
            for row in result:
                listResult += list(row.values())
            return listResult

        return result

``convert_decimal``
-------------------

.. code-block:: python

    def convert_decimal(self, value):
        """Converts inputted value into decimal format if it is possible"""

        if isinstance(value, Decimal):
            return float(value)
        return value

``convert_datetime``
--------------------

.. code-block:: python

    def convert_datetime(self, value):
        """Converts inputted value into desired date format if it is possible"""

        if isinstance(value, datetime.datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S %Z")
        return value

``convert_number``
------------------

.. code-block:: python

    def convert_number(self, strNumber):
        """Converts inputted string into number if it's possible"""

        if len(strNumber):
            checkedStrNumber = strNumber.replace(".", "", 1)
            checkedStrNumber = (
                checkedStrNumber.replace("-", "", 1)
                if checkedStrNumber[0] == "-"
                else checkedStrNumber
            )
            if checkedStrNumber.isdigit():
                strNumber = (
                    round(float(strNumber), 1) if "." in strNumber else int(strNumber)
                )
        return strNumber

``rounding``
------------

.. code-block:: python

    def rounding(self, query_result, column_names, option):
        """Iterats over query result and rounding all values in certain columns"""

        for row in query_result:
            for col in row:
                if col in column_names:
                    row[col] = round(row[col], option)
        return query_result

``rgba_string_to_hex``
----------------------

.. code-block:: python

    def rgba_string_to_hex(self, rgba_string):
        """Converts RGBA string (mostly from Selenium) into hex code"""

        rgb_values = re.findall(r"\d+", rgba_string)
        r, g, b = map(int, rgb_values[:3])
        return "#{:02x}{:02x}{:02x}".format(r, g, b)

``convert_period``
------------------

.. code-block:: python

    def convert_period(self, period: str) -> list[list]:
        """
        Converts period into separated date

        Args:
            period (str): the period string

        Returns:
            list[list]: the separated date

        Example:
            >>>  convert_period("2023/06/15 - 2023/06/06")
            [[2023, 6, 15], [2023, 6, 6]]
        """

        return [
            [int(_) if _ != "" else _ for _ in date.split("/")]
            for date in period.split(" - ")
        ]

``re_sub``
----------

.. code-block:: python

    def re_sub(self, pattern, string):
        return re.sub(pattern, "", string).strip()

gsheet.py
=========

.. code-block:: python

    class GSheet:
        """Class to interact with Google Sheet"""

        def __init__(self, spreadsheetName) -> None:
            self.__sa = gspread.service_account()
            self.__ss = self.__sa.open(spreadsheetName)

        @property
        def sa(self):
            return self.__sa

        @property
        def ss(self):
            return self.__ss

.. code-block:: python 

    class GSheetStateSXT(GSheet):
        """Class to interact with Google Sheet corresponds to the SPREADSHEET_NAME"""

        scenarioResult = {}

        def __init__(
            self,
            spreadsheetName,
            folderId,
            testedFilesOnly=True,
            executeJSON=False,
        ) -> None:
            super().__init__(spreadsheetName)
            self.curDate = dt.now().strftime("%Y/%m/%d %H:%M:%S")
            self.automationName = "Selenium"
            self.newSpreadsheetName = f"Automation - Release {self.curDate}"
            self.__folderId = folderId
            self.__newSs = None
            self.testedFilesOnly = testedFilesOnly
            self.executeJSON = executeJSON
            self.json_path = "track.json"

``create_a_copy_of_worksheet_into_new_gsheet_file_and_update_the_values``
-------------------------------------------------------------------------

.. code-block:: python

    def create_a_copy_of_worksheet_into_new_gsheet_file_and_update_the_values(
        self, worksheetName, namedRange, values
    ):
        try:  # assuming that the gsheet has already a worksheet with paramater name
            wks = self.__newSs.worksheet(worksheetName)
        except:  # assuming that the gsheet does not have any worksheet the same with the parameter
            oldWks = self.ss.worksheet(worksheetName)
            wks = self.__newSs.worksheet(oldWks.copy_to(self.__newSs.id)["title"])
            wks.update_title(worksheetName)
        wks.update(namedRange, values, value_input_option="USER_ENTERED")


``create_a_copy_of_gsheet_file``
--------------------------------

.. code-block:: python

    def create_a_copy_of_gsheet_file(self):
        self.sa.copy(
            file_id=self.ss.id, title=self.newSpreadsheetName, copy_permissions=True
        )
        self.__newSs = self.sa.open(self.newSpreadsheetName)
        if self.testedFilesOnly:
            deleteRequests = []
            initialSheets = ["Cover", "Use Cases", "ToC", "Queries", "variables"]
            for wks in self.__newSs.worksheets():
                if wks.title not in initialSheets:
                    deleteRequests.append({"deleteSheet": {"sheetId": wks.id}})
            self.__newSs.batch_update({"requests": deleteRequests})


``get_values_by_named_range``
-----------------------------

.. code-block:: python

    def get_values_by_named_range(self, worksheetName, namedRange):
        wks = self.ss.worksheet(worksheetName)
        return wks.get(namedRange)


``upload_the_gsheet_file_to_folder``
------------------------------------

.. code-block:: python

    def upload_the_gsheet_file_to_folder(self):
        # Move the newly created spreadsheet to the desired folder
        drive_service = build("drive", "v3", credentials=self.sa.auth)
        drive_service.files().update(
            fileId=self.__newSs.id, addParents=self.__folderId, fields="id,parents"
        ).execute()



``save_data_to_json``
---------------------

.. code-block:: python

    def save_data_to_json(self):
        # Write data to the JSON file
        with open(self.json_path, "w") as json_file:
            json.dump(
                self.scenarioResult, json_file, indent=4
            )  # Use indent for pretty formatting


``get_json``
------------

.. code-block:: python

    def get_json(self):
        # Read data from the JSON file
        with open(self.json_path, "r") as json_file:
            return json.load(json_file)


``update_all_values``
---------------------

.. code-block:: python

    def update_all_values(self, useJSON=False):
        # create a new file (the duplicate of the target file)
        self.create_a_copy_of_gsheet_file()

        data = self.get_json()
        if not useJSON:
            self.save_data_to_json()
            data = self.scenarioResult
        for worksheetName in data:
            for namedRange in data[worksheetName]:
                values = [
                    [
                        self.curDate,
                        self.automationName,
                        internalCheckResult,
                        externalCheckResult,
                        testerNote,
                    ]
                    for internalCheckResult, externalCheckResult, testerNote in data[
                        worksheetName
                    ][namedRange]
                ]
                self.create_a_copy_of_worksheet_into_new_gsheet_file_and_update_the_values(
                    worksheetName, namedRange.replace("Data", "Form"), values
                )
        # remove sheet1, which is the default sheet that is created when creating a new gsheet file
        if self.__newSs.sheet1.title == "Sheet1":
            self.__newSs.del_worksheet(self.__newSs.sheet1)
        self.upload_the_gsheet_file_to_folder()


``update_worksheet_colors``
---------------------------

.. code-block:: python

    def update_worksheet_colors(self, useJSON=False):
        data = self.scenarioResult
        if useJSON:
            data = self.get_json()
        for wksName in data:
            wksId = self.__newSs.worksheet(wksName).id
            noFail = True
            for nr in data[wksName]:
                if len(list(filter(lambda x: x[0] == "FAILED", data[wksName][nr]))):
                    noFail = False
                    break

            if noFail:
                requestsBatch = [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": wksId,
                                "tabColor": {
                                    "red": 0.0,  # Specify the color values in RGB format (from 0.0 to 1.0)
                                    "green": 1.0,
                                    "blue": 0.0,
                                },
                            },
                            "fields": "tabColor",
                        }
                    }
                ]
            else:
                requestsBatch = [
                    {
                        "updateSheetProperties": {
                            "properties": {
                                "sheetId": wksId,
                                "tabColor": {
                                    "red": 1.0,  # Specify the color values in RGB format (from 0.0 to 1.0)
                                    "green": 0.0,
                                    "blue": 0.0,
                                },
                            },
                            "fields": "tabColor",
                        }
                    }
                ]

            # Send the batchUpdate request
            self.__newSs.batch_update({"requests": requestsBatch})



logger.py
=========

.. code-block:: python

    class RootFilter(logging.Filter):
        def __init__(self, name: str) -> None:
            super().__init__(name)
            self.name = name

        def filter(self, record: logging.LogRecord) -> bool:
            return record.name.startswith(self.name)

.. code-block:: python

    class Logger:
        """Logging messages for a specific system or application component"""

        def __init__(self) -> None:
            # instantiate logging components
            self.logger = logging.getLogger("root")
            self.file_handler = logging.FileHandler("automation.log", mode="w")
            # self.console_handler = logging.StreamHandler()
            self.formatter = logging.Formatter(
                "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
            )

            # set up
            self.setup()

``setup``
---------

.. code-block:: python

    def setup(self):
        # set level of the logger
        self.logger.setLevel(logging.ERROR)

        # set level of the handler
        self.file_handler.setLevel(logging.ERROR)
        # self.console_handler.setLevel(logging.ERROR)

        # install formatter into the handlers
        self.file_handler.setFormatter(self.formatter)
        # self.console_handler.setFormatter(self.formatter)

        # add filters
        self.logger.addFilter(RootFilter(name=self.logger.name))
        self.file_handler.addFilter(RootFilter(name=self.logger.name))
        # self.console_handler.addFilter(RootFilter(name="root"))

        # add the handlers to the logger
        self.logger.addHandler(self.file_handler)
        # self.logger.addHandler(self.console_handler)

``shutdown``
------------

.. code-block:: python

    def shutdown(self):
        logging.shutdown()


response_handler.py
===================

.. code-block:: python

    class ResponseHandler:
        """To get response of calls (making use selenium-wire)"""

``get_response``
----------------

.. code-block:: python

    def get_response(self, driver: webdriver, prefix=""):
        data = []
        for request in driver.requests:
            if request.response:
                if request.url.startswith(prefix):
                    response = request.response
                    body = decode(
                        response.body,
                        response.headers.get("Content-Encoding", "identity"),
                    )
                    decoded_body = body.decode("utf-8")
                    json_data = json.loads(decoded_body)
                    data.append(json_data)
        return data

wrapper.py
==========

.. code-block:: python

    class Wrapper:
        """Making use functools\wraps"""

``exception_handling_returns_None``
-----------------------------------

.. code-block:: python

    @classmethod
    def exception_handling_returns_None(cls, func):
        """
        to let a test case returns a None value instead of raises an exception/error
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger(
                    f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}"
                ).error(f"error:\n{str(e)}")
                return None

        return wrapper
        
``exception_handling_raises_error``
-----------------------------------

.. code-block:: python

    @classmethod
    def exception_handling_raises_error(cls, func):
        """
        to handle the error by tracking, but keeps raises the error
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.getLogger(
                    f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}"
                ).error(f"error:\n{str(e)}")
                raise Exception(str(e))

        return wrapper
        
``result_receiving``
--------------------

.. code-block:: python

    @classmethod
    def result_receiving(cls, func):
        """
        to track the result of test cases, so instead of directly raising error, it lets to write down the error first, e.g. email, report, and summary
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            funcName = str(func.__name__).replace("_", " ").title()
            try:
                isFail = False
                errorMessage = None
                try:
                    func(self, *args, **kwargs)
                    self.email.testResult[funcName].append("PASSED")
                except Exception as e:
                    if str(e).replace("'", "") != funcName:
                        logging.getLogger(
                            f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}"
                        ).error(
                            f"class: {self.__class__.__name__}, method: {func.__name__}\n{str(e)}"
                        )
                        isFail = True
                    errorMessage = str(e)
                    self.email.testResult[funcName].append("FAILED")
            except:
                if not isFail:
                    self.email.testResult[funcName] = ["PASSED"]
                else:
                    self.email.testResult[funcName] = ["FAILED"]

            print(f"\n\nCurrent results:\n{self.email.testResult}")
            if isFail:
                raise Exception(f"There is an error in {funcName}: {errorMessage}")

        return wrapper
        
``unpagshe``
------------

.. code-block:: python

    @classmethod
    def unpagshe(cls, worksheetName, named_range, needExternalCheck=False):
        """
        to retrieve and unpack the data from gsheet
        """
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                data = self.gsheet.get_values_by_named_range(worksheetName, named_range)
                result = []
                isFail = False
                emptyFormats = [
                    "",
                    "-",
                    "<blank>",
                    "<empty>",
                    "blank",
                    "empty",
                    "inactive",
                    "uncheck",
                ]
                anyFormats = ["anything", "dc", "Any", "any"]
                for row in data:
                    # preprocess data
                    row = [None if (col in emptyFormats) else col for col in row]
                    row = [
                        FakerGenerator().generate_sentence()
                        if (col in anyFormats)
                        else col
                        for col in row
                    ]

                    try:
                        func(self, *row, *args, **kwargs)
                        result.append(
                            ["PASSED", "PASSED" if needExternalCheck else "", ""]
                        )
                    except Exception as e:
                        logging.getLogger(
                            f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}"
                        ).error(
                            f"class: {self.__class__.__name__}, method: {func.__name__}\n{str(e)}"
                        )
                        # raise Exception(str(e))
                        result.append(
                            [
                                "FAILED",
                                "FAILED" if needExternalCheck else "",
                                f"'{str(e)}'",
                            ]
                        )
                        if not isFail:
                            isFail = True

                try:
                    self.gsheet.scenarioResult[worksheetName][named_range] = result
                except:
                    self.gsheet.scenarioResult[worksheetName] = {named_range: result}
                if isFail:
                    raise Exception("an error occured")

            return wrapper

        return decorator
        
``login_exeception_handling``
-----------------------------

.. code-block:: python

    @classmethod
    def login_exeception_handling(cls, func):
        """to catch the error when login"""
        decoratorClassName = cls.__name__
        decoratorMethodName = sys._getframe().f_code.co_name

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)

            except Exception as e:
                logging.getLogger(
                    f"root.{__name__}.{decoratorClassName}.{decoratorMethodName}"
                ).error(f"login error:\n{str(e)}")
                raise Exception(str(e))

        return wrapper
        
``role_checking``
-----------------

.. code-block:: python

    @classmethod
    def role_checking(cls, func_role):
        """
        to check the role inputted (from command) before executing any testcase (not used/deprecated)
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                if self.role == func_role:
                    func(self, *args, **kwargs)
                else:
                    print(f"Role doesn't match, skipping '{func.__name__}' execution")
                    return

            return wrapper

        return decorator
        