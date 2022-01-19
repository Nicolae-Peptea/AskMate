--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.6
-- Dumped by pg_dump version 9.5.6

ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS pk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS pk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.answer DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS pk_comment_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_answer_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.comment DROP CONSTRAINT IF EXISTS fk_user_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS pk_question_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_question_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.tag DROP CONSTRAINT IF EXISTS pk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.question_tag DROP CONSTRAINT IF EXISTS fk_tag_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS pk_users_id CASCADE;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_email_key CASCADE;


DROP TABLE IF EXISTS public.users;
CREATE TABLE users (
    id serial NOT NULL,
    registration_time timestamp without time zone,
    email text UNIQUE,
    password text,
    reputation int default 0
);



DROP TABLE IF EXISTS public.question;
CREATE TABLE question (
    id serial NOT NULL,
    uuid text NOT NULL,
    user_id integer,
    submission_time timestamp without time zone,
    view_number integer default 0,
    vote_number integer default 0,
    title text,
    message text,
    image text
);

DROP TABLE IF EXISTS public.answer;
CREATE TABLE answer (
    id serial NOT NULL,
    uuid text NOT NULL,
    user_id integer,
    submission_time timestamp without time zone,
    vote_number integer default 0,
    question_id integer,
    message text,
    image text,
    accepted_by_user int DEFAULT 0
);

DROP TABLE IF EXISTS public.comment;
CREATE TABLE comment (
    id serial NOT NULL,
    uuid text NOT NULL,
    user_id integer,
    question_id integer,
    answer_id integer,
    message text,
    submission_time timestamp without time zone,
    edited_count integer default 0
);


DROP TABLE IF EXISTS public.question_tag;
CREATE TABLE question_tag (
    question_id integer NOT NULL,
    tag_id integer NOT NULL
);

DROP TABLE IF EXISTS public.tag;
CREATE TABLE tag (
    id serial NOT NULL,
    name text
);


ALTER SEQUENCE users_id_seq RESTART WITH 1 increment by 1;
ALTER SEQUENCE question_id_seq RESTART WITH 1 increment by 1;
ALTER SEQUENCE answer_id_seq RESTART WITH 1 increment by 1;
ALTER SEQUENCE comment_id_seq RESTART WITH 1 increment by 1;
ALTER SEQUENCE tag_id_seq RESTART WITH 1 increment by 1;


ALTER TABLE ONLY answer
    ADD CONSTRAINT pk_answer_id PRIMARY KEY (id);

ALTER TABLE ONLY comment
    ADD CONSTRAINT pk_comment_id PRIMARY KEY (id);

ALTER TABLE ONLY question
    ADD CONSTRAINT pk_question_id PRIMARY KEY (id);

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT pk_question_tag_id PRIMARY KEY (question_id, tag_id);

ALTER TABLE ONLY tag
    ADD CONSTRAINT pk_tag_id PRIMARY KEY (id);

ALTER TABLE ONLY users
    ADD CONSTRAINT pk_users_id PRIMARY KEY (id);


ALTER TABLE ONLY question
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_answer_id FOREIGN KEY (answer_id) REFERENCES answer(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY answer
    ADD CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY comment
    ADD CONSTRAINT fk_question_id FOREIGN KEY (question_id) REFERENCES question(id)
        ON DELETE CASCADE;

ALTER TABLE ONLY question_tag
    ADD CONSTRAINT fk_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id)
        ON DELETE CASCADE;


INSERT INTO users (registration_time, email, password, reputation)
VALUES ('2017-04-25 14:55:00', 'ion@doe.com', 'maricica', 25);
INSERT INTO users (registration_time, email, password, reputation)
VALUES ('2017-04-29 14:55:00', 'gigel@doe.com', 'ioana', 25);



INSERT INTO question (uuid, user_id, submission_time, view_number, vote_number, title, message, image)
            VALUES ('avdsabfd5864', 1, '2017-04-28 08:29:00', 29, 7, 'How to make lists in Python?', 'I am totally new to this, any hints?', NULL);
INSERT INTO question (uuid, user_id, submission_time, view_number, vote_number, title, message, image)
            VALUES ('fvcgfdxhgfgfchgf', 1, '2017-04-29 09:19:00', 15, 9, 'Wordpress loading multiple jQuery Versions', 'I developed a plugin that uses the jquery booklet plugin (http://builtbywill.com/booklet/#/) this plugin binds a function to $ so I cann call $(".myBook").booklet();

I could easy managing the loading order with wp_enqueue_script so first I load jquery then I load booklet so everything is fine.

BUT in my theme i also using jquery via webpack so the loading order is now following:

jquery
booklet
app.js (bundled file with webpack, including jquery)', 'images/image1.png');
INSERT INTO question (uuid, user_id, submission_time, view_number, vote_number, title, message, image)
    VALUES ('bgfbgfcvcx', 1, '2017-05-01 10:41:00', 1364, 57, 'Drawing canvas with an image picked with Cordova Camera Plugin', 'I''m getting an image from device and drawing a canvas with filters using Pixi JS. It works all well using computer to get an image. But when I''m on IOS, it throws errors such as cross origin issue, or that I''m trying to use an unknown format.
', NULL);


INSERT INTO answer (uuid, user_id, submission_time, vote_number, question_id, message, image)
                VALUES ('kjmkjmkjkj' , 1, '2017-04-28 16:49:00', 4, 1, 'You need to use brackets: my_list = []', NULL);
INSERT INTO answer (uuid, user_id, submission_time, vote_number, question_id, message, image)
                VALUES ('dsdsbfsghsrhtfs', 1, '2017-04-25 14:42:00', 35, 1, 'Look it up in the Python docs', 'images/image2.jpg');


INSERT INTO comment (uuid, user_id, question_id, answer_id, message, submission_time)
                VALUES ('gd0gjr9rejoifd', 1, 1, NULL, 'Please clarify the question as it is too vague!', '2017-05-01 05:49:00');
INSERT INTO comment (uuid, user_id, question_id, answer_id, message, submission_time)
                VALUES ('xiuhvxiug489845ur', 1, NULL, 1, 'I think you could use my_list = list() as well.', '2017-05-02 16:55:00');

INSERT INTO tag (name) VALUES ('python');
INSERT INTO tag (name) VALUES ('sql');
INSERT INTO tag (name) VALUES ('css');

INSERT INTO question_tag VALUES (1, 1);
INSERT INTO question_tag VALUES (2, 3);
INSERT INTO question_tag VALUES (3, 3);
