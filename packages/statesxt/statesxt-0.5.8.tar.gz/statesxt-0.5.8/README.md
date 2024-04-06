# StateSXT

![Tests](https://github.com/cjsonnnnn/statesxt/actions/workflows/test.yml/badge.svg)
<br/>

## How to Install?
There are two approaches to install the package:
- Manually cloning the project in Github repository: [statesxt](https://github.com/jsonnnnn/statesxt)
- Using `pip`, that the package is hosted in [here](https://pypi.org/project/statesxt/#description) <b>(recommended)</b>. 
  ``` console
  pip install statesxt
  ```

> **Note:** It is always better to install the package in a virtual environment.

## How to Use?
- Generate the template
  ``` console
  statesxt generate
  ```
- Remove the template
  ``` console
  statesxt remove
  ```
- Update the template
  ``` console
  statesxt update
  ```
- Generate a new page template (inside /testcases)
  ``` console
  statesxt create-page
  ```


## How to Update?
Currently, the package can not be updated through usual command `pip install --upgrade statesxt`. Probably because is hosted in TestPypi.
So, for the time being, user have to reinstall the package.


## How to Uninstall?
There are two approaches to uninstall the package:
- Uninstalling only the package
  ``` console
  pip uninstall statesxt
  ```
- Uninstalling the package and its dependencies <b>(vulnerable)</b>.
  To do this, the user must install a package called `pip-autoremove` (if not already installed).
  ``` console
  pip install pip-autoremove
  ```
  Once the package is installed, user can now uninstall the package with the following command.
  ``` console
  pip-autoremove statesxt -y
  ```
  Note: If there is an error saying that `ModuleNotFoundError: No module named 'pip_autoremove'`, you could try to move the `pip_autoremove.py` file from `./Scripts` into `./Lib` instead. For further information: [here](https://stackoverflow.com/questions/74523001/modulenotfounderror-when-trying-to-use-pip-autoremove).


## How to Test?
There is a tox.ini file inside .\statesxt\, where you can just execute it by invoking `tox -c .\statesxt\` in terminal. But anyway, that is to test manually in your local, meanwhile there is .github\ that enables to testing with Github Actions, where it works by triggering the execution of `tox.ini` once you make a commit. So basically, it has implemented CI/CD. 


## License
This project is licensed under the [MIT License](https://github.com/cjsonnnnn/statesxt?tab=MIT-1-ov-file).