from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import data_handler

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'images'


def generate_entry_with_image(new_entry, path, operation, prev_entry=''):
    uploaded_file = request.files['image']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        if operation == 'new_question':
            filename = 'question' + str(data_handler.get_last_added_question_id()+1)
        elif operation == 'new_answer':
            filename = 'answer' + str(data_handler.get_last_added_answer_id()+1)
        elif operation == 'edit_question':
            filename = 'question' + str(prev_entry['id'])
        else:
            filename = operation
        uploaded_file.save(os.path.join(path, filename))
        new_entry['image'] = filename

    return new_entry


def generate_new_entry(path, operation, prev_entry=''):
    if request.files:
        new_entry = generate_entry_with_image(dict(request.form), path, operation, prev_entry)
    else:
        new_entry = dict(request.form)
    return new_entry


@app.route('/images/<filename>')
def upload_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route("/")
@app.route("/list")
def route_list():
    # print (data_handler.get_questions())
    # ordered_questions = data_handler.get_ordered_questions(parameters=request.args)
    # print(data_handler.get_questions())
    return render_template(
        'list.html',
        questions=data_handler.get_questions(),
        request_param=request.args)


# QUESTION MANIPULATION
@app.route('/add-question', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template('manipulate_question.html')
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'], 'new_question')
        data_handler.add_question(new_entry)
        question_id = data_handler.get_last_added_question_id()
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    my_question = data_handler.get_single_question(question_id)
    answers = data_handler.get_answers_for_question(question_id)
    files = os.listdir(app.config['UPLOAD_PATH'])
    question_comment = data_handler.get_comment_by_question_id(question_id)
    print(question_comment)
    return render_template("question_page.html",
                           my_question=my_question,
                           answers=answers,
                           files=files,
                           question_comment=question_comment)


@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    question = data_handler.get_single_question(question_id)
    if request.method == "GET":
        return render_template(
            "manipulate_question.html",
            question=question
        )
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'], operation='edit_question', prev_entry=question)
        data_handler.edit_question(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    data_handler.delete_question(question_id, app.config['UPLOAD_PATH'])
    return redirect(url_for('route_list'))


@app.route('/question/<int:question_id>/vote', methods=["POST"])
def vote_question(question_id):
    vote_type = ''.join(dict(request.form).keys())
    data_handler.vote_question(question_id, 'question', vote_type)
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
    question_id = data_handler.get_question_id(answer_id)
    data_handler.delete_answer(answer_id, app.config['UPLOAD_PATH'])
    return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<int:answer_id>/vote', methods=["POST"])
def vote_answer(answer_id):
    question_id = data_handler.get_question_id(answer_id)
    vote_type = ''.join(dict(request.form).keys())
    data_handler.vote_question(answer_id, 'answer', vote_type)
    return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/new-comment", methods=["GET","POST"])
def add_comment_to_question(question_id):
    if request.method == "GET":
        return render_template('manipulate_comment.html', question_id=question_id)
    else:
        comment = request.form
        data_handler.add_comment_to_question(comment, question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/answer/<int:answer_id>/new-comment", methods=["GET","POST"])
def add_comment_to_answer(answer_id):
    if request.method == "GET":
        return render_template('manipulate_comment.html', answer_id=answer_id)
    else:
        question_id = data_handler.get_question_id(answer_id)
        comment = request.form
        data_handler.add_comment_to_answer(comment, answer_id)
        return redirect(url_for("display_question", question_id=question_id))


if __name__ == "__main__":
    app.run(debug=True)
