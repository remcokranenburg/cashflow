from flask import Flask, render_template, request

from views import IngChecking

app = Flask("cashflow")


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/ing-checking", methods=["GET", "POST"])
def ing_checking():
    return IngChecking().as_view(request)

