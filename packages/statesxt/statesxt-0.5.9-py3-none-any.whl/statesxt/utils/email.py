from pretty_html_table import build_table
from email.message import EmailMessage
from abc import ABC, abstractmethod
import pandas as pd
import smtplib
import ssl


class Email:
    """Class to send all emails related to scheduler test cases"""

    context = ssl.create_default_context()
    emailSubject = ""
    emailBody = None
    num_of_successes = None
    num_of_fails = None

    @abstractmethod
    def send(self):
        pass

    def __init__(self, sender_email, sender_password, receiver_email, receiver_name, results={}) -> None:
        self.results = results
        self.__senderEmail = sender_email
        self.__senderPassword = sender_password
        self.__receiverEmail = receiver_email
        self.__receiverName = receiver_name

    def calculateFailsSuccesses(self):
        self.num_of_successes = len(list(filter(lambda x: self.results[x][-1] == "PASSED", self.results)))
        self.num_of_fails = len(self.results) - self.num_of_successes

    def generateEmailBody(self, receiverName):
        self.emailBody = f"""
            Hi {receiverName}-san,
            <br><br>
            I hope this email finds you well. Attached table is the Selenium Test Automation Report, providing an overview of the test results and performance for our software application.
            <br><br>
            Below is a summary table highlighting the key metrics from the Selenium test suite:
            {
                build_table(
                    pd.DataFrame.from_dict(self.results),
                    "blue_dark"
                )
            }
            Thank you for your attention to this matter.
            <br><br>
            Best regards,<br>
            QA-Team
        """

    def generateEmailSubject(self):
        self.calculateFailsSuccesses()
        if self.num_of_successes > 1 and self.num_of_fails > 1:
            self.emailSubject = f"{self.emailSubject} - There were {self.num_of_successes} successes and {self.num_of_fails} failures"
        elif self.num_of_successes > 1 and self.num_of_fails <= 1:
            self.emailSubject = f"{self.emailSubject} - There were {self.num_of_successes} successes and {self.num_of_fails} failure"
        elif self.num_of_successes <= 1 and self.num_of_fails > 1:
            self.emailSubject = f"{self.emailSubject} - There were {self.num_of_successes} success and {self.num_of_fails} failures"
        else:
            self.emailSubject = f"{self.emailSubject} - There were {self.num_of_successes} success and {self.num_of_fails} failure"

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
