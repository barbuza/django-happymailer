from setuptools import setup, find_packages

setup(
    name='django-happymailer',
    version='0.4.0',
    description='django email templates manager',
    author='Victor Kotcheruba',
    author_email='barbuzaster@gmail.com',
    maintainer='Dmitrii Gerasimenko',
    maintainer_email='kiddima@gmail.com',
    include_package_data=True,
    packages=find_packages(exclude=['django_happymailer','dummy','dummy2']),
    install_requires=[
        'django >= 3.2.4, < 4.0',
        'django-import-export >= 0.4.5',
        'faker >= 0.8.6',
        'html2text >= 2016.5.29',
        'trafaret >= 2.1, < 3.0',
        'six',
    ]
)

