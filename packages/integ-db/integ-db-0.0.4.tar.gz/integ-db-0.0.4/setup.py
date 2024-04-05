from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="integ-db",
    version="0.0.4",
    author="byeongin.jeong",
    author_email="jbi0214@gmail.com",
    description="Python Integrated Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Byeongin-Jeong/integdb",
    project_urls={
        "Bug Tracker": "https://github.com/Byeongin-Jeong/integdb/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    keywords=['mysql', 'mssql', 'mariadb', 'python db', 'python database', 'integrate database', 'sqlalchemy'],
    install_requires=['pymysql', 'mariadb', 'pymssql', 'pymysql-pool', 'SQLAlchemy', 'pandas'],
)