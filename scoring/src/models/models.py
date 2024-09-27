from sqlalchemy import Column, Integer, String


from .database import Base


class ApplicationScored(Base):
    __tablename__ = 'application_scored'

    scoring_id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer)
    status = Column(String)
