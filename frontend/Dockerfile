FROM python:3.9

USER root

RUN pip install requests networkx matplotlib

RUN pip install numpy

RUN pip install torch

# RUN pip install pandas

RUN pip install shap

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY *.py /app/

CMD ["python", "main.py"]
