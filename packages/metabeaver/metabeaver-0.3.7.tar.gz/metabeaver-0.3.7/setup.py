from setuptools import setup, find_packages

setup(
    name='metabeaver',
    version='0.3.7', # Major, minor, patch
    packages=find_packages(exclude=['Testing', '*.xlsx', '*.xls']),
    install_requires=[
        'google-cloud-bigquery',
        'google-cloud-core',
        'numpy',
        'pandas',
        #transformers,
        #llama-cpp-python,
    ],
    description='Beaverish about data. '
                'Metabeaver originally started as a "glue" project to bring together commonly used code. '
                'It has since expanded to contain common operations, metaprogramming, and Computer Sci resources. ' 
                'It is intended a resource to learn computer science, Python, and limit the need to rebuild the wheel. '
                'For development operations, please see Operation Beaver.',
    author='Luke Anthony Pollen',
    author_email='luke@pollenanalytics.com',
    url='https://github.com/rainbowpusheenthe3rd/dataBeaver',
)


##### ERRATA #####

### Create the wheel and the tar in dist folder
#python setup.py sdist bdist_wheel
# OR
# python setup.py sdist

### Upload to PyPi, using twine
#twine upload dist/*
# OR
#twine upload *

### Where does Twine live?
#pip show twine
#dir /s twine.exe

##### ERRATA #####