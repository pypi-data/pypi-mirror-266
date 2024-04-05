from setuptools import setup, find_packages 

# reading long description from file 
# with open('DESCRIPTION.txt') as file: 
# 	long_description = file.read()


# specify requirements of your package here 
REQUIREMENTS = ['jsonschema']

# some more details 
CLASSIFIERS = [ 
	'Development Status :: 4 - Beta', 
	'Intended Audience :: Developers', 
	'Topic :: Internet', 
	'License :: OSI Approved :: MIT License', 
	'Programming Language :: Python', 
	'Programming Language :: Python :: 2', 
	'Programming Language :: Python :: 2.6', 
	'Programming Language :: Python :: 2.7', 
	'Programming Language :: Python :: 3', 
	'Programming Language :: Python :: 3.3', 
	'Programming Language :: Python :: 3.4', 
	'Programming Language :: Python :: 3.8', 
	]

# calling the setup function 
setup(name='graas-observability-utility', 
	version='1.5.7', 
	description='A small wrapper around data observability', 
	# long_description=long_description, 
	url='https://bitbucket.org/shoptimizeanalytics/graas-observability-utility', 
	author='Graas', 
	author_email='priyanka.patel@graas.ai', 
	# license='MIT',
    packages=find_packages(),
    # data_files=[('graas_utilities', ['schemas/*.json'])],
    include_package_data=True,    
	classifiers=CLASSIFIERS, 
	install_requires=REQUIREMENTS, 
	keywords='utility'
	)
