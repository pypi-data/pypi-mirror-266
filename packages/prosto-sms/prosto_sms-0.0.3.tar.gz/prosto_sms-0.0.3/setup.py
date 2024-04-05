from setuptools import setup

with open('requirements.txt') as f:
    requirements = list(map(lambda x: x.strip(), f.readlines()))

setup(
    name='prosto_sms',
    version='0.0.3',

    author='Alex Dennitsev',
    author_email='me@chydo.dev',

    url="https://github.com/exituser/prosto-sms-python",
    description='sms-prosto api wrapper written in python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    packages=['prosto_sms'],
    install_requires=requirements,

    classifiers=[
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.11'
    ]
)
