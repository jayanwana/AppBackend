# Muve

Django Rest API for Muve Backend

### Prerequisites

1. A Terminal or a CMD
2. Python 3.7 or above installed.

### Installing

Open a Terminal or CMD, and clone the repository.
```
git clone https://github.com/jayanwana/AppBackend.git
```

Enter the root directory.
```
cd AppBackend
```

Install requirements (use pip3 if pip doesn't work)
```
pip install -r requirements.txt 
```

Run migrations to create Database and models<br/>
(Replace "python" with "py" or "python3" if an error occurs) 
```
python manage.py makemigrations
python manage.py migrate
```

Create a super user (User with all permissions)<br/>
(Replace "python" with "py" or "python3" if an error occurs) 
```
python manage.py createsuperuser
```
Enter the relevant information (email and password) when prompted

## Running the server

To run the server on localhost use the following command (Replace "python" with "py" or "python3" if an error occurs)
```
python manage.py runserver
```
### Using the API

After running the server, open the browser and go to
```
http://127.0.0.1:8000/
```
to view the Swagger UI and API endpoints. <br/>
Note: Only endpoints which don't require Authorization would be visible initially. 
Login with the details used to create the super user, to generate your authentication token. 
Add token to authorization header to view full list of API endpoints.

## Built With

* [Django](https://docs.djangoproject.com/en/3.0/) - The web framework used
* [Django-Rest-Framework](https://www.django-rest-framework.org/) - Rest API Framework
* [Django-Rest-Swagger](https://django-rest-swagger.readthedocs.io/en/latest/) - Used to generate swagger documentation
* [JWT Authentication](https://jpadilla.github.io/django-rest-framework-jwt/) - Authentication Token Generator

## Author

* **Anwana John** - [jayanwana](https://github.com/jayanwana)

See also the list of [contributors](https://github.com/MuveWallet/AppBackend/graphs/contributors) who participated in this project.



