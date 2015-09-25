from nltk.corpus import stopwords
import string
from nltk.tag import pos_tag
from nltk import word_tokenize, PorterStemmer

_stemmer = PorterStemmer()

def term_freq(text):
    d = defultdict(int)
    for word in word_tokenize(text):
        d[word] += 1

    return d

def clean_text(s):
    s = s.lower()
    clean_methods = [remove_punc, remove_numbers, remove_stopwords, stem_text]
    return clean_text_with(s, clean_methods)

def clean_text_with(s, clean_methods):
    for method in clean_methods:
        s = method(s)
    return s

def remove_punc(text):
    return text.translate({ord(c): None for c in string.punctuation})

def remove_numbers(text):
    return ''.join([i for i in text if not i.isdigit()])

def remove_stopwords(text, lang='english'):
    return ' '.join(filter(lambda x: x.lower() not in stopwords.words(lang), word_tokenize(text)))

def stem_text(s):
    return ' '.join(map(_stemmer.stem, word_tokenize(s)))
