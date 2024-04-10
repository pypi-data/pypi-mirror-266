from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

# Setting up
setup(
    name="telugu_words_numbers",
    packages=find_packages(where="telugu_words_numbers"),
    version='0.0.1',
    license='MIT',
    author="Sandeep Panchal",
    author_email="sandeep.panchal545@gmail.com",
    description='Telugu words to numbers conversion',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/Sandeep-Panchal/telugu-word-to-number-conversion/tree/main",
    project_urls ={
            "Bug Tracker" : "https://github.com/Sandeep-Panchal/telugu-word-to-number-conversion/issues"
        },
    install_requires=["text2digits", "numpy"],
    keywords=[
        "telugu", "words", "numbers", "conversion", "words to number",
        "words to number conversion", "telugu words number conversion",
    ], 
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)