# Virtual Metro

Online simulation of Melbourne Metro Trains (Public Transport Victoria) platform information display systems.

![Example image](https://yingtongli.me/blog/assets/posts/2018/Clayton-Flinders.png)

## Status

I (@ishepherd) forked it from this repo https://yingtongli.me/git/virtual-metro where its last commit is in 2019.
I'm told it may not work with current PTV APIs. I hope to fix that.

## Usage

Apply for a [PTV Timetable API] API key, and copy *virtual_metro/config.example.py* to *virtual_metro/config.py* and set `PTV_USER_ID` and `PTV_USER_ID` accordingly. [Instructions for API keys and signatures]

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

see [log-of-pain.md](log-of-pain.md)


# API Resources

- [timetableapi.ptv.vic.gov.au v3 swagger]

Below are some helpful docs, in Wayback Machine. These were linked to from the swagger but those links are now dead (now just redirects to transport.vic.gov.au which seems not to have this content).

- [PTV Timetable API]
- [PTV Timetable API FAQ]
- [Instructions for API keys and signatures]


[PTV Timetable API]: https://web.archive.org/web/20250405065747/https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/
[PTV Timetable API FAQ]: https://web.archive.org/web/20250414195219/https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/ptv-timetable-api-faqs/
[Instructions for API keys and signatures]: https://web.archive.org/web/20250419170433/https://www.ptv.vic.gov.au/assets/default-site/footer/data-and-reporting/Datasets/PTV-Timetable-API/60096c0692/PTV-Timetable-API-key-and-signature-document.rtf
[timetableapi.ptv.vic.gov.au v3 swagger]: https://timetableapi.ptv.vic.gov.au/swagger/ui/index
