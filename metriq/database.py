from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from metriq.models import Base

engine = create_engine("sqlite:///metriq.db")

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
