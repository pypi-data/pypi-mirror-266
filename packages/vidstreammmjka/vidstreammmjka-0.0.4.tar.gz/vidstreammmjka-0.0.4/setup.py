from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.4'
DESCRIPTION = 'Hello Pack'

# Setting up
setup(
    name="vidstreammmjka",
    version=VERSION,
    author="NeuralNine (Florian Dedov)",
    author_email="<mail@neuralnine.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={'vidstreammmjka': ['helloworld.kv']},
    install_requires=['kivy'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)