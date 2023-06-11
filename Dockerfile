FROM python:3.10

WORKDIR /app

COPY frontend/requirements.txt requirements.txt

RUN apt-get update && apt-get install -y libgl1-mesa-glx

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

COPY ./frontend .

CMD [ "python",  "app.py" ]