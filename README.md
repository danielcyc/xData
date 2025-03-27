# xData

## Running Docker containers

- Ensure you are in the root directory
- run `docker-compose up --build`

## Running Backend Tests

- Ensure that you are in the `/backend` subfolder:
`pwd` ~/xData/backend
or else change your directory: `cd backend`
- run `poetry run pytest`

## Running Frontend Tests

- Ensure that you are in the `/frontend` subfolder:
`pwd` ~/xData/frontend
or else change your directory: `cd frontend`
- run `npm test`

### Running the Frontend

- Ensure that you are running on node v23.9.0 and npm 10.9.2
`node -v` v23.9.0
`npm -v` 10.9.2
or else use nvm to install it: `nvm install 23.9.0`
- Ensure that you are in the `/frontend` subfolder:
`pwd` ~/xData/frontend
or else change your directory: `cd frontend`
- Install dependencies `npm install`
- Run the app `npm run dev`

### Running the Backend

- Ensure that you have Python version 3.13.2
`python --version` Python 3.13.2
or else use pyenv to install it `pyenv install 3.13.2`
- Ensure that you have Poetry 2.1.1 installed
`poetry --version` Poetry (version 2.1.1)
- Ensure that you are in the `/backend` subfolder:
`pwd` ~/xData/backend
or else change your directory: `cd backend`
- Activate virtual envrionment `eval $(poetry env activate)`
- Install dependencies `poetry install`
- Run the app `poetry run uvicorn main:app --reload`
