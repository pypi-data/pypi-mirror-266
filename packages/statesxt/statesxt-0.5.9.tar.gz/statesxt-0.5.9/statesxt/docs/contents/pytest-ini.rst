##########
pytest.ini
##########

``pytest.ini`` is a configuration file used by the Pytest testing framework for Python. Pytest is a popular testing tool that allows you to write simple unit tests as well as complex functional testing scenarios.

The ``pytest.ini`` file allows you to customize the behavior of Pytest by specifying various configuration options. This file should typically be placed in the root directory of your project. When Pytest runs, it looks for this configuration file to determine how to execute the tests.

By configuring pytest through ``pytest.ini``, you can tailor the testing process to your project's specific needs. It helps in maintaining consistency across your tests and provides a centralized way to manage various testing-related settings.

.. code-block:: ini

    [pytest_html]
    encoding = utf-8

This section is specific to the pytest-html plugin, which is a pytest plugin that generates HTML reports for your test results. In this case, it sets the encoding of the HTML report to UTF-8. This ensures that the HTML file can correctly represent characters from a wide range of languages.

.. code-block:: ini

    [pytest]
    markers=
        dev: is a non-product marker where is used for development only

This section is related to general pytest configuration. It defines a custom marker named "dev." In pytest, markers are used to label or categorize tests. Here, the marker "dev" is explained as a non-product marker used only for development purposes. Developers can use this marker to tag specific tests and then run or exclude them based on the marker. For example, you can run tests with the "dev" marker using the -m option:

.. code-block:: bash

    pytest -m dev

This can be helpful when you have tests that are not meant for regular production runs but are useful during development or debugging.