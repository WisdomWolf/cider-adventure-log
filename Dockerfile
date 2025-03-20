FROM node:lts as build-stage
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install -g npm@11.2.0 && \
    npm install
COPY ./frontend .
RUN npm run build

FROM nginx as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist/ /app
COPY nginx.conf /etc/nginx/nginx.conf