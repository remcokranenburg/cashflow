from datetime import date

from sqlalchemy import Column, Date, Integer, Numeric, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def parse_date(txt):
    return date(int(txt[0:4]), int(txt[4:6]), int(txt[6:8]))


def parse_amount(sign, value):
    value = value.replace(".", "").replace(",", ".")
    return float(value) if sign == "Bij" else -float(value)


class IngTransaction(Base):
    __tablename__ = "ingtransactions"

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    name = Column(String)
    account = Column(String)
    other_account = Column(String)
    code = Column(String)
    amount = Column(Numeric)
    mutation_kind = Column(String)
    description = Column(String)
    balance_after_mutation = Column(Numeric)
    tag = Column(String)

    @classmethod
    def from_csv_line(cls, csv_line):
        return cls(date=parse_date(csv_line[0]),
                   name=csv_line[1],
                   account=csv_line[2],
                   other_account=csv_line[3],
                   code=csv_line[4],
                   amount=parse_amount(csv_line[5], csv_line[6]),
                   mutation_kind=csv_line[7],
                   description=csv_line[8],
                   balance_after_mutation=csv_line[9] if len(csv_line) > 9 else 0,
                   tag=csv_line[10] if len(csv_line) > 10 else "")
