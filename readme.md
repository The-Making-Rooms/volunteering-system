# Volunteering System


This system was created to allow organisations to manage opportunities and volunteer sign ups through an easy to use platform. It is the culmination of many months of user research and has been initially launched with the Chip In project.

Chip In is a place-based volunteering project for young people from the borough of Blackburn with Darwen, with mentoring at the heart. [See the platform in action](https://chipinbwd.co.uk/) or learn more [here](https://www.communitycvs.org.uk/volunteer/chip-in/)

This project is distributed under the [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/) license. Please see below and the attached LICENSE file for more details.


## 🌠 Getting started with development

### Install Dependancies:
- Start by clong this repo
- Create a virtual environment:
	`python -m venv venv`
- Activate the virtual environment:
	`source venv/bin/activate`
- Install pyhton dependancies:
	`pip install -r requirements.txt`
- Install npm dependancies:
	`npm install` 

### Setup Django:
```
cd src
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### Run the project:
Open 2 terminals:

**In terminal 1:**
```
cd src
npx tailwindcss -i ./static/src/input.css -o ./static/src/output.css --watch
```
**In terminal 2:**
```
cd src
python manage.py runserver
```

### Sign in:
goto the /org_admin route and sign in as the super user


And you should be good to go!


## 📚 System Architecture:
The system is written in Django, htmx and tailwindCSS+DaisyUI. htmx is used for interactivity, and most routes have a check to see if the request has a htmx header. If it does, only a partial will be sent. DaisyUI components are used throughout using tailwind utility classes.

### User Roles:
**superuser**: Can see and manage everything
**staff**: Can manage a single organisation, all of it's opportunities and volunteers
**volunteer**: Can sign up for opportuinities and browse the platform

### Main apps:
| App name |Function  |
|--|--|
| commonui |Contains the Sign in, Sign up and password reset pages as well as navigation components.   |
| communications |Messaging system for volunteers to send enquiries|
|forms  |Handles rendering forms|
|explore  |Allows looking at all of the opportunities and organisations in the system|
|organisations|Contains the models for organisations, and rendering the organisation pages|
|opportunities|Contains the models for opportunities, and rendering the opportunity pages |
|org_admin|Administration interface to manage everything |
|volunteer| Allows users to see thier profile and keep information up to date |


## License

### You are free to:

1.  **Share** — copy and redistribute the material in any medium or format
2.  **Adapt** — remix, transform, and build upon the material
3.  The licensor cannot revoke these freedoms as long as you follow the license terms.

### Under the following terms:

1.  **Attribution** — You must give [appropriate credit](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-appropriate-credit) , provide a link to the license, and [indicate if changes were made](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-indicate-changes) . You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
2.  **NonCommercial** — You may not use the material for [commercial purposes](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-commercial-purposes) .
3.  **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the [same license](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-same-license) as the original.
4.  **No additional restrictions** — You may not apply legal terms or [technological measures](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-technological-measures) that legally restrict others from doing anything the license permits.

### Notices:

You do not have to comply with the license for elements of the material in the public domain or where your use is permitted by an applicable [exception or limitation](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-exception-or-limitation) .

No warranties are given. The license may not give you all of the permissions necessary for your intended use. For example, other rights such as [publicity, privacy, or moral rights](https://creativecommons.org/licenses/by-nc-sa/4.0/#ref-publicity-privacy-or-moral-rights) may limit how you use the material.
