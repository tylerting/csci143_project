# flask-on-docker

In this project, I created a web app that allows users to upload images from their computer and view them in the browser. This tutorial is drawn from https://testdriven.io/blog/dockerizing-flask-with-postgres-gunicorn-and-nginx/

To upload an image, navigate to the webpage http://localhost:55553/upload

To view an image, navigate to the webpage http://localhost:55553/media/IMAGE_FILE_NAME

Development

1. Rename .env.dev-sample to .env.dev

2. Update the environment variables in the docker-compose.yml and .env.dev files

3. Build the image and run the containers

Production

Uses gunicorn + nginx

1. Rename .env.prod-sample to .env.prod and .env.prod.db-sample to .env.prod.db. Update the environment variables

2. Build the images and run the containers


