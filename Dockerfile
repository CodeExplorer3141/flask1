FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["python", "gongzhonghao.py"]
