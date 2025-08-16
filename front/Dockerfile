FROM node:20

COPY ./app /app
WORKDIR /app

RUN yarn

CMD [ "yarn", "serve", "--", "--port", "8000"]
