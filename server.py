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
    address = url_for('ask_question')
    if request.method == "GET":
        return render_template('post_question.html', address=address)
    elif request.method == "POST":
        question_id = data_handler.add_question(new_entry=dict(request.form))
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    questions = data_handler.get_questions()
    answers = data_handler.get_answers(question_id)
    num_of_answers = len(answers)
    my_question = data_handler.get_question(questions, question_id)
    return render_template("question.html",
                           my_question=my_question,
                           answers=answers,
                           num_of_answers=num_of_answers)


@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    address = url_for('answer_question', question_id=question_id)

    if request.method == "GET":
        return render_template("post_answer.html", address=address)
    elif request.method == "POST":
        data_handler.add_answer(new_entry=dict(request.form), question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["GET"])
def delete_question(question_id):
    data_handler.delete_question(question_id)
    return redirect('/')



if __name__ == "__main__":
    app.run(debug=True)
