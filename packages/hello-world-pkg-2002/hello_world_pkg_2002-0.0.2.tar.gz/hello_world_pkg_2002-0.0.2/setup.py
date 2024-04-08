from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))


VERSION = '0.0.2'
DESCRIPTION = 'this is a simple hello world pkg'
# Setting up
setup(
    name="hello_world_pkg_2002",
    version=VERSION,
    author="Sathish Kumar",
    author_email="sathishmahi456@gmail.com",
    packages=find_packages(),
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