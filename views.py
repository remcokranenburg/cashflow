import csv

from flask import render_template
from sqlalchemy import func, inspect

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
                year_month
                    .label("month"),
                func.sum(IngTransaction.amount)
                    .over(partition_by=year_month)
                    .label("amount"),
                func.last_value(IngTransaction.balance_after_mutation)
                    .over(partition_by=year_month)
                    .label("balance")
            )
            .distinct(IngTransaction.date)
            .order_by(IngTransaction.date)
            .all()
        )
        session.close()
        return result

    def as_view(self, request):

        data = self.retrieve_data()
        columns = data[0].keys() if len(data) > 0 else []

        return render_template("datatable.html",
                               page_title=self.page_title,
                               columns=columns,
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
        return render_template("datatable.html",
                               page_title=self.page_title,
                               upload_form_visible=True,
                               upload_message=self.upload_message,
                               columns=inspect(IngTransaction).columns.keys(),
                               table=data)

    def process_post(self):
        upload_message = None

        if "data.csv" in self.request.files:
            file = self.request.files["data.csv"]
            file_contents = file.read().decode("utf-8")
            dialect = csv.Sniffer().sniff(file_contents)
            table = csv.reader(file_contents.split("\n"), dialect)
            self.persist_data(table)
            self.upload_message = "CSV file imported"

