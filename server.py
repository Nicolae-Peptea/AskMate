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
    question_db = data_handler.get_questions()

    if request.method == "GET":
        return render_template('post_question.html')
    elif request.method == "POST":
        data_handler.add_entry(old_entries=question_db,
                               new_entry=list(request.form.items()),
                               question_or_answer='question')
        question_id = data_handler.get_id()
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    questions = data_handler.get_questions()
    answers = data_handler.get_answers(question_id)
    num_of_answers = len(answers)
    my_question = data_handler.get_answer(questions, question_id)
    return render_template("question.html",
                           my_question=my_question,
                           answers=answers,
                           num_of_answers=num_of_answers)


@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    answers = data_handler.get_answers(question_id)

    if request.method == "GET":
        return render_template("post_answer.html")
    if request.method == "POST":
        data_handler.add_entry(old_entries=answers,
                               new_entry=list(request.form.items()),
                               question_or_answer='answer')
        return redirect(url_for("display_question", question_id=question_id))


if __name__ == "__main__":
    app.run()
