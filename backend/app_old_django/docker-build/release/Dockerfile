FROM python:3
WORKDIR /usr/src/app

COPY ./docker-build/baseRequirements.txt ./
COPY ./docker-build/release/requirements.txt ./

RUN pip3 install --no-cache-dir -r baseRequirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

ARG CACHEBUST=1
COPY ./app/ ./

EXPOSE 8000
CMD [ "./run_release.sh" ]
# CMD [ "python3", "run_release.py" ]
