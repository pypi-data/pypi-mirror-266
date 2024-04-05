from setuptools import setup, find_packages

# Function to read the list of requirements from 'requirements.txt'
def read_requirements():
    with open('requirements.txt', 'r') as req:
        return [line for line in req.read().splitlines() if "file:" not in line]
    

setup(
    name='RAG_metrics_2',
    version='0.0.1.29', # all versions prior to launch will go into 0.0.1.--
    packages=find_packages(),
    license='MIT',
    description='This library is to search the best parameters across different steps of the RAG process.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Ankit',
    author_email='a.baliyan008@gmail.com',
    url='https://github.com/hidevscommunity/gen-ai-library/tree/main/Ankit',
    install_requires=[
        'langchain>=0.1.13',
        'langchain-community>=0.0.29',
        'langchain-core>=0.1.36',
        'langchain-openai>=0.1.1',
        'langchain-text-splitters>=0.0.1',
        'tiktoken>=0.6.0',
        'scikit-learn>=1.4.1.post1',
        'trulens-eval>=0.27.0',
        'chromadb>=0.4.24',
        'sentence-transformers>=2.6.1',
        'nltk>=3.8.1',
        'unstructured[pdf]==0.13.0',
        'unstructured-client>=0.18.0',
        'openai>=1.10.0'
    ],
)


# python setup.py sdist bdist_wheel
