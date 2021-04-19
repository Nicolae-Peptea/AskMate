from flask import Flask, render_template, redirect, request
import data_handler

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def list_questions():
    return render_template('list.html')


@app.route("/question/<int:question_id>")
def display_question(quenstion_id):
    pass

if __name__ == "__main__":
    app.run()
