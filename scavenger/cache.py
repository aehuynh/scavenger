from redis import StrictRedis

DOCUMENT_WORD_SCORE_NAME =  "doc_word_scores:"
HOST = 'localhost'
PORT = 6379

def create_index_cache(host, port):
    params = {}
    if host is not None:
        params['host'] = host
    else:
        params['host'] = HOST

    if port is not None:
        params['port'] = port
    else:
        params['port'] = PORT

    return IndexCache(**params)

class IndexCache(object):

    def __init__(self, host, port):
        self.client = StrictRedis(host=host, port=port, db=0)


    def build(self, doc_word_scores):
        """Clears the entire store and adds all the doc_word_scores into a
        hash table in the store.

        :param doc_word_scores: dictionary of dictionaries that looks like:
                    doc_word_scores[word][doc_id] = score of word in that
                                                    document
        """
        self.reset()

        for word, doc_id_score in doc_word_scores.items():
            # Add table name to word
            word_key = DOCUMENT_WORD_SCORE_NAME + word
            self.client.hmset(word_key, doc_id_score)

        self.save_to_disk()

    def reset(self):
        """Deletes all keys in this DB.
        """
        self.client.flushdb()

    def save_to_disk(self):
        """Asyncronous write to disk for persistent storage.
        """
        self.client.bgsave()

    def to_dict(self):
        """Returns the "doc_word_scores" table in Redis in dictionary form.
        """
        doc_word_scores = {}

        for word_key in self.doc_word_scores_iter():
            # Remove the table name from the key
            word = word_key.replace(DOCUMENT_WORD_SCORE_NAME, "")

            # Grab the {doc_ids : scores} dictionary for word
            doc_word_scores[word] = self.client.hgetall(word_key)

        return doc_word_scores

    def doc_word_scores_iter(self):
        """Returns an iterator for the keys of all the words stored in Redis
        """
        return self.client.scan_iter(match=DOCUMENT_WORD_SCORE_NAME + "*")

    def is_empty(self):
        return self.client.dbsize() <= 0

    def doc_scores(self, word):
        """Returns a hash table of document_ids mapping to scores
        """
        word_key = DOCUMENT_WORD_SCORE_NAME + word
        return self.client.hgetall(word_key)
