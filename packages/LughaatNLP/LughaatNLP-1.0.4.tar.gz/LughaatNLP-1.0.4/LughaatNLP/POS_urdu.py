import json
import Levenshtein
from typing import Mapping
import logging
import re
import os
import json
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle
import numpy as np
import pkg_resources

    
class POS_urdu:
    def __init__(self):
        # Load NER model
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)  # Set logging level to INFO
        self.max_sequence_length = 281
        model_path = pkg_resources.resource_filename(__name__, 'pos_model.h5')
        self.model = load_model(model_path)

        # Load word to index mapping (pickle file)
        word2index_file = pkg_resources.resource_filename(__name__, 'word2index.pkl')
        with open(word2index_file, 'rb') as f:
            self.word2index = pickle.load(f)

        tag2index_file = pkg_resources.resource_filename(__name__, 'tag2index.pkl')
        with open(tag2index_file, 'rb') as f:
            self.tag2index = pickle.load(f)

    
    def remove_whitespace(self, text: str) -> str:
        # Remove extra whitespaces
        return ' '.join(text.split())
        
    
        
    def preserve_special_characters(self, text: str) -> str:
        # Preserve special characters like ! @ # $ & * - _ = +
        special_characters_pattern = r'(?<=[!@#$&*=_+,.؟۔-])|(?=[!@#$&*=_+,.؟۔-])'
        text = re.sub(special_characters_pattern, ' ', text)
        return self.remove_whitespace(text)

    def urdu_tokenize(self, text: str) -> str:
        text = self.remove_whitespace(text)
        text = self.preserve_special_characters(text)
        pattern = '[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]+|\d+|[^\w\s]'
        tokens = re.findall(pattern, text)
        return tokens
    
    
    def pos_tags_urdu(self, sentence):
        # Tokenize using urdu_tokenize from LughaatNLP
        sentence_tokens = self.urdu_tokenize(sentence)
        
        # Convert tokens to indices
        sentence_indices = [self.word2index.get(word, self.word2index['-OOV-']) for word in sentence_tokens]
        
        # Pad sequence to maximum length
        padded_sequence = pad_sequences([sentence_indices], maxlen=self.max_sequence_length, padding='post')
        
        # Predict POS tags using the model
        predictions = self.model.predict(padded_sequence)
        
        # Decode predicted tag indices to POS tags
        predicted_tags_indices = np.argmax(predictions, axis=-1)[0]
        predicted_tags = [list(self.tag2index.keys())[list(self.tag2index.values()).index(tag_idx)] for tag_idx in predicted_tags_indices]
        
        # Create list of dictionaries containing word and corresponding POS tag
        result = []
        for word, pos_tag in zip(sentence_tokens, predicted_tags):
            result.append({'Word': word, 'POS_Tag': pos_tag})
        
        return result

