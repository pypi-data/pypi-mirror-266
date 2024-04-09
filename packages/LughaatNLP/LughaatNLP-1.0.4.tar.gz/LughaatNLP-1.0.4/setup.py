from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_file(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), 'r', encoding='utf-8') as f:
        return f.read()

setup(
    name='LughaatNLP',
    version='1.0.4',
    packages=find_packages(),
    include_package_data=True,
    package_data={'LughaatNLP': ['Urdu_Lemma.json', 'stopwords.json', 'tokenizer.json' , 'NER_Model.h5' , 'pos_model.h5' , 'tag2index.json' , 'tag2index.pkl' ,'word2index.json' , 'word2index.pkl']},
    entry_points={
        'console_scripts': [
            'lughaatnlp = LughaatNLP.LughaatNLP:main'
        ]
    },
    install_requires=[
        'python-Levenshtein',
        'tensorflow',
        'numpy'
    ],
    project_urls = {
    'Source': 'https://github.com/MuhammadNoman76/LughaatNLP',
    'Issue Tracker': 'https://github.com/MuhammadNoman76/LughaatNLP/issues',
    'LinkedIn': 'https://www.linkedin.com/in/muhammad-noman76',
    'YouTube Channel': 'https://www.youtube.com/channel/YOUR_CHANNEL_ID_HERE'
    },
    classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    'Topic :: Text Processing :: Linguistic',
    'Natural Language :: Urdu',
    ],
    author='Muhammad Noman',
    author_email='muhammadnomanshafiq76@gmail.com',
 description='A Python package for natural language processing tasks for the Urdu language, including normalization, part-of-speech (POS) tagging, named entity recognition (NER), stemming, lemmatization, tokenization, and stopword removal.',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    license_files=['LICENSE'],
    keywords='urdu nlp natural language processing text processing tokenization stemming lemmatization stopwords morphological-analysis nlp urdu LughaatNLP urdunlp UrduNLP urduhack stanza natural-language-processing text-processing language-processing preprocessing stemming lemmatization tokenization stopwords',
    url='https://github.com/MuhammadNoman76/LughaatNLP'
)