from flask import Flask, render_template, request, redirect, url_for

import data_handler

app = Flask(__name__)
question_path = ''


@app.route("/")
@app.route("/list")
def route_list():
    questions = list(data_handler.read_file(data_handler.QUESTIONS_PATH))
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
    global question_path
    answers = data_handler.get_answers_for_question(question_id)
    num_of_answers = len(answers)
    my_question = data_handler.get_single_question(question_id)
    question_path = url_for('display_question', question_id=question_id)
    print (question_path)
    return render_template("question.html",
                           my_question=my_question,
                           answers=answers,
                           num_of_answers=num_of_answers)


@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    address = url_for('edit_question', question_id=question_id)
    if request.method == "GET":
        return render_template('post_question.html', address=address,
                               question=data_handler.get_single_question(question_id)
                               )
    elif request.method == "POST":
        data_handler.edit_question(new_entry=dict(request.form), question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    address = url_for('answer_question', question_id=question_id)
    if request.method == "GET":
        return render_template("post_answer.html", address=address)
    elif request.method == "POST":
        data_handler.add_answer(new_entry=dict(request.form), question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    data_handler.delete_question(question_id)
    return redirect('/')


@app.route('/answer/<int:answer_id>/delete')
def delete_answer(answer_id):
    data_handler.delete_answer(answer_id)
    return redirect(question_path)


@app.route('/question/<int:question_id>/vote_up')
def up_vote_question(question_id):
    data_handler.vote_question(question_id, vote='up')
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/question/<int:question_id>/vote_down')
def down_vote_question(question_id):
    data_handler.vote_question(question_id, vote='down')
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote_up')
def up_vote_answer(answer_id):
    data_handler.vote_answer(answer_id=answer_id, vote='up')
    return redirect(question_path)


@app.route('/answer/<int:answer_id>/vote_down')
def up_vote_answer(answer_id):
    data_handler.vote_answer(answer_id=answer_id, vote='down')
    return redirect(question_path)


if __name__ == "__main__":
    app.run(debug=True)
