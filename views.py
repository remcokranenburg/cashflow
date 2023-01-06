import csv

from gi.repository import Gtk, Gio, GObject, GLib

from sqlalchemy import func, inspect
from sqlalchemy.sql import select, text

from models import Base, IngTransaction, MeesmanBalance
from settings import DBSession


def year_month(model):
    return func.date(model.date, "start of month")


class BalanceRecord(GObject.GObject):
    def __init__(self, date: str, ing_checking: float, meesman: float,
            net_worth: float):
        super().__init__()
        self._date = date
        self._ing_checking = ing_checking
        self._meesman = meesman
        self._net_worth = net_worth

    @staticmethod
    def get_factory(property_name: str):
        ui_description = f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <interface>
                <template class="GtkListItem">
                    <property name="child">
                        <object class="GtkLabel">
                            <property name="xalign">0</property>
                            <binding name="label">
                                <lookup name="{property_name}" type="views+BalanceRecord">
                                    <lookup name="item">GtkListItem</lookup>
                                </lookup>
                            </binding>
                        </object>
                    </property>
                </template>
            </interface>
            """
        ui_bytes = GLib.Bytes.new(ui_description.encode("utf-8"))
        return Gtk.BuilderListItemFactory.new_from_bytes(None, ui_bytes)

    @GObject.Property(type=str)
    def date(self):
        return self._date

    @GObject.Property(type=float)
    def ing_checking(self):
        return self._ing_checking

    @GObject.Property(type=float)
    def meesman(self):
        return self._meesman

    @GObject.Property(type=float)
    def net_worth(self):
        return self._net_worth


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

    def as_view(self):
        data = self.retrieve_data()
        columns = data[0].keys() if len(data) > 0 else []

        print("data:", data)

        balance_list = Gio.ListStore.new(BalanceRecord)

        for record in data:
            balance_list.append(BalanceRecord(*record))

        selection = Gtk.SingleSelection.new(balance_list)
        view = Gtk.ColumnView.new(selection)

        columns = [
            Gtk.ColumnViewColumn.new("Date", BalanceRecord.get_factory("date")),
            Gtk.ColumnViewColumn.new("ING Checking", BalanceRecord.get_factory("ing_checking")),
            Gtk.ColumnViewColumn.new("Meesman", BalanceRecord.get_factory("meesman")),
            Gtk.ColumnViewColumn.new("Net Worth", BalanceRecord.get_factory("net_worth")),
        ]

        for column in columns:
            view.append_column(column)

        return view


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
