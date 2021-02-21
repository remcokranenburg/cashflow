#!/usr/bin/env python3

from models import Base
from settings import engine


if __name__ == "__main__":
    Base.metadata.create_all(engine)
