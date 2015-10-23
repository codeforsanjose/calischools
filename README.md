# CaliSchools

This project was conceived as a way to circumvent the difficulties associated with obtaining batch data from the California Department of Education School Directory. We would love for this API platform to be widely adopted for use in apps and data analysis centered around Californian schools.


## Technology stack
* Django
* Django Rest Framework
* PostgresSQL
* Celery
* Redis


## Getting started

#### Setting up a virtual environment
We recommend using `virtualenv` to set up all the necessary dependencies. You may install it using `pip` as follows:
```
$ pip install virtualenv
```

Next, initiate a fresh virtual enviroment:
```
$ virtualenv env
```

#### Installing the dependencies
First, clone the project to a local folder of your choice and switch to it as your current working directory:
```
$ git clone https://github.com/codeforsanjose/calischools
$ cd calischools
```

Next, make sure that your existing or newly created `virtualenv` is active, and install the necessary dependencies using `pip`:
```
$ source ../env/bin/activate
(env)$ pip install -r requirements.txt
```

Redis is only being used as a broker for Celery, and as such, is not a critical requirement. However, it is required for setting up periodic database updates via Celery.

#### Setting up the database
We will be using the SQLite database backend for development purposes. Create a fresh database and set up the necessary tables as follows:
```
(env)$ ./manage.py migrate
```

Next, create an admin user account to gain access to Django's admin app:
```
(env)$ ./manage.py createsuperuser
```
Follow the prompts to complete user registration.

Once your blank database is set up, you may load the initial data dump (current as of **10/22/2015**):
```
(env)$ ./manage.py loaddata schools
```

#### Running the app
Run the tests, and fire up the Django development server as follows:
```
(env)$ py.test
(env)$ ./manage.py runserver
```

You should now be able to navigate to `http://localhost:8000/` on your favorite browser to access the API endpoints.

#### Updating the database
There are mainly two different ways to start database updates:
* Set up a periodic task for `data.update_db` on the Django admin panel.
* Manually from within the Django python interpreter: `from data.tasks import update_db; update_db();` 
