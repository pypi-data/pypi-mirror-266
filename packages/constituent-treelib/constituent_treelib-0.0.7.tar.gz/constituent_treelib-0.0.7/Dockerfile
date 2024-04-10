FROM python:3.9-slim

RUN apt-get update && apt-get install -y build-essential g++	
	
RUN pip install streamlit

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN apt-get install -y tk

EXPOSE 8501
CMD ["streamlit", "run", "ctl_app.py", "--server.port=8501", "--server.address=0.0.0.0"]