# Assistive Chess Robot Server

This is the server for the assistive chess robot created by Team -i^2 for the System Design Project 2019 at the University of Edinburgh.

## Structure of repo

The repository is laid out in the following structure:

```
|
\ server - Contains all code for the flask app
| \
| | __init__.py - To make server into an importable module
| | server.py - Contains the entry point for the Flask app
| | ...
|
\ test - All tests
| \
| | __init__.py - Allows server module to be imported
| | test_main.py - A test file
| | ...
|
| .gitignore - Files that shouldn't be committed by Git
| .travis.yml - Configuration for the CI
| README.md - This readme file
```

## Gettting Started

### Pre-requisites

 - Heroku CLI
 - Python 3
 - virtualenv
 - pytest (optional for testing)

Run the following to set up a virtual environment. This will make sure that you are running the correct version of Python and that your libraries won't clash with versions if working on multiple Python projects.

```
$ cd negativei2-server
$ virtualenv --python=python3 venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
```

The tests are all found in `/tests` and can be run with `pytest`.

Run the following to start the application.

```
$ heroku local
3:59:29 PM web.1 |  [2019-02-12 15:59:29 +0000] [26045] [INFO] Starting gunicorn 19.9.0
3:59:29 PM web.1 |  [2019-02-12 15:59:29 +0000] [26045] [INFO] Listening at: http://0.0.0.0:5000 (26045)
3:59:29 PM web.1 |  [2019-02-12 15:59:29 +0000] [26045] [INFO] Using worker: sync
3:59:29 PM web.1 |  [2019-02-12 15:59:29 +0000] [26048] [INFO] Booting worker with pid: 26048
```

You can then visit the server by going to `http://localhost:5000` in your browser. Press `Ctrl+C` to stop the application.

## Contributing

No commits are allowed directly to master. All PRs to master need to pass status checks and be reviewed by at least one other contributor. Ideally, all pull requests should come with tests for the code within.

**Branch naming** - The convention `<username>/<descriptive word or phrase>` should be used.
