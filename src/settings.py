from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///generated/data.sqlite")
DBSession = sessionmaker(bind=engine)
