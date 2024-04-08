from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'An easy to use low level websocket based utility package.'

# Setting up
setup(
    name="ppynet",
    version=VERSION,
    author="Darkodaaa",
    author_email="",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['websocket'],
    keywords=['python', 'sockets', 'connection', 'utility'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)