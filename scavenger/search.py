from text_process import clean_text
from nltk import word_tokenize

class Searcher(object):

    def __init__(self, index_reader):
        self.index_reader = index_reader

    def search(self, query):
        """Searches the index for the query.

        Returns a list of dictiories containing keys "document_id" and
        "score" sorted in descending order.
        """
        words = word_tokenize(clean_text(query))

        results = self.index_reader.search(words)

        doc_scores_sum = defaultdict(float)

        for word, doc_scores in results:
            for doc_id, score in doc_scores:
                doc_scores_sum[doc_id] += score

        # Sort all the doc_ids by the score descending
        sorted_doc_ids = sorted(doc_scores_sum, key=doc_scores_sum.get,
                                reverse=True)

        return [{"document_id" : doc_id, "score" : doc_scores_sum[k]}
                    for doc_id in sorted_doc_ids]
