from setuptools import setup, find_packages
setup(
    name="AHML",
    version="0.2.0",
    packages=find_packages(),
    entry_points={
    	'console_scripts': [
    		'compile_ahml = ahml.compile_ahml:compile_arg'
    	]
    }
)