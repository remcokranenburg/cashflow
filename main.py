from flask import Flask, render_template, request

from views import IngChecking

flask = Flask("cashflow")


@flask.route("/")
def index():
    return render_template('index.html')


@flask.route("/ing-checking", methods=["GET", "POST"])
def ing_checking():
    return IngChecking().as_view(request)

