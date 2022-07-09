FROM python:latest

RUN pip install numpy

CMD ["python", "thermal-storage/src/main.py"]