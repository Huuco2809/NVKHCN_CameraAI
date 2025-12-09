# Stage 0, "builder", based on Node.js, to build and compile the frontend
FROM node:lts-alpine as builder

# make the 'evn-project-fe' folder the current working directory
RUN mkdir -p /usr/src/evn-project-fe
WORKDIR /usr/src/evn-project-fe

# copy both 'package.json' and 'package-lock.json' (if available)
COPY package*.json ./

# install project dependencies
RUN npm install

# copy project files and folders to the current working directory (i.e. 'evn-project-fe' folder)
COPY . /usr/src/evn-project-fe

EXPOSE 4200

# build app for production with minification
CMD ["node_modules/.bin/ng", "serve", "-c", "production", "--host", "0.0.0.0"]