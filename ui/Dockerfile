# From node version 17 on it uses ssl v3 which is not supported
# in this application
FROM node:16.13-bullseye as build-stage

ARG GIT_VERSION
ARG GIT_BRANCH
ARG GIT_LASTCOMMITDATE
ENV VITE_APP_VERSION=${GIT_VERSION}
ENV VITE_APP_BRANCH=${GIT_BRANCH}
ENV VITE_APP_LASTCOMMITDATE=${GIT_LASTCOMMITDATE}

ENV PATH="$PATH:/app/node_modules/.bin"

COPY ./app /app
WORKDIR /app

RUN npm install -g npm@latest
RUN yarn global add vite
RUN yarn install
RUN npx browserslist@latest --update-db
RUN yarn build

FROM nginx:stable as production-stage
COPY --from=build-stage /app/dist /app

# Adjust values fom template using env vars
COPY nginx.conf /etc/nginx/nginx.conf
CMD /bin/bash -c "nginx -g 'daemon off;'"
