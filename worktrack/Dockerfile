FROM python:3.9-slim

# set work directory
WORKDIR /app

RUN pip install --upgrade pip

ENV LIBRARY_PATH=/lib:/usr/lib

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# copy project
COPY . .

# install dependencies
RUN pip install -r requirements.txt

RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
