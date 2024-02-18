FROM rasa/rasa:3.6.5-full

WORKDIR /app

COPY . /app

USER root

COPY ./data /app/data
COPY ./models /app/models

VOLUME /app

VOLUME /app/data

VOLUME /app/models

CMD ["run","-m","/app/models","--enable-api","--cors","*","--debug" ,"--endpoints", "endpoints.yml", "--log-file", "out.log", "--debug"]
