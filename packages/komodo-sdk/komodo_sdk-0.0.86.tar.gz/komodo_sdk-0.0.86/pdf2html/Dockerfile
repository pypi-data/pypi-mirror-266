FROM pdf2htmlex/pdf2htmlex:0.18.8.rc2-master-20200820-alpine-3.12.0-x86_64

RUN apk add --update python3
RUN apk add py3-pip curl
RUN pip install --upgrade pip
RUN pip install fastapi uvicorn

WORKDIR /code
COPY pdf2html/server.py /code/server.py

# You must override the default entrypoint from base image to run the server
# You can do this in docker-compose.yml or in the command line
# You must also mount the volume to the container to access the files

# docker run -v $(pwd):/data/komodo -p 8050:8050 pdf2html --entrypoint "uvicorn server:app --host 127.0.0.1 --port 8050"
# ENTRYPOINT ["uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8050"]
