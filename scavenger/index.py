from text_process import word_freq, clean_text
from models import Document, DocumentWord
from search import Searcher
from redis import IndexCache, create_index_cache
from sqlite import IndexStore, create_index_store

from collections import defaultdict


class Index(object):

    def __init__(self, cache_host=None, cache_port=None, db_file_path=None,
                 db_url=None):
        cache = create_index_cache(host=cache_host, port=cache_port)
        db = create_index_store(file_path=db_file_path, url=db_url)

        self.reader = IndexReader(db, cache)
        self.writer = IndexWriter(db, cache)
        self.searcher = Searcher(self.reader)

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

    def writer(self):
        return self.writer

    def reader(self):
        return self.reader


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
        return {word : self.doc_word_scores[word] for word in words if word in self.doc_word_scores}

class IndexWriter(object):

    def __init__(self, db, cache):
        self.buffer = IndexBuffer()
        self.db = db
        self.cache =cache

    def add(self, text, doc_id):
        # Convert text to dictionary of words mapping to their term frequency
        wf = word_freq(clean_text(text))

        # Get doc length by summing all term frequencies
        doc_length = reduce(lambda x, y: x + y, wf.values())

        self.buffer.add(create_document_words(tf, doc_id))
        self.buffer.add([Document(doc_id, doc_length)])

    def add_bulk(self, documents):
        for text, document_id in documents:
            self.add(text, document_id)

    def delete(self, document_id):
        doc_to_del = self.db.select_document(document_id)
        doc_words_to_del = self.db.select_document_word(document_id)

        self.buffer.delete(doc_to_del)
        self.buffer.delete(doc_words_to_del)

    def delete_bulk(self, document_ids):
        for document_id in document_ids:
            self.delete(document_id)

    def commit(self):
        # Flush buffer into the database
        models_to_add, models_to_del = self.buffer.flush()
        self.db.insert(models_to_add)
        self.db.delete(models_to_del)

    def build_cache(self, doc_word_scores):
        self.cache.build(doc_word_scores)


class IndexBuffer(object):
    """Represents the Document and DocumentWord objects to be added or
    deleted from the database on commit.
    """

    def __init__(self, models_to_add=[], models_to_del=[]):
        self.models_to_add = models_to_add
        self.models_to_del = models_to_del

    def flush():
        """Removes and returns the content in the buffer.
        """
        content = (self.models_to_add, self.models_to_del)

        self.models_to_add = []
        self.models_to_del = []

        return content

    def add(models):
        self.models_to_add.extend(models)

    def delete(models):
        self.models_to_del.extend(models)

