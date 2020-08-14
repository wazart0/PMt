# build stage
FROM node:lts-alpine as pmt-fe-build-stage
WORKDIR /app
COPY ./app/package*.json ./
RUN npm install
RUN npm install --save axios
RUN npm install --save moment
COPY ./app/. .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=pmt-fe-build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]