from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="integ-db",
    version="0.0.8",
    author="byeongin.jeong",
    author_email="jbi0214@gmail.com",
    description="This package Integrated Database library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Byeongin-Jeong/integdb",
    project_urls={
        "Bug Tracker": "https://github.com/Byeongin-Jeong/integdb/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Topic :: Database',
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    keywords=['mysql', 'mssql', 'mariadb', 'python db', 'python database', 'integrate database', 'sqlalchemy'],
    install_requires=['pymysql', 'mariadb', 'pymssql', 'pymysql-pool', 'SQLAlchemy', 'pandas'],
)