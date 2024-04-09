from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required_packages = f.read().splitlines()

with open('LICENSE') as f:
    license_text = f.read()

setup(
    name='atl',
    version='0.1',
    packages=find_packages(),
    description='ambedded.ch ambedded-technology-lab python3 library',
    author='ambedded.ch',
    author_email='info@ambedded.ch',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    install_requires=required_packages,
    license=license_text,
    url='https://gitlab.com/ambedded-labs/al-pypi-ambedded-atl',
)
