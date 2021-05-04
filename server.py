<<<<<<< HEAD
import os
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
import data_handler


app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'images'


def generate_entry_with_image(new_entry, path, operation):
    uploaded_file = request.files['image']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        if operation == 'new_question':
            filename = 'question' + str(data_handler.get_next_question_id())
        elif operation == 'new_answer':
            filename = 'answer' + str(data_handler.get_next_answer_id())
        else:
            filename = operation
        uploaded_file.save(os.path.join(path, filename))
        new_entry['image'] = filename
    return new_entry


def generate_new_entry(path, operation):
    if request.files:
        new_entry = generate_entry_with_image(dict(request.form), path, operation)
    else:
        new_entry = dict(request.form)
    return new_entry


@app.route('/images/<filename>')
def upload_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route("/")
@app.route("/list")
def route_list():
    ordered_questions = data_handler.get_ordered_questions(parameters=request.args)
    return render_template(
        'list.html',
        questions=data_handler.generate_data_without_new_line(ordered_questions),
        request_param=request.args)


# QUESTION MANIPULATION
@app.route('/add-question', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        url = url_for('ask_question')
        return render_template('manipulate_question.html', url=url)
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'], 'new_question')
        question_id = data_handler.add_question(new_entry)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    data_handler.increment_views(question_id)
    my_question = [data_handler.get_single_question(question_id)]
    answers = data_handler.get_answers_for_question(question_id)
    num_of_answers = len(answers)
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template("question_page.html",
                           my_question=my_question[0],
                           answers=data_handler.generate_data_without_new_line(answers),
                           num_of_answers=num_of_answers, files=files)


@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "GET":
        question = data_handler.get_single_question(question_id)
        url = url_for('edit_question', question_id=question['id'])
        return render_template(
            "manipulate_question.html",
            question=question,
            url=url)
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='question' + str(question_id))
        data_handler.edit_question(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    data_handler.delete_question(question_id, app.config['UPLOAD_PATH'])
    return redirect(url_for('route_list'))


@app.route('/question/<int:question_id>/vote', methods=["POST"])
def vote_question(question_id):
    vote_list = list(dict(request.form).keys())
    if 'upvote' in vote_list:
        data_handler.vote_question(question_id, vote='1')
    elif 'downvote' in vote_list:
        data_handler.vote_question(question_id, vote='-1')
    return redirect(url_for('route_list'))


# ANSWER MANIPULATION
@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    if request.method == "GET":
        return render_template("post_answer.html", question_id=question_id)
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'], 'new_answer')
        data_handler.add_answer(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    answer = data_handler.get_single_answer(answer_id)
    data_handler.delete_answer(answer_id, app.config['UPLOAD_PATH'])
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route('/answer/<int:answer_id>/vote', methods=["POST"])
def vote_answer(answer_id):
    answer = data_handler.get_single_answer(answer_id)
    vote_list = list(dict(request.form).keys())
    if 'upvote' in vote_list:
        data_handler.vote_answer(answer, vote='1')
    elif 'downvote' in vote_list:
        data_handler.vote_answer(answer, vote='-1')
    return redirect(url_for("display_question", question_id=answer['question_id']))


if __name__ == "__main__":
    app.run(debug=True)
=======
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == "__main__":
    app.run()
>>>>>>> 634448c (starter project)
