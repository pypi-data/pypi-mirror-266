from setuptools import setup, find_packages

VERSION = '0.0.2.1'
DESCRIPTION = 'Python3 Package for Fingerprint Processing'
LONG_DESCRIPTION = ('This is a python3 package for fingerprint processing,'
                    ' which can be used for fingerprint enhancement.')

setup(
    name="fplab",
    version=VERSION,
    author="Yurun Wang",
    author_email="wangyurun@mail.sdu.edu.cn",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    license='MIT',
    install_requires=[],
    keywords=['python', 'fingerprint'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires='>=3.10'
)
