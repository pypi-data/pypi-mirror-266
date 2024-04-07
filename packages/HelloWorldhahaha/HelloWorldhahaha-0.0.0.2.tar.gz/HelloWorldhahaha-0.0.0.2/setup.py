from setuptools import setup

with open('README.md', encoding='utf-8') as f:
	  long_description = f.read()

setup(
	name='HelloWorldhahaha',
	version='0.0.0.2',
	long_description    = long_description,
	long_description_content_type = 'text/markdown',
	description='hello world package.',
	author='',
	author_email='',
	url='',
	license='MIT',
	python_requires='>=3.4',
	install_requires=[ 'boto3', 'pymongo'],
	packages=['HelloWorldhahaha']
)