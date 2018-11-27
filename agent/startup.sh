#!/bin/bash

# add redis instruction hashes
python lua/redisLoadScript.py

# call tests to check they are added
python lua/scriptExecuterExample.py

# launch API
python app.py -p 5000
