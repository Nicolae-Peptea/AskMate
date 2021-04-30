import os
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)
from werkzeug.utils import secure_filename
import data_handler


app = Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'images'


def generate_entry_with_image(new_entry, path):
    uploaded_file = request.files['image']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        uploaded_file.save(os.path.join(path, filename))
    new_entry['image'] = filename
    return new_entry


def generate_new_entry(path):
    if request.files:
        new_entry = generate_entry_with_image(dict(request.form), path)
    else:
        new_entry = dict(request.form)
    return new_entry


@app.route("/")
@app.route("/list")
def route_list():
    ordered_questions = data_handler.get_ordered_questions(parameters=request.args)
    return render_template('list.html', questions=data_handler.new_line_for_html(ordered_questions),
                           request_param=request.args)


@app.route('/add-question', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template('post_question.html')
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'])
        question_id = data_handler.add_question(new_entry)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>")
def display_question(question_id):
    data_handler.increment_views(question_id)
    my_question = [data_handler.get_single_question(question_id)]
    answers = data_handler.get_answers_for_question(question_id)
    num_of_answers = len(answers)
    files = os.listdir(app.config['UPLOAD_PATH'])
    return render_template("question.html",
                           my_question=my_question[0],
                           answers=data_handler.new_line_for_html(answers),
                           num_of_answers=num_of_answers, files=files)


@app.route('/images/<filename>')
def upload_image(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)


@app.route("/question/<int:question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    if request.method == "GET":
        return render_template("edit_question.html", question=data_handler.get_single_question(question_id))
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'])
        data_handler.edit_question(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route("/question/<int:question_id>/new-answer", methods=["GET", "POST"])
def answer_question(question_id):
    if request.method == "GET":
        return render_template("post_answer.html", question_id=question_id)
    elif request.method == "POST":
        new_entry = generate_new_entry(app.config['UPLOAD_PATH'])
        data_handler.add_answer(new_entry=new_entry, question_id=question_id)
        return redirect(url_for("display_question", question_id=question_id))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    answer = data_handler.get_single_answer(answer_id)
    data_handler.delete_answer(answer_id, app.config['UPLOAD_PATH'])
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    data_handler.delete_question(question_id, app.config['UPLOAD_PATH'])
    return redirect(url_for('route_list'))


@app.route('/question/<int:question_id>/vote_up', methods=["POST"])
def up_vote_question(question_id):
    data_handler.vote_question(question_id, vote='up')
    return redirect(url_for('route_list'))


@app.route('/question/<int:question_id>/vote_down', methods=["POST"])
def down_vote_question(question_id):
    data_handler.vote_question(question_id, vote='down')
    return redirect(url_for('route_list'))


@app.route('/answer/<int:answer_id>/vote_up', methods=["POST"])
def up_vote_answer(answer_id):
    answer = data_handler.get_single_answer(answer_id)
    data_handler.vote_answer(entry_to_vote=answer, vote='up')
    return redirect(url_for("display_question", question_id=answer['question_id']))


@app.route('/answer/<int:answer_id>/vote_down', methods=["POST"])
def down_vote_answer(answer_id):
    answer = data_handler.get_single_answer(answer_id)
    data_handler.vote_answer(entry_to_vote=answer, vote='down')
    return redirect(url_for("display_question", question_id=answer['question_id']))


if __name__ == "__main__":
    app.run(debug=True)
