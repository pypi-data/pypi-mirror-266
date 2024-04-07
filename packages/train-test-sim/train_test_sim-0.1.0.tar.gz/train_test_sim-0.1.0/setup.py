from setuptools import setup, find_packages
import codecs
import os
import pandas
import string
import warnings
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix,precision_score,accuracy_score,recall_score,f1_score


here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()
VERSION = '0.1.0'
DESCRIPTION = 'Library to create simulation to find out what train test ratio is ideal'
LONG_DESCRIPTION = 'This library will let you know what is train test ratio is ideal for your model'


setup(
    name="train_test_sim",
    version=VERSION,
    author="Marcel Tino",
    author_email="<marceltino92@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['pandas','numpy','scikit-learn'],
    keywords=['train test','simulation'])
