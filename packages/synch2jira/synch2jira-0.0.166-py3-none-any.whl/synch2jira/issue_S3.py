from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from synch2jira.issue import Issue
from sqlalchemy import create_engine
import config

db_url = config.database_file
Base = declarative_base()
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)


class IssueS3(Issue,Base):
    __tablename__ = 'issues'

    id = Column(Integer, primary_key=True, autoincrement=True)
    summary = Column(String)
    description = Column(String)
    updated = Column(DateTime)
    status = Column(String)
    miror = None

    def __init__(self, summary, description, updated, status):
        self.summary = summary
        self.description = description
        self.updated = updated
        self.status = status

    # def __repr__(self):
    #     return f"IssueS3(id={self.id}, summary={self.summary}, description={self.description}, updated={self.updated}, status={self.status})"

    @staticmethod
    def create(**kwargs):  # avec les argument on creee un objet et on le save
        issue = IssueS3(**kwargs)
        session.add(issue)
        session.commit()
        return issue

    @staticmethod
    def new(**kwargs):  # avec les argument on creee un objet sans le save
        return IssueS3(**kwargs)

    @staticmethod
    def all():
        return session.query(IssueS3).all()

    @staticmethod
    def first():
        return session.query(IssueS3).first()

    @staticmethod
    def last():
        return session.query(IssueS3).order_by(IssueS3.id.desc()).first()

    @staticmethod
    def find_by(**kwargs):
        return session.query(IssueS3).filter_by(**kwargs).all()

    @staticmethod
    def find_by_id(id):
        return session.query(IssueS3).filter_by(id=id).first()

    @staticmethod
    def save(instance):
        session.add(instance)
        session.commit()

    @staticmethod
    def update(instance, **kwargs):
        for key, value in kwargs.items():
            setattr(instance, key, value)
        session.commit()

    @staticmethod
    def update_all(**kwargs):
        session.query(IssueS3).update(kwargs)
        session.commit()

    @staticmethod
    def delete(instance):
        session.delete(instance)
        session.commit()

    @staticmethod
    def delete_all():
        session.query(IssueS3).delete()
        session.commit()


