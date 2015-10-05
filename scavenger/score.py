from math import log

class Scorer(object):

    def __init__(self, doc_count, doc_freqs, doc_lengths, avgdl):
        self.doc_count = doc_count
        self.doc_freqs = doc_freqs
        self.doc_lengths = doc_lengths
        self.avgdl = avgdl

    def score(self, doc_word):
        raise NotImplementedError

    def tf(self, doc_word):
        # Term frequency in normalized by the total document word count
        return doc_word.count / self.doc_lengths[doc_word.document_id]

    def idf(self, doc_word):
        doc_freq = self.doc_freqs[doc_word.word]

        return log(self.doc_count / (doc_freq + 1.0)) + 1.0

class BM25(Scorer):

    def __init__(self, b=0.75, k=1.2, **kwargs):
        super().__init__(**kwargs)
        self.k = k
        self.b = b

    def score(self, doc_word):
        B = self.b
        K = self.k
        TF = self.tf(doc_word)
        IDF = self.idf(doc_word)
        doc_length = self.doc_lengths[doc_word.document_id]
        avgdl = self.avgdl

        return IDF * TF * (K+1) / (TF + K * (1 - B  + B * doc_length / avgdl))

class TF_IDF(Scorer):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def score(self, doc_word):
        TF = self.tf(doc_word)
        IDF = self.idf(doc_word)

        return TF * IDF
