#QnA
Flask based web-application which could serve as a back-end for a multiple-choice-question game. The application, primarily, populates its data-store from sample data provided (data.csv). The application allows end-users to perform the following : fetching a question, fetching all questions, editing an existing question, fetching all the topics (for which the game has questions) and adding new questions. The application allows the end-users to further filter questions on the basis of 'topic' (from where the question is being derived from) and question creation-time.

##How to:

**To run app-server :** (by default, the server would run on port 5000 of **localhost**)
```sh
python app_server.py data.csv
```

a. To get a question:
  
  1. On the basis of **question_id** - 

  	```sh
	curl http://localhost:5000/get_question/<question_id>
	```
	A **question_id** would be a positive integral value >= 1.
  
  2. On the basis of a **topic** - 

	a. Fetches a question from topic named *topic_name*:

	```sh
  	curl http://localhost:5000/get_question/<topic_name>
	```

	b. Fetches most-recently added question from topic named *topic_name*

	```sh
	curl http://localhost:5000/get_question/<topic_name>?sort=y
	```

b. To get all questions:

  1. Without any filter

    ```sh
    curl http://localhost:5000/get_all_questions
    ```

  2. From topic named *topic_name*:

    ```sh
    curl http://localhost:5000/get_all_questions/<topic_name>
    ```

  3. Limiting the number of questions fetched

    ```sh
  	curl http://localhost:5000/get_all_questions?max_count=m
  	```
  	Where, **m** is a positive integral value.

  4. Filtering on the basis of question's creation time:

     ```sh
     curl http://localhost:5000/get_all_questions?sort=y
     ```

  Both **sort** and **max_count** can be simultaneously applied to queries as well. **e.g.**
  ```sh
  curl 'http://localhost:5000/get_all_questions/arithmetic?max_count=15&sort=y'
  ```

c. To get all topics:

```sh
curl http://localhost:5000/get_topics
```

d. To edit an existing question:
```sh
curl -H "Content-Type: application/json" -X POST -d '{"Question" : "Hello World?", "Distractors" : "me,me,me", "Answer" : "Nah..."}' http://localhost:5000/edit_question/qid
```
Where, **qid** is the *question_id* for the question that end-user is trying to change.

e. To create a new question:
```sh
curl -H "Content-Type: application/json" -X POST -d '{"Question" : "Hello World?", "Distractors" : "me,me,me", "Answer" : "Nah...", "Topic" : "philosophy"}' http://localhost:5000/create_question
```

##Requirements

. Flask 0.10

. Python 2.7



