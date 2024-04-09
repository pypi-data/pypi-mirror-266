from setuptools import find_packages, setup

setup(
    name='halludetector',
    version='0.0.1',
    author='Mihai Onofrei',
    author_email='monofrei@cisco.com',
    url='https://github.com/Mihai-Onofrei/Hallucination-detector',  # Replace with your project's URL
    license='MIT',  # Choose an appropriate license
    description="Hallucination detection package",
    long_description=open('README.rst').read(),
    include_package_data=True,
    packages=find_packages(),
    package_data={
        '': ['*.json'],  # Include all JSON files in the package
        'logos': ['*.png'],
        'js': ['*.js'],
        'txt': ['*.txt']
    },
    install_requires=[
        'openai',
        'click'
    ]
)
