from setuptools import setup, find_packages

setup(
    name='django-happymailer',
    version='0.1.9',
    description='django email templates manager',
    author='Victor Kotcheruba',
    author_email='barbuzaster@gmail.com',
    maintainer='Dmitrii Gerasimenko',
    maintainer_email='kiddima@gmail.com',
    include_package_data=True,
    packages=find_packages(exclude=['django_happymailer','dummy','dummy2']),
    install_requires=[
        'django >= 1.9',
        'django-import-export >= 0.4.5',
        'fake-factory >= 0.5.7',
        'html2text >= 2016.5.29',
        'trafaret >= 0.7',
        'six',
    ]
)

