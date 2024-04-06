import setuptools

with open("README.md", encoding="utf8") as file:
    LONG_DESC = file.read()

setuptools.setup(
    name="statesxt",
    version="0.5.8",
    description="A project template for testing your website application.",
    long_description=LONG_DESC,
    long_description_content_type="text/markdown",
    url="https://test.pypi.org/project/statesxt/",
    author="Jason Caleb",
    author_email="cjsonnnnn@gmail.com",
    license="MIT License",
    project_urls={
        "Source": "https://github.com/jsonnnnn/statesxt",
        "Documentation": "https://statesxt.readthedocs.io/en/latest/",
    },
    classifiers=[
        "Development Status :: 1 - Planning",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities",
    ],
    entry_points={
        "console_scripts": [
            "statesxt=statesxt.main:main",
        ],
    },
    keywords=[
        "Selenium",
        "Pytest",
        "Python",
        "project template",
        "template",
        "Testing",
        "Framework",
    ],
    python_requires=">=3.10",
    packages=setuptools.find_packages(),
    include_package_data=True,
    setup_requires=["setuptools-git"],
)
