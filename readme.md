# The Volunteer System



## Getting Started:

- Create a virtual environment


	    python -m venv venv


- Activate the virtual env

  

	- Windows:

  

	- Linux/mac:
		

		    source venv/bin/activate


  

- Install Dependancies

	     pip3 install django django-recurrence


  

- Change into src directory and run Development server


		cd src
        python manage.py makemigrations
        pyhton manage.py migrate


- Run these commands in 2 seperate terminals during development

		npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
		python manage.py runserver
		python manage.py runserver_plus --cert-file example.crt --key-file example.key 192.168.1.174:8001

