from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='LughaatNLP',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['stopwords.json', 'tokenizer.json', 'Urdu_Lemma.json']},
    entry_points={
        'console_scripts': [
            'lughaatnlp = LughaatNLP.LughaatNLP:main'
        ]
    },
    install_requires=[
        'python-Levenshtein'
    ],
    author='Muhammad Noman',
    author_email='muhammadnomanshafiq76@gmail.com',
    description='A Python package for natural language preprocessing tasks in Urdu language.',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    license_files=['LICENSE'],
    keywords='nlp urdu LughaatNLP urdunlp UrduNLP urduhack stanza natural-language-processing text-processing language-processing preprocessing stemming lemmatization tokenization stopwords',
    url='https://github.com/MuhammadNoman76/LughaatNLP'
)