# MHacks Backend And Frontend

## Installation

### New way
1. [Get Docker](https://docs.docker.com/engine/getstarted/step_one/#/step-1-get-docker)
2. [Get Docker Compose](https://docs.docker.com/compose/install/)
4. Clone this repo: `git clone https://github.com/MHacks-Website`
4. Change directory to the deploy directory: `cd deploy`
5. Start whatever environment you want
    - Development
        - `docker-compose -f development.yml up -d`
        - **NOTE: Your git repo will be linked to the development environment, so your local changes will be reflected with a container restart**
    - Production (You're gonna need some more env data)
        - `docker-compose -f production.yml up -d`
        - **NOTE: This takes care of setting up NGINX AND LetsEncrypt with the appropriate hosts (and autorenewal!).**
6. Access `http://localhost:8000` and start developing!

#### More docs regarding development will be added later

### Old way
Pre-installed packages:
- Python 2.7
- Git
- Postgre SQL (make sure its setup and running!)
    - For this make sure you have a database named mhacks and an empty user and password on localhost. If this is not the case update the development settings DATABASE settings to your own authentication details.

    



### Getting started:

```bash
    git clone <ssh or git link from repo>
    cd MHacks-Website
    # if <virtual environment preferred>
    virtualenv --distribute venv/
    source venv/bin/activate
    # endif
    pip install -r requirements.txt
    ./manage.py migrate
    ./manage.py runserver

```
##Installation Issues

### Ubuntu/Linux

If you're running on Ubuntu/Linux and you run into this output while doing `pip install -r requirements.txt`:
]

```
Complete output from command python setup.py egg_info:
    running egg_info
    creating pip-egg-info/psycopg2.egg-info
    writing pip-egg-info/psycopg2.egg-info/PKG-INFO
    writing top-level names to pip-egg-info/psycopg2.egg-info/top_level.t$
t
    writing dependency_links to pip-egg-info/psycopg2.egg-info/dependency$
links.txt
    writing manifest file 'pip-egg-info/psycopg2.egg-info/SOURCES.txt'
    warning: manifest_maker: standard file '-c' not found

    Error: pg_config executable not found.

    Please add the directory containing pg_config to the PATH
    or specify the full executable path with the option:

        python setup.py build_ext --pg-config /path/to/pg_config build ..$

    or with the pg_config option in 'setup.cfg'.

    ----------------------------------------
Command "python setup.py egg_info" failed with error code 1 in /tmp/pip-b$
ild-vqrPuW/psycopg2/
```
run `sudo apt-get install libpq-dev python-dev` to fix it and then run `pip install -r requirements.txt` to begin installation again.



### Mac OS

When installing through the ``requirements.txt``, you might encounter an issue where the installation breaks when installing M2Crypto. If you have brew installed, manually install the following dependencies. 

```
brew install openssl && brew install swig
brew --prefix openssl
$ /usr/local/opt/openssl
$ LDFLAGS="-L$(brew --prefix openssl)/lib"
CFLAGS="-I$(brew --prefix openssl)/include" \
SWIG_FEATURES="-I$(brew --prefix openssl)/include" \
pip install m2crypto
```

## URLs
    `/`                             => Homepage (can be index or blackout page)
    `/register`                     => Registration page (aka signup)
    `/validate/<uid>/<token>`       => Validate email page
    `/send_verify_email/<uid>`      => Send new verification email then redirects to login
    `/login`                        => Login page
    `/logout`                       => Logout then redirect to Homepage
    `/reset`                        => Request to reset password
    `/update_password/<uid>/<token>`=> Allows a reset of password from email link
    `/dashboard`                    => Dashboard with context based on user type
    `/live`                         => Live page with updates and stuff
    `/v1/docs`                      => API Documentation, also includes URLs to the rest of the API and methods

## Project Structure
 - Settings: `config/settings.py`: Has all the important configuration settings. `development_settings.py`: is used for local development, whereas `production_settings.py` should be created with the right settings and left on the production server.
 - URLs: `config/urls.py`: Has the high level URLs and includes URLs from different sources. `MHacks/frontend/urls.py`: Has the frontend URLs, `MHacks/v1/urls.py` has the backend endpoints.
 - Models: `MHacks/models.py` contains all the models that are in the database
 - Common code: `MHacks/` has common code like utils and forms and decorators shared between both the frontend and backend.
 - Managers:

## Important Things To Note:
(At some point this should be more fleshed out, better organized and moved to the wiki)
 - When creating forms for basically anything use Django forms and extend the generic form html file, allowing for maximum scalability and code reuse. See already implemented forms like login for how to do it correctly.
 - Always use form validators, don't do it yourself in the views. (See django docs for more)
 - Keep number of migrations as low as possible, i.e. by combining and pushing your (only one) migration only when you are certain that there will be no more changes to that part of the app. This is not necessary but is nice to keep the codebase clean and well maintained. Also once the migration is pushed don't go back and change as others may be depending on it.
 - When adding new models, remember to add it to the admin.py file so that it is exposed to the admin interface (if that behavior is wanted).
 - Keep view code small and minimal, implement maximum functionality in validators and model requirements.
 - Keep things as generic as possible thereby allowing maximum re-usability.
 - When adding API keys or anything protected, add a 'dummy' variable to development_settings.py and only then push, protected keys will be used on the backend. Never put any protected keys or anything protected in any other python file.
