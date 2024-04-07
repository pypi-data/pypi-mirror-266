from setuptools import setup, find_packages

setup(
    name="flaskfy",
    author="Álvaro Mbeia Daniel Miguel",
    author_email="alvarombeiadanielmiguel@gmail.com",
    description="This is a lib to help generate flask apps with custom components",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AlvaroMbeiaDanie1234/flaskfy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "pymysql",
        "flask",
    ],
    entry_points = {
        "console_scripts": [
            "createflaskapp = flaskfy:criar_projeto_flask"
        ]
    }
)