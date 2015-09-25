from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    """Represents a simple text document.
    """
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, nullable=False)

class DocumentWord(Base):
    """Represents a unique word in a document. It is mainly used to store the
    number of times the word appears in a particular document.
    """
    __tablename__ = 'document_words'
    id = Column(Integer, primary_key=True)
    word = Column(String, nullable=False)
    count = Column(Integer, nullable=False)
    document_id = Column(Integer, ForeighKey('documents.id'))

def create_document_words(self, word_counts, doc_id):
    """Creates a list of DocumentWords.

    :param word_counts: dictionary mapping words to number of times they
                        appear in the Document with doc_id
    """
    return [DocumentWord(word=word, id=doc_id, count=count, document_id=doc_id)
            for word, count in word_counts]
