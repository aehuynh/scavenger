from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from models import Document, DocumentWord

Base = declarative_base()

#basedir = os.path.abspath(os.path.dirname(__file__))

FILE_PATH='/ScavengerIndex.db'

def create_index_store(file_path, url):

    params = {}
    if file_path is not None:
        return IndexStore(file_path, url)
    else:
        return IndexStore(FILE_PATH, url)

class IndexStore(object):

    def __init__(self, file_path, url=None):
        # file_path is not needed if url is set
        if url is None:
            self.url = 'sqlite://' + file_path
        else:
            self.url = url
        self.session = self.session()

    def session(self):
        engine = create_engine(self.url)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        return session()

    def select_all(self, model_type):
        return self.session.query(model_type).all()

    def select_document(self, doc_id):
        return self.session.query(Document).filter(Document.id==doc_id)

    def select_document_word(self, doc_id):
        return self.session.query(DocumentWord).filter(DocumentWord.document_id==doc_id)

    def insert(self, models):
        for model in models:
            self.session.add(model)
        self.session.commit()

    def delete(self, models):
        for model in models:
            self.session.delete(model)
        self.session.commit()

    def delete_all(self):
        """Delete all Documents and DocumentWords.
        """
        self.delete(self.select_all(Document))
        self.delete(self.select_all(DocumentWord))
