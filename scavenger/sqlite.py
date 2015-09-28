from sqlalchemy.orm import relationship,sessionmaker
from sqlalchemy import create_engine

from models import Document, DocumentWord

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
        enginee = create_engine(selfurl)
        session = sessionmaker()
        session.configure(bind=engine)
        Base.metadata.create_all(engine)
        return session()

    def select_all(model_type):
        return self.session.query(model_type)

    def select_document(doc_id):
        return self.session.query.(Document).filter(Document.id==doc_id)

    def select_document_word(doc_id):
        return self.session.query.(DocumentWord).filter(DocumentWord.document_id==doc_id)

    def insert(models):
        for model in models:
            self.session.add(model)
        self.session.commit()

    def delete(models):
        for model in models:
            self.session.delete(model)
        self.session.commit()

    def delete_all(self):
        """Delete all Documents and DocumentWords.
        """
        self.delete(self.select_all(Document))
        self.delete(self.select_all(DocumentWord))
