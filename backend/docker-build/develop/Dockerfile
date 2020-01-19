FROM python:3
WORKDIR /usr/src/app

COPY ./backend/docker-build/baseRequirements.txt ./
RUN pip3 install --no-cache-dir -r baseRequirements.txt

COPY ./backend/docker-build/develop/requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD [ "./backend/app/run_develop.sh" ]
