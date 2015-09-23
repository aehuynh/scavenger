class Scorer(object):
    def __init__(self, index):
        self.index = index

    def score(self, doc_word):
        raise NotImplementedError

    def idf(self, doc_word):
        total_doc_count = self.index.total_doc_count
        doc_freq = self.index.doc_freq(doc_word.word)

        return log(total_doc_count / (doc_freq + 1.0)) + 1.0

class BM25(Scorer):
    def __init__(self, index, k=1.2, b=0.75):
        super().__init__(index)
        self.k = k
        self.b = b

    def score(self, doc_word):
        B = self.b
        K = self.k
        tf = log(1 + doc_word.term_freq)
        idf = self.idf(doc_word)
        doc_word_count = self.index.doc_word_count(doc_word.document_id)
        avgdl = self.index.avgdl

        return idf * tf * (K + 1) /
            (tf + K +*(1 - B  + B * doc_word_count / avgdl))

class TF_IDF(Scorer):
    def __init__(self, index):
        super().__init__(index)

    def score(self, doc_word):
        # Uses term frequency in proportion to the document word count
        tf = doc_word.term_freq / self.doc_word_count(doc_word.document_id)
        idf = self.idf(doc_word)

        return tf * idf

