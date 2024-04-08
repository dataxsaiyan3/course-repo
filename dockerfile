FROM python:3.10-slim

COPY requirements.txt opt/
RUN pip3 install -r opt/requirements.txt

# copy code
COPY ./src/ /app/src/


#Changing user to keep container secure
RUN groupadd -g 999 username && \
    useradd -r -u 999 -g username username && \
    chown -R username /app

USER username

# set workdir and execute task
WORKDIR /app/src

CMD ["python3", "main.py"]
