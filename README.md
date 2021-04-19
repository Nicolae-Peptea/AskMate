# AskMate (sprint 1)

## Story

Its time to put your newly acquired Flask skills to use! Your next big task will be to implement a crowdsourced Q&A site, like Stack Overflow.

The initial version of the site should be able to handle questions and answers, there is no need for other functionality like user management or comments for questions/answers.

The management was very interested in the agile development methodologies that they just recently hear about, thus they are handing out a **prioritized list** of user stories called a product backlog. Try to estimate how many of these stories your team can finish until the demo. As the order is important, you should choose from the beginning of the list as much as you can, **the first four stories are the most important**.

## What are you going to learn?

- create a Flask project
- use routes with Flask
- use HTML and the Jinja templating engine
- CSV handling

## Tasks

1. Implement the `/list` page that displays all questions.
    - The page is available under `/list`
    - Load and display the data from `question.csv`
    - Sort the questions by the latest question on top

2. Create the `/question/<question_id>` page that displays a question and the answers for it.
    - The page is available under `/question/<question_id>`
    - There are links to the question pages from the list page
    - The page displays the question title and message
    - The page displays all the answers to a question

3. Implement a form that allows you to add a question.
    - There is an `/add-question` page with a form
    - The page is linked from the list page
    - There is a POST form with at least `title` and `message` fields
    - After submitting, you are redirected to "Display a question" page of this new question

4. Implement posting a new answer.
    - The page URL is `/question/<question_id>/new-answer`
    - The question detail page links to this page
    - The page has a POST form with a form field called `message`
    - Posting an answer redirects you back to the question detail page, and the new answer is there

5. Implement sorting for the question list.
    - The question list can be sorted by title, submission time, message, number of views, and number of votes
    - You can choose the direction: ascending or descending
    - The order is passed as query string parameters, for example `/list?order_by=title&order_direction=desc`

6. Implement deleting a question.
    - Deleting is implemented by the `/question/<question_id>/delete` endpoint
    - There should be a deletion link on the question page
    - Deleting redirects you back to the list of questions

7. Allow the user to upload an image for a question or answer.
    - The forms for adding question and answer contain an "image" file field
    - You can attach an image (.jpg, .png)
    - The image is saved on server and displayed next to question / answer
    - When you delete the question / answer, the file gets deleted as well

8. Implement editing an existing question.
    - There is a `/question/<question_id>/edit` page
    - The page is linked from the question's page
    - There is a POST form with at least `title` and `message` fields
    - The fields are pre-filled with existing question's data
    - After submitting, you are redirected back to "Display a question" page and you see the changed data

9. Implement deleting an answer.
    - Deleting is implemented by `/answer/<answer_id>/delete` endpoint
    - There should be a deletion link on the question page, next to an answer
    - Deleting redirects you back to the question detail page

10. Implement voting on questions.
    - Vote numbers are displayed next to questions on the question list page
    - There are "vote up/down" links next to questions on the question list page
    - Voting uses `/question/<question_id>/vote_up` and `/question/<question_id>/vote_down` endpoints
    - Voting up increases, voting down decreases the `vote_number` of the question by one
    - Voting redirects you back to the question list

11. Implement voting on answers.
    - Vote numbers are displayed next to answers on the question detail page
    - There are "vote up/down" links next to answers
    - Voting uses `/answer/<answer_id>/vote_up` and `/answer/<answer_id>/vote_down` endpoints
    - Voting up increases, voting down decreases the `vote_number` of the answer by one
    - Voting redirects you back to the question detail page

## General requirements

- All data should be persisted to `.csv` files. You will need a `questions.csv` for storing all questions and an `answers.csv` for storing all answers.

## Hints

### Project structure

We recommend that you split the code into modules according to clean code principles: Do not put more than 100-150 lines of code into a single file, files should contain logically the same things, etc.

For example, you could split it up to these 3+1 parts:

**Layer** | **Example filename** | **What should it do/contain?**
---|---|---
Routing layer | `server.py` | Flask stuff (server, routes, request handling, session, etc.)<br>This layer should consist of logic that is related to Flask. (with other words: this should be the only file importing from Flask)
Persistence layer | `data_manager.py` | Layer between the server and the data. Functions here should be called from the server.py and these should use generic functions from the connection.py
CSV _(later SQL)_ connection layer |  `connection.py | Common functions to read/write/append CSV files without feature specific knowledge.<br>The layer that have access to any kind of long term data storage. In this case, we use CSV files, but later on we'll change this to SQL database.
Utility "layer" | util.py | Helper functions which can be called from any other layer. (but mainly from the business logic layer)

This is just one way to structure your code, you don't have to follow it _strictly_.

### Data models

In the `sample_data` folder you'll see two sample files for questions and answers.

These look like the following (you can ignore data in the not implemented fields):

**question.csv**<br>
*id:* A unique identifier for the question<br>
*submission_time:* The UNIX timestamp when the question was posted<br>
*view_number:* How many times this question was displayed in the single question view<br>
*vote_number:* The sum of votes this question has received<br>
*title:* The title of the question<br>
*message:* The question text<br>
*image:* The path to the image for this question<br>

**answer.csv**<br>
*id:* A unique identifier for the answer<br>
*submission_time:* The UNIX timestamp when the answer was posted<br>
*vote_number:* The sum of votes this answer has received<br>
*question_id:* The id of the question this answer belongs to.<br>
*message:* The answer text<br>
*image:* the path to the image for this answer<br>

## Background materials

- <i class="far fa-exclamation"></i> [Understanding the web](project/curriculum/materials/pages/web/understanding-the-web.md)
- <i class="far fa-exclamation"></i> [Introduction to HTML](project/curriculum/materials/tutorials/introduction-to-html.md)
- <i class="far fa-exclamation"></i> [Pip and VirtualEnv](project/curriculum/materials/pages/python/pip-and-virtualenv.md)
- <i class="far fa-exclamation"></i> [A web-framework for Python: Flask](project/curriculum/materials/pages/python/python-flask.md)
- <i class="far fa-book-open"></i> [Flask documentation](http://flask.palletsprojects.com/) (the Quickstart gives a good overview)
- <i class="far fa-book-open"></i> [Jinja2 documentation](https://jinja.palletsprojects.com/en/2.10.x/templates/)
- <i class="far fa-book-open"></i> [HTML tutorials and references on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML)
- [Tips & Tricks](project/curriculum/materials/pages/web/web-with-python-tips.md)
- [About unique identifiers](project/curriculum/materials/pages/general/unique-id.md)
