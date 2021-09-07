FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install Cython
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scikit-learn

COPY model.pkl ProcessData.py server.py wsgi.py ./

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
