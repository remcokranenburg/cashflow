import csv

from flask import render_template
from sqlalchemy import func

from models import Base, IngTransaction
from settings import DBSession


class Balance:
    page_title = "Balance"
    upload_message = None

    def retrieve_data(self):
        session = DBSession()
        year_month = func.date(IngTransaction.date, "start of month")
        result = (
            session.query(
                year_month,
                func.sum(IngTransaction.amount)
                    .over(partition_by=year_month),
                func.last_value(IngTransaction.balance_after_mutation)
                    .over(partition_by=year_month)
            )
            .distinct(IngTransaction.date)
            .order_by(IngTransaction.date)
            .all()
        )
        session.close()
        return result

    def as_view(self, request):

        data = self.retrieve_data()

        return render_template("balance.html", page_title=self.page_title,
                               table=data)


class IngChecking:
    page_title = "ING Checking"
    upload_message = None

    def persist_data(self, table):
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

    def retrieve_data(self):
        session = DBSession()
        result = (session.query(IngTransaction)
                  .order_by(IngTransaction.date)
                  .all())
        session.close()
        return result

    def as_view(self, request):
        self.request = request

        if request.method == "POST":
            self.process_post()

        data = self.retrieve_data()
        return render_template("datatable.html", page_title=self.page_title,
                               upload_message=self.upload_message, table=data)

    def process_post():
        upload_message = None

        if "data.csv" in request.files:
            file = self.request.files["data.csv"]
            file_contents = file.read().decode("utf-8").split("\n")
            table = csv.reader(file_contents)
            self.persist_data(table)
            self.upload_message = "CSV file imported"

