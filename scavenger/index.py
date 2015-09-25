from text_process import term_freq, clean_text
from models import Document, DocumentWord
from collections import defaultdict

class Index(object):
    '''
    self.scoring_type
    '''
    def __init__(self, searcher, reader, writer):
        self.searcher = searcher
        self.reader = reader
        self.writer = writer

    def add(self, text, doc_id):
        self.writer.add(text, doc_id)

    def bulk_add(self, documents):
        self.writer.bulk_add(documents)

    def search(self, query):
        return self.searcher.search(query)

    def commit(self):
        self.writer.commit()
        self.load_from_db()

    def load_from_db(self):
         # Refresh data in reader with data from database
        self.reader.load_from_db()

        # Push the new data into the cache
        self.writer.build_cache(self.reader.doc_word_scores)


class IndexWriter(object):

    def __init__(self, db, cache):
        self.buffer = IndexBuffer()
        self.db = db
        self.cache =cache

    def add(self, text, doc_id):
        # Convert text to dictionary of words mapping to their term frequency
        tf = term_freq(clean_text(text))

        # Get doc length by summing all term frequencies
        doc_length = reduce(lambda x, y: x + y, tf.values())

        self.buffer.add(create_document_words(tf, doc_id))
        self.buffer.add([Document(doc_id, doc_length)])

    def bulk_add(self, documents):
        for text, document_id in documents:
            self.add(text, document_id)

    def delete(self, document_id):
        doc_to_del = self.db.select_document(document_id)
        doc_words_to_del = self.db.select_document_word(document_id)

        self.buffer.delete(doc_to_del)
        self.buffer.delete(doc_words_to_del)

    def bulk_delete(self, document_ids):
        for document_id in document_ids:
            self.delete(document_id)

    def commit(self):
        # Flush buffer into the database
        self.db.insert(self.buffer.models_to_add)
        self.db.delete(self.buffer.models_to_del)
        self.buffer.flush()

    def build_cache(self, doc_word_scores):
        self.cache.build(doc_word_scores)


class IndexBuffer(object):

    def __init__(self, models_to_add=[], models_to_del=[]):
        self.models_to_add = docs_to_add
        self.models_to_del = models_to_del

    def flush():
        self.models_to_add = []
        self.models_to_del = []

    def add(models):
        self.models_to_add.extend(models)

    def delete(models):
        self.models_to_del.extend(models)


class IndexReader(object):

    def __init__(self, db, cache):
        self.db = db
        self.cache = cache
        self.docs_containing_word = {}
        self.doc_word_score = {}

    def load_from_db(self):
        documents = self.db.select_all(Document)
        document_words = self.db.select_all(DocumentWord)

        # Maps a word to number of documents containing the word
        doc_freqs = defaultdict(int)
        for dw in document_words:
            doc_freqs[dw.word] += 1

        # Maps document.id -> document.length
        doc_lengths = {d.id : d.length  for d in documents}

        # Average document length
        avgdl = reduce(lambda x,y: x + y, doc_length.values()) / doc_count
        doc_count = len(documents)

        bm25 = BM25(doc_count=doc_count, doc_freqs=doc_freqs,
                    doc_lengths=doc_lengths, avgdl=avgdl)

        # Maps document_id to a dictionary of words with their scores
        # doc_word_scores[document_id][word] = score
        self.doc_word_scores = defaultdict(defaultdict(float))
        for dw in document_words:
            self.doc_word_scores[dw.word][dw.document_id] = bm25.score(dw)

    def load_from_cache(self):
        self.doc_word_scores = self.cache.to_dict()

    def search(words):
        return {word : v for word, v in self.doc_word_scores if word in words}


'''
Notes:
3. Keep dictionary on run: need redis/memcache support for a web server
        Allow user to enter redis/memcache url

DB OPTIONS
    1. Load data from Redis into Python dictionary
    2. Always search from Redis

Make stopword list configurable
'''
