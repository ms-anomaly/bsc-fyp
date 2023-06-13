FROM python:3.9

USER root

RUN pip install requests networkx matplotlib

RUN pip install numpy

RUN pip install torch

RUN pip install pandas

RUN pip install shap

EXPOSE 80

WORKDIR /app

COPY requirements.txt /app/
COPY web/index.html /app/
COPY scripts/init-script.sh /app/

RUN pip install -r requirements.txt

COPY *.py /app/

CMD ["/bin/sh", "init-script.sh"]
