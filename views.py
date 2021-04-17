import csv

from flask import render_template
from sqlalchemy import func, inspect
from sqlalchemy.sql import select, text

from models import Base, IngTransaction, MeesmanBalance
from settings import DBSession


def year_month(model):
    return func.date(model.date, "start of month")


class Balance:
    page_title = "Balance"
    upload_message = None

    def retrieve_data(self):
        session = DBSession()

        statement = text("""
            with
                ing_checking as (
                    select distinct
                        date(date, 'start of month') as month,
                        last_value(balance_after_mutation)
                            over (partition by date(date, 'start of month'))
                            as balance
                    from ingtransactions
                    order by date
                ),
                meesman as (
                    select distinct
                        date(date, 'start of month') as month,
                        last_value(value)
                            over (partition by date(date, 'start of month'))
                            as balance
                    from meesmanbalances
                    order by date
                )
            select
                ing_checking.month,
                ing_checking.balance as ing_checking,
                meesman.balance as meesman,
                (
                    coalesce(ing_checking.balance, 0)
                    + coalesce(meesman.balance, 0)
                ) as net_worth
            from ing_checking
            left outer join meesman on ing_checking.month=meesman.month
        """)

        result = list(session.execute(statement))
        session.close()
        return result

    def as_view(self, request):

        data = self.retrieve_data()
        columns = data[0].keys() if len(data) > 0 else []

        return render_template("datatable.html",
                               page_title=self.page_title,
                               columns=columns,
                               table=data)


class Datatable:
    model = None
    page_title = "Table"
    upload_message = None

    def persist_data(self, table):
        session = DBSession()

        for i, row in enumerate(table):
            if len(row) == 0:
                continue

            if i == 0:
                print("skipping header")
                continue

            session.add(self.model.from_csv_line(row))

        session.commit()
        session.close()

    def retrieve_data(self):
        session = DBSession()
        result = (session.query(self.model)
                  .order_by(self.model.date)
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
                               columns=inspect(self.model).columns.keys(),
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


class IngChecking(Datatable):
    model = IngTransaction
    page_title = "ING Checking"


class Meesman(Datatable):
    model = MeesmanBalance
    page_title = "Meesman"
