FROM python:3
WORKDIR /usr/src/app
COPY ./docker-build/release/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./restServer/ ./

EXPOSE 8000
CMD [ "./run_release.sh" ]
