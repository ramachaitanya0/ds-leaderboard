FROM python:3.8
COPY . /DS-LEADERBOARD
WORKDIR /DS-LEADERBOARD
RUN pip install -r requiremnts.txt
# RUN pip install sharepy
EXPOSE 8501 
ENTRYPOINT ["streamlit","run"]
CMD ["app.py"]
