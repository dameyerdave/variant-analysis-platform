#!/usr/bin/env bash

dcc exec api sh -c 'pip freeze > requirements.txt'
mv api/app/requirements.txt api/. 
cd api; pipenv run pip install -r requirements.txt