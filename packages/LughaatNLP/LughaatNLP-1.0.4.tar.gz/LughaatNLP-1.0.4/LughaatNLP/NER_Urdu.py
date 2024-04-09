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

class NER_Urdu:
    def __init__(self):
        # Load NER model
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)  # Set logging level to INFO
        model_path = pkg_resources.resource_filename(__name__, 'NER_Model.h5')
        self.model = load_model(model_path)

        # Load word to index mapping
        word2index_data = pkg_resources.resource_string(__name__, 'word2index.json')
        self.word2index = json.loads(word2index_data)

        # Load tag to index mapping
        tag2index_data = pkg_resources.resource_string(__name__, 'tag2index.json')
        self.tag2index = json.loads(tag2index_data)

    def logits_to_tokens(self, logits, index_to_tag):
        predictions = []
        for logit in logits[0]:
            tag_index = logit.argmax()
            predictions.append(index_to_tag[tag_index])
        return predictions
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

    def ner_tags_urdu(self, sentence):
        # Tokenize the input sentence
        sentence_words = self.urdu_tokenize(sentence)

        # Convert words to corresponding indices
        sentence_indices = []
        for word in sentence_words:
            if word in self.word2index:
                sentence_indices.append(self.word2index[word])
            else:
                sentence_indices.append(self.word2index['-OOV-'])

        # Pad the sequence to the maximum length
        padded_sentence_indices = pad_sequences([sentence_indices], maxlen=101, padding='post')

        # Predict using the model
        predictions = self.model.predict(padded_sentence_indices)

        # Convert predicted indices to tag labels
        predicted_tags = self.logits_to_tokens(predictions, {i: t for t, i in self.tag2index.items()})

        # Create a dictionary of word and predicted tag
        word_tag_dict = {word: tag for word, tag in zip(sentence_words, predicted_tags[:len(sentence_words)])}

        return word_tag_dict