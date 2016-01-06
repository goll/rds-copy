# RDS copy

## Overview
Copy RDS DB instance from one AWS account to another using boto3.

## Requirements (see requirements.txt)
* Python 3
* [Boto 3](https://github.com/boto/boto3)

## Installation
If you have `virtualenv` installed:

    $ git clone https://github.com/goll/rds-copy.git
    $ cd rds-copy/
    $ virtualenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

Without `virtualenv`:

    $ git clone https://github.com/goll/rds-copy.git
    $ cd rds-copy/
    $ pip install -r requirements.txt

## Usage
The script expects 3 arguments: source AWS account credentials, destination AWS account credentials, source DB instance name.

    $ ./rds-copy.py "<AWS_ACCESS_KEY_ID>:<AWS_SECRET_ACCESS_KEY>:<REGION_NAME>" "<AWS_ACCESS_KEY_ID>:<AWS_SECRET_ACCESS_KEY>:<REGION_NAME>" <DB_INSTANCE_NAME>
    $ ./rds-copy.py --help

