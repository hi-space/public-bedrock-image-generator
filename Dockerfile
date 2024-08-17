FROM python:3.8

WORKDIR /app
COPY . .

RUN  pip3 install --upgrade pip && pip3 install -r requirements.txt

EXPOSE 8000
CMD ["streamlit", "run", "app.py", "--server.port", "8000", "--server.address", "0.0.0.0"]