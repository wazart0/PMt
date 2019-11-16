FROM postgres:12

COPY postgresql12-develop.conf /etc/postgresql/postgresql.conf

# CMD [ "postgres" ]
CMD [ "postgres", "-c", "config_file=/etc/postgresql/postgresql.conf" ]
