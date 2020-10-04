FROM dpage/pgadmin4:latest

ARG CACHEBUST=1

COPY pgadmin_servers.json /pgadmin4/pgadmin_servers.json
COPY password.file /pgadmin4/password.file

ENTRYPOINT ["/entrypoint.sh"]