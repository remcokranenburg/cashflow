#!/usr/bin/env python3

import sys

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, GLib

from views import Balance


def on_activate(application: Gtk.Application):
    window = Gtk.ApplicationWindow(application=application, title="Cashflow")
    window.set_default_size(600, 250)

    header = Gtk.HeaderBar()
    window.set_titlebar(header)

    balance_view = Balance().as_view()

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.set_child(balance_view)

    window.set_child(scrolled_window)
    window.present()


def main(argv: list[str]):
    application = Gtk.Application(application_id="com.remcokranenburg.Cashflow")
    application.connect("activate", on_activate)
    application.run(argv)


if __name__ == "__main__":
    main(sys.argv)


"""
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
"""
