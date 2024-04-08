from setuptools import setup, find_packages

setup(
    name='OperationBattleshipCommonUtilities',
    version='0.4.1',
    packages=find_packages(),
    license='Apache-2.0 license',
    description='Classes and Utilities that are shared in the Operation Battleship Application',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Matthew Caraway',
    author_email='matthew@CarawayLabs.com',
    url='https://github.com/CarawayLabs/OperationBattleshipCommonUtilities',
    install_requires=[
        'python-dotenv',
        'apify-client',
        'pandas',
        'psycopg2',
        'nomic',
        'openai',
        'pinecone-client',
    ],
)
