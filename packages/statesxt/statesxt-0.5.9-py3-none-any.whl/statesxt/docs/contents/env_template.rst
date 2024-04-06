#############
.env_template
#############

This file contains all sensitive parameters that are important for your program to running. Most of the parameters below are about the configurations in order to establish a connection to your database. While the rest parameters are used to send emails, and establish connection to Google Sheet and Google Drive.
Once, everything set, you should then rename this file to ``.env``.

.. caution::    
    This ``.env`` file holds your project's secret keys, like API passwords and database credentials. Exposing them on GitHub is like giving away your castle keys. Use a .gitignore file to lock them away, and treat security like a shield, not a burden, to keep your project safe and sound.



POSTGRE_DB_SSH_HOST
===================
This refers to the hostname or IP address of the server to which you connect via SSH. If your PostgreSQL server is behind a firewall or on a private network, and you need to access it securely, you might use SSH tunneling. Example: ``192.168.1.100``.


POSTGRE_DB_SSH_PORT
===================
This is the port number on which the SSH service is running on the server. The default SSH port is ``22``, but it could be configured differently for security reasons.


POSTGRE_DB_SSH_USERNAME
=======================
This is the username used to authenticate yourself on the SSH server. You need the correct SSH username to establish a connection.


POSTGRE_DB_SSH_PASSWORD
=======================
This is the password associated with the SSH username. Alternatively, SSH connections can use key-based authentication for added security. 


POSTGRE_DB_DB_SERVER
====================
This refers to the hostname or IP address of the server where your PostgreSQL database is running. It's the direct address to reach the PostgreSQL service itself. When you're connecting to the database without using SSH tunneling, you use this parameter to specify the address of the PostgreSQL server directly. Example: ``db.example.com``.


POSTGRE_DB_DB_PORT
==================
This is the port number on which the PostgreSQL service is running on the server. The default PostgreSQL port is ``5432``.


EXAMPLE_DB_DB_NAME
==================
This is the name of the specific PostgreSQL database you want to connect to. You need to know the name of the database you want to work with.


EXAMPLE_DB_DB_USER
==================
This is the username used to authenticate yourself to the PostgreSQL database server. You need the correct PostgreSQL username to connect.


EXAMPLE_DB_DB_PASSWORD
======================
This is the password associated with the PostgreSQL username. Make sure to keep this information secure. If you don't have this password or have forgotten it, you might need to reset it through your database management system or consult with your database administrator.


SENDER_EMAIL
============
This variable represents the email address associated with the sender or the originator of the communication. When implementing email functionality in your application, set this variable to the email address from which emails will be sent.


SENDER_PASSWORD
===============
This variable holds the password associated with the sender's email account for authentication purposes.


RECEIVER_EMAIL
==============
This variable denotes the email address of the recipient or the target of the communication. When configuring email functionality, set this variable to the email address where you want to send the emails. You could provide more than one email into it by using coma as the separator.


RECEIVER_NAME
=============
This variable represents the name of the recipient, providing a human-readable identification for the receiver of the email. You could also provide more than one name into it by using coma as the separator as well.


SPREADSHEET_NAME
================
This variable specifies the name of the Google Sheets file associated with the signed-in account on the computer. The Google Sheets file serves as the data source for the program, containing information or data that the program needs to access or manipulate.

.. note::
    The thing about **signed-in account on the computer** actually is an account service. This account serves as interface for you to communicate with Google Service, e.g. Google Sheets and Google Drive, through the use of APIs. For further information click `here <https://docs.gspread.org/en/v5.10.0/oauth2.html#enable-api-access/>`_.


FOLDER_ID
=========
This variable designates the unique identifier of the Google Drive folder where the report generated after the execution of the program will be stored. The folder is associated with the signed-in Google account on the computer, and the program integrates with Google Drive to manage the storage location of generated reports. You could obtain this information from the URL of the folder.