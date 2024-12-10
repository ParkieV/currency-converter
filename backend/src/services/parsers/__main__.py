import schedule
import time
import os


def run_container():
    os.system("docker run --rm my_container")


# Запланировать запуск в 20:00
schedule.every().day.at("20:00").do(run_container)

# Запуск бесконечного цикла
while True:
    schedule.run_pending()
    time.sleep(1)
