# Backend For Loan Simulation

<center>

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=rcleydsonr-sonar_lending-backend&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=rcleydsonr-sonar_lending-backend)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=rcleydsonr-sonar_lending-backend&metric=coverage)](https://sonarcloud.io/summary/new_code?id=rcleydsonr-sonar_lending-backend)

</center>

## Environment setup
For this project you just need to have installed docker and docker-compose apps.
When installed you can clone this repository and follow above steps.

```bash
# clone this repository
$ git clone https://github.com/RcleydsonR/loan_backend.git

# change to cloned repository directory
$ cd loan_backend

# Use docker-compose to start application container
$ docker-compose up --build

# migrate django models
$ make migrate

# You will need to enter container that is running django application and create django super user
$ make bash
$ python manage.py createsuperuser --email admin@example.com --username admin
```

## Test setup
This application is using pytest to execute test suite, and the command is available in Makefile with default flag -s that capture breakpoints for debugging.

```bash
# Executing all application tests
$ make test

# Select file test to be run
$ make test FILE=your/file/test.py

# Select a unique test case
$ make test TEST=testOrClassName
```