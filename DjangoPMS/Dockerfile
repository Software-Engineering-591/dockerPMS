FROM python:3.12-alpine

# Get GeoDjango dependencies
RUN apk add --no-cache geos gdal 

WORKDIR /usr/src/app
# prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# ensure Python output is sent directly to the terminal without buffering
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

COPY . /usr/src/app/

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
