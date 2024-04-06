from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Hello'

# Setting up
setup(
    name="wengtimIsNotGay",
    version=VERSION,
    author="Wengtim",
    author_email="<siewt48@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
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
