import os
import re
from setuptools import setup

f = open(os.path.join(os.path.dirname(__file__), 'README.md'))
readme = f.read()
f.close()

f = open(os.path.join(os.path.dirname(__file__), 'yurumikuji/__init__.py'))
for line in f:
    if '__version__ = ' in line:
        version_ = [x for x in re.split(r"[ =']", line) if x][1]
    elif '__author__ = ' in line:
        author_ = [x for x in re.split(r"[ =']", line) if x][1]
f.close()

test_deps = ['importlib-metadata<2,>=0.12', 'tox', 'tox-pyenv', 'pytest']

setup(
    name = "yurumikuji"
    , version = version_
    , author = author_
    , author_email = "zumix.cpp@gmail.com"
    , url = "https://github.com/srz-zumix/yurumikuji/"
    , description = "kamidana(jinja2 cli) slack additonal."
    , license = "MIT"
    , platforms = ["any"]
    , keywords = "Slack, Jinja2"
    , packages = ['yurumikuji']
    , long_description = readme
    , long_description_content_type='text/markdown'
    , classifiers = [
        "Development Status :: 4 - Beta"
        , "Topic :: Utilities"
        , "License :: OSI Approved :: MIT License"
        , "Programming Language :: Python"
        , "Programming Language :: Python :: 3.7"
        , "Programming Language :: Python :: 3.8"
        , "Programming Language :: Python :: 3.9"
    ]
    , install_requires=['jinja2>=3.1', 'markupsafe', 'kamidana>=0.10', 'slack_sdk', 'python-dotenv']
    , tests_require=test_deps
    , test_suite="tests.test_suite"
    , extras_require={
        'test': test_deps
    }
)
