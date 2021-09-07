FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install Cython
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scikit-learn

COPY 00_model/model.pkl 01_server/ProcessData.py 01_server/server.py 01_server/wsgi.py ./

CMD [ "gunicorn", "--bind", "0.0.0.0:5001", "wsgi:app"]
