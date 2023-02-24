FROM mysql:8.0

COPY ./mysql/my.cnf /etc/my.cnf
RUN chown root:root /etc/my.cnf && chmod 644 /etc/my.cnf
