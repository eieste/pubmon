FROM python:3.11


COPY . /app


RUN pip3 install /app


ENTRYPOINT ["publicmon"]
