from flask import Flask, render_template, request

from views import Balance, IngChecking, Meesman

app = Flask("cashflow")


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/balance")
def balance():
    return Balance().as_view(request)


@app.route("/ing-checking", methods=["GET", "POST"])
def ing_checking():
    return IngChecking().as_view(request)

@app.route("/meesman", methods=["GET", "POST"])
def meesman():
    return Meesman().as_view(request)

