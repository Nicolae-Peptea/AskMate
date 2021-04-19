from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)


@app.route("/")
@app.route("/list")
def route_list():
    questions = data_handler.get_questions()
    return render_template('list.html', questions=questions)


@app.route('/add-question', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template('post_question.html')
    elif request.method == "POST":
        # get id_
        return redirect('/question/<question_id>')
    pass

@app.route("/question/<int:question_id>")
def display_question(question_id):
    questions = data_handler.read_questions()
    for question in questions:
        if question["id"] == str(question_id):
            my_question = question
    return render_template("question.html", my_question=my_question)


@app.route("/add-question", methods=["GET", "POST"])
def ask_question():
    pass


@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    pass


if __name__ == "__main__":
    app.run()
