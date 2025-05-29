FROM python:3.12.3

WORKDIR /myBot

COPY bot.py .

RUN pip install --no-cache-dir requests pyTelegramBotAPI

CMD ["python", "bot.py"]
