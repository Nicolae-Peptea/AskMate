import imghdr
import os
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename

import data_handler

question_path = ''

app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'images'


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')


@app.route("/")
@app.route("/list")
def route_list():
    questions = list(data_handler.read_file(data_handler.QUESTIONS_PATH))
    if request.args:
        order_by = request.args['order_by']
        direction = request.args['order_direction']
        ordered_questions = data_handler.get_ordered_questions(questions, order_by, direction)
        return render_template('list.html', questions=ordered_questions, order_by=order_by, direction=direction)
    return render_template('list.html', questions=questions[::-1])


@app.route('/add-question', methods=["GET", "POST"])
def ask_question():
    address = url_for('ask_question')
    if request.method == "GET":
        return render_template('post_question.html', address=address)
    elif request.method == "POST":
        new_entry = dict(request.form)
        if request.files:
            uploaded_file = request.files['image']
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            new_entry['image'] = filename
        question_id = data_handler.add_question(new_entry)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    global question_path
    files = os.listdir(app.config['UPLOAD_PATH'])
    answers = data_handler.get_answers_for_question(question_id)
    num_of_answers = len(answers)
    my_question = data_handler.get_single_question(question_id)
    question_path = url_for('display_question', question_id=question_id)
    return render_template("question.html",
                           my_question=my_question,
                           answers=answers,
                           num_of_answers=num_of_answers,
                           files=files,
                           )


@app.route('/images/<filename>')
def upload_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


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
        new_entry = dict(request.form)
        if request.files:
            uploaded_file = request.files['image']
            filename = secure_filename(uploaded_file.filename)
            if filename != '':
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
            new_entry['image'] = filename
        data_handler.add_answer(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<int:answer_id>/delete')
def delete_answer(answer_id):
    data_handler.delete_answer(answer_id)
    return redirect(question_path)


@app.route('/question/<int:question_id>/delete')
def delete_question(question_id):
    my_question = dict(data_handler.get_single_question(question_id))
    if my_question['image']:
        filename = my_question['image']
        os.unlink(os.path.join(app.config['UPLOAD_PATH'], filename))
    answers = data_handler.get_answers_for_question(question_id)
    for answer in answers:
        if answer['question_id'] == question_id:
            answer_id = answer['id']
            data_handler.delete_answer(answer_id)
            if answer['image']:
                filename = answer['image']
                os.unlink(os.path.join(app.config['UPLOAD_PATH'], filename))
    data_handler.delete_question(question_id)
    return redirect(url_for('route_list'))


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
def down_vote_answer(answer_id):
    data_handler.vote_answer(answer_id=answer_id, vote='down')
    return redirect(question_path)


if __name__ == "__main__":
    app.run(debug=True)
