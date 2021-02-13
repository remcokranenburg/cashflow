#!/usr/bin/env python3

from sqlalchemy import create_engine

from models import Base

if __name__ == "__main__":
    engine = create_engine("sqlite:///generated/data.sqlite")
    Base.metadata.create_all(engine)
