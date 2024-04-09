import pika
from setuptools import setup, find_packages
with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='tieto_pika_test1',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        # Add any dependencies your package needs here, e.g.,
        # 'numpy',
        'pika'
    ],
    # Add other necessary metadata here, such as author, email, description, etc.
)