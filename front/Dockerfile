FROM node:20

RUN yarn

COPY ./app /app
WORKDIR /app

CMD [ "yarn", "serve", "--", "--port", "8000"]
