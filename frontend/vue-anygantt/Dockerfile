# build stage
FROM node:lts-alpine as pmt-fe-build-stage
WORKDIR /any-gantt
COPY ./any-gantt/package*.json ./
RUN npm install
RUN npm install --save axios
RUN npm install --save moment
COPY ./any-gantt/. .
RUN npm run build

# production stage
FROM nginx:stable-alpine as production-stage
COPY --from=pmt-fe-build-stage /any-gantt/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]