# Reddit Image Scraper

A simple Reddit Image Scraper created with AsyncPraw, httpx and Pillow. The main focus of this application is asynchronous functionality. It can download reddit content parallelized.


## Getting Started with Reddit API
Login to Reddit and go to this page: https://www.reddit.com/prefs/apps/

At the bottom of the page, create a new app and follow the instructions. Save the client id and the client secret.

## Install

First step is to clone the repository. After you're done, you can use the handy make commands to use this app.

Note: go into devserver.sh and paste client id and client secret from Reddit API.

### On Linux/WSL:
* `make install` creates directories and renames devserver.example.sh to devserver.sh
* `make fmt` formats the project with black and isort
* `make lint` checks linting rules according to flake8, black and isort

### On Windows
Manually rename devserver.example.sh to devserver.sh.

After that you will have to run the commands one by one. Example: `flake8 .` in the project folder
