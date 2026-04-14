from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base
import datetime

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    upload_date = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_info = Column(JSON, nullable=True)
