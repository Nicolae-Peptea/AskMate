from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)


@app.route("/list")
def route_list():
    questions = data_handler.read_questions()
    return render_template("list.html", questions=questions)


if __name__ == "__main__":
    app.run()
