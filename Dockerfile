###########
# BUILDER #
###########

# pull official base image
FROM python:3.11-alpine as builder

# set work directory
WORKDIR /home/user/web

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update

# install psycopg2 dependencies
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN apk add python3-dev
RUN apk add --no-cache geos gdal

# lint
RUN pip install --upgrade pip

COPY . .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /home/user/web/wheels -r requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /home/user/web/wheels gunicorn
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /home/user/web/wheels psycopg2-binary


#########
# FINAL #
#########

# pull official base image
FROM python:3.11-alpine

# install the timezone data package
# RUN apk add tzdata

# Set the timezone
# ENV TZ=Asia/Tashkent
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S app && adduser -S app -G app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media
WORKDIR $APP_HOME

# install dependencies
RUN apk update && apk add libpq

RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install ruamel.yaml

RUN pip install --upgrade pip

COPY --from=builder /home/user/web/wheels /wheels
COPY --from=builder /home/user/web/requirements.txt .
RUN pip install --no-cache /wheels/*

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app:app $APP_HOME

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]