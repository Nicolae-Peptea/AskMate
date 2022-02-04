<div id="top"></div>

# ASK MATE

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#main-features">Main Features</a></li>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#visuals">Visuals</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#development-team">Development Team</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![home-page.png][home-page]

Ask mate is a forum where visitors can register and login, start new discussions on different topics, respond to other topics, comment on questions and answers, and vote for answers as preffered. It's simmilar to let's say...Stack Overflow, but it's low specs version.

<p align="right">(<a href="#top">back to top</a>)</p>


### Main Features

- Register
- Login
- Sort questions
- Search key terms/phrases
- Create new question
- Answer questions
- Vote and comment on questions and answers
- Mark questions as accepted
- Delete questions, answers and comments
- Access user dashboard
- Users statistics


<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

Back End:
* [Python][python]
* [Flask][flask]

Front End:
* [HTML][html]
* [CSS][css]

Database Management:
* [PostgreSQL][postgres]

IDE:
* [Visual Studio Code][visual-studio-code]

<p align="right">(<a href="#top">back to top</a>)</p>



### Visuals

Home page:

![questions-page.png][home-page]

Home Page - Logged in:

![home-page-logged-in.png][home-page-logged-in]

Register Form:

![register-page.png][register-page]

Password validation on client side:

![passwrod-validation.png][password-validation]

Login Form:

![login-page.png][login-page]


New question from:

![new-question-page.png][new-question-page]

New Answer form:

![new-answer-page.png][new-answer-page]

Question Details:

![question-page.png][question-page]

Answers:

![comments-page.png][comments-page]

User Dashboard:

![user-dashboard-page.png][user-dashboard-page]

Users Statistics:

![users-page.png][users-page]

Tags Page:

![tags-page.png][tags-page]




<p align="right">(<a href="#top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->
## Usage

### If you'd like to have a look at the application, please, follow these steps:

- Go to the [web app][heroku-app] on Heroku
- Credentials for user login
	```
	user_name: nick_the_brick@yolo.com
	pass: L1nk1np@rk
	``` 
- Enjoy!

### If you'd like to edit and test the source code on Windows OS, please, follow these steps

- Install [Python 3.8 or higher][python]
 
- Install [PostgreSQL 14 or higher][postgres]

- In order to acccess the PSQL command line, set up the environment variables with the path of the `bin` and `lib` folders of PostgreSQL directory. Maybe this [video][set-postgres-env-vars] can give you a hand with this

- Run `psql -U postgres` in the command line and add the password you choose when installed PostgreSQL to login
- Create a database `psql CREATE DATABASE <DB_NAME>`
- Connect to the database you've just created `psql \c <DB_NAME>`
- Seed the database with the data from `\sample_data\askmatepart2-sample-data.sql` by using `psql \i <Copy realtive path of the askmatepart2-sample-data.sql>` change the `\` path separator with `/`
- Duplicate the `.env.template` and rename it to `.env`
- In the `.env` file fill these fields
	```PSQL_USER_NAME=postgres account
	PSQL_PASSWORD=postgres account password
	PSQL_HOST=localhost
	PSQL_DB_NAME=db_name_you_created 
	COOKIE_SECRET_KEY=something_random ex: gordgandoibv551150``` 
- Go to your Python folder and add both the folder and the subfolder `Scripts` paths to the environment variables
- Install [virtualenv][virtualenv] with `pip install virtualenv` from the command prompt
- Open the root directory and create a virtual environment `virtual venv venv`
- Activate the virtual environment `venv\Scripts\activate`
- Install requirements from the `requirements.txt` `pip install -r requirements.txt`
- Run `server.py`

<p align="right">(<a href="#top">back to top</a>)</p>

## Development Team

* [Mihai Buga's GitHub][mihai-buga]
* [Nicolae Peptea's GitHub][nicolae-peptea]

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Thanks for all the support to the Codecool mentors that have guided us!


<!-- MARKDOWN LINKS & IMAGES -->
[postgres]: https://www.postgresql.org/
[python]: https://www.python.org/
[flask]: https://flask.palletsprojects.com/en/2.0.x/
[html]: https://html.com/
[css]: https://www.w3.org/Style/CSS/Overview.en.html
[visual-studio-code]: https://code.visualstudio.com/
[virtualenv]: https://pypi.org/project/virtualenv/

[mihai-buga]: https://github.com/mihaibuga
[nicolae-peptea]: https://github.com/Nicolae-Peptea

[heroku-app]:https://askmate09.herokuapp.com/

[home-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602800/AskMate/home-page_miro46.png
[questions-page]:https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602789/AskMate/question-page_lvo3kn.png
[register-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602789/AskMate/register-page_vorgp0.png
[login-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602800/AskMate/login-page_kz1cyl.png
[tags-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602789/AskMate/tags-page_d3s93e.png
[home-page-logged-in]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602800/AskMate/home-page-logged-in_e4lz1f.png
[new-question-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642603336/AskMate/new_question_page_yxnw8w.png
[new-answer-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602800/AskMate/new-answer-page_o2bi10.png
[question-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642604707/AskMate/question_page_odfvk0.png
[password-validation]:https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602930/AskMate/password_validation_ej4pv9.png

[comments-page]:https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642604764/AskMate/comments_section_emlxjz.png
[user-dashboard-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602789/AskMate/user-dashboard-page_xhg3os.png
[users-page]: https://res.cloudinary.com/dqwtm9fw1/image/upload/v1642602789/AskMate/users-page_wkirhq.png
[set-postgres-env-vars]:https://www.youtube.com/watch?v=0CAzSXG6N8E&ab_channel=Chandra1947
