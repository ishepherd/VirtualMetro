# Virtual Metro

Online simulation of Melbourne Metro Trains (Public Transport Victoria) platform information display systems.

![Example image](https://yingtongli.me/blog/assets/posts/2018/Clayton-Flinders.png)

## Status

I (@ishepherd) forked it from this repo https://yingtongli.me/git/virtual-metro where its last commit is in 2019.
I'm told it may not work with current PTV APIs. I hope to fix that.

## Usage

Apply for a [PTV Timetable API](https://www.ptv.vic.gov.au/about-ptv/data-and-reports/datasets/ptv-timetable-api/) API key, and copy *virtual_metro/config.example.py* to *virtual_metro/config.py* and set `PTV_USER_ID` and `PTV_USER_ID` accordingly.

Create a Python virtual environment if necessary and install the required dependencies:

```bash
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt
```

Run the app as per the [Flask documentation](http://flask.pocoo.org/docs/1.0/quickstart/):

```bash
. venv/bin/activate
export FLASK_APP=virtual_metro
flask run
```

see [log-of-pain.md]
