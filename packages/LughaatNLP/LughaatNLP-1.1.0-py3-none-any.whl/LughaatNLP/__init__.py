# This file is required to treat the directory as a Python package

# Import the LughaatNLP class from LughaatNLP module
from .LughaatNLP import LughaatNLP
import pkg_resources

def __init__(self):
    self.logger = logging.getLogger(__name__)
    lemma_data = pkg_resources.resource_string(__name__, 'Urdu_Lemma.json')
    self.lemmatization_dict = json.loads(lemma_data)

    stopwords_data = pkg_resources.resource_string(__name__, 'stopwords.json')
    self.stopwords_data = json.loads(stopwords_data)

    tokenizer_data = pkg_resources.resource_string(__name__, 'tokenizer.json')
    self.tokenizer_word_index = json.loads(tokenizer_data)
    # ... (rest of the code)

# Define __all__ to specify which modules get imported when using `from LughaatNLP import *`
__all__ = ['LughaatNLP']
