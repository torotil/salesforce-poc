from setuptools import setup

setup(
    name="Salesforce POC",
    version="0.1",
    py_modules=["salesforce_poc"],
    install_requires=[
        "click",
        "ipython",
        "pyjwt",
        "pyyaml",
        "requests",
    ],
    entry_points="""
        [console_scripts]
        sf-poc=salesforce_poc:cli
    """,
)
