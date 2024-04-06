from setuptools import setup, find_packages

setup(
    name='Information_Retrieval',
    version='3.0',
    packages=find_packages(),
    install_requires=[
        # Add dependencies here.
    ],
    entry_points={
        "console_scripts" : [
            "hello = Information_Retrieval:hello",
        ],
    },
)