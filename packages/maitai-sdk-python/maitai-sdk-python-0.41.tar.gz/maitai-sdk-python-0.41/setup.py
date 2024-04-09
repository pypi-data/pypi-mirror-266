# setup.py

from setuptools import setup, find_packages

setup(
    name='maitai-sdk-python',
    version='0.41',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    # Optional metadata
    author='Christian DalSanto',
    author_email='christian@yewpay.com',
    description='MaiTai SDK for Python',
    url='https://github.com/yewpay/maitai-sdk-python',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
