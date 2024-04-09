import os, shutil

# os.chdir(r"D:\Coding\GPP-Vue\gpp-py-components")
os.chdir(r"D:\gitLab\gpp-py-components")
dir_list = ["./build", "./dist", "./gpp_components.egg-info"]
for i in dir_list:
    if os.path.exists(i):
        shutil.rmtree(i)


from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="gpp_components",
    version="0.0.36",
    #
    author="L",
    description="for internal use",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",
    #
    packages=find_packages(),
    install_requires=[
        "crypto",
        "django",
        "cx_Oracle",
        "pandas",
        "jsonpath",
        "rich",
        "SQLAlchemy",
    ],
)
