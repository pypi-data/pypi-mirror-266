# botwrap

Project Structure
botwrap/
│
├── openaiwrapper/       # Main package directory
│   ├── __init__.py      # Initializes the openaiwrapper package
│   ├── api_client.py    # Base module for API interactions
│   ├── assistants.py    # Assistants module
│   ├── threads.py       # Threads module
│   ├── messages.py      # Messages module
│   ├── runs.py          # Runs module
│   ├── tools.py         # Tools module
│   ├── files.py         # Files module
│   ├── utils.py         # Utility functions and helpers
│   └── config.py        # Configuration settings and constants
│
├── tests/               # Directory for test cases
│   ├── __init__.py      # Initializes the tests package
│   ├── test_api_client.py
│   ├── test_assistants.py
│   ├── test_threads.py
│   ├── test_messages.py
│   ├── test_runs.py
│   ├── test_tools.py
│   ├── test_files.py
│   └── test_utils.py
│
├── .gitignore           # Specifies intentionally untracked files to ignore
├── Procfile             # Specifies commands that are executed by the app on startup
├── requirements.txt     # The list of project dependencies
├── runtime.txt          # Specifies the Python version to use on Heroku
└── app.json             # (Optional) Used to define app setup for Heroku CI/CD and review apps
