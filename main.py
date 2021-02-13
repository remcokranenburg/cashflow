import csv

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, IngTransaction

app = Flask("cashflow")

engine = create_engine("sqlite:///generated/data.sqlite")
DBSession = sessionmaker(bind=engine)


def persist_data(table):
    session = DBSession()
    for row in table:
        if len(row) != 9 and len(row) != 11:
            continue
        if row[0] == "Datum":
            print("skipping header")
            continue
        session.add(IngTransaction.from_csv_line(row))
    session.commit()
    session.close()


def retrieve_data():
    session = DBSession()
    result = session.query(IngTransaction).all()
    session.close()
    return result


@app.route("/")
def index():
    return '<a href="ing-checking">ING Checking</a>'


@app.route("/ing-checking", methods=["GET", "POST"])
def ing_checking():
    upload_message = None

    if request.method == "POST" and "data.csv" in request.files:
        file_contents = request.files["data.csv"].read().decode("utf-8").split("\n")
        table = csv.reader(file_contents)
        persist_data(table)
        upload_message = "CSV file imported"

    data = retrieve_data()

    return render_template("datatable.html", page_title="ING Checking",
                           upload_message=upload_message, table=data)
