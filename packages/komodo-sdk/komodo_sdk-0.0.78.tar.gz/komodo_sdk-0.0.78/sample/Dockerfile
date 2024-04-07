FROM python:3.11

WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip3 install -r requirements.txt

RUN wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.4/wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN tar xvf wkhtmltox-0.12.4_linux-generic-amd64.tar.xz
RUN cp -a wkhtmltox/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
RUN cp -a wkhtmltox/bin/wkhtmltoimage /usr/local/bin/wkhtmltoimage

ENV NLTK_DATA /data/nltk_data
RUN python3 -m nltk.downloader punkt stopwords -d /data/nltk_data

COPY komodo /code/komodo/
COPY sample /code/sample/
