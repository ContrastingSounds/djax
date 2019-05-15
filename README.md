# djax

_WORK IN PROGRESS – Not yet a working example_

Bare bones Django implementation of a Looker Action Hub.

Includes example of converting Looker dashboard to a Google Slides presentation.

## Notes
- Slides example has only got as far as creating the slides & headers
– Have been able to generate and upload the images, but not yet add those images to a slide
- Trying the new @dataclass functionality, released as part of Python 3.7
  - To my mind, conceptually similar to using TypeScript to encourage stronger typing in JavaScript
- Requires Redis to be installed and running

## Most important files 
_(aside from having to learn a bit about the Django framework to understand the Action Hub web app)_

| File               | Description |
|--------------------|-------------|
| actions/actions.py | Defines the main data structures for an Action Hub. Includes the data for the actions endpoint used to register an Action Hub with a Looker instance |
| djax/utils.py      | get_client() used to call the Looker API using the Python SDK |
| dashboard_presentations/views.py | generate_dashboard_presentation() is the action endpoint |
| dashboard_presentations/tasks.py | Defines the data structures and code to generate the slidedeck. Separate to views.py as its important to run the generation process as a background task (using Celery) |

#### dashboard_presentations/tasks.py

| Function           | Description         |
|--------------------|---------------------|
| generate_presentation_from_dashboard() | The main task. Uses the Looker API to build an intermediary definition of the dashboard. At this stage, the definition is output agnositc. |
| generate_google_slides_presentation() | Take the intermediary definition, then use the Google Slides API to generate the slidedeck itself. |

Other functions are briefly commented in the code.


## Status and Support

This application is NOT supported or warranted by Looker in any way. Please do not contact Looker for support. Issues can be 
logged via https://github.com/ContrastingSounds/stub_hub/issues.

## Running locally

TODO: Document how to get the token.pickle file for OAuth authentication
TODO: Figure out how to use the new OAuth capability in Action Hub

1. Create a Python virtual environment eg for Conda users
- conda create -n djax python=3.7
- source activate djax
- pip install -r requirements.txt
2. Have credentials saved as a token.pickle file
- See https://developers.google.com/slides/quickstart/python
3. Check the .env environment file
4. ./run.sh

## Links to Google resources

###### GSuite APIs
https://blog.google/products/g-suite/slides-api/
http://developers.google.com/slides

###### GCP Client Authentication
https://developers.google.com/api-client-library/python/auth/web-app

###### GCP Console 
_(to enable the required APIs – be sure to be in the right GCP project)_
https://console.cloud.google.com/apis/api/drive.googleapis.com/overview
https://console.cloud.google.com/apis/api/slides.googleapis.com/overview
