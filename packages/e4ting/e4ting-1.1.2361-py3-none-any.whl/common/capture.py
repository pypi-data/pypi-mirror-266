#  -*-  coding=utf8  -*-

import cv2
from time import sleep
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import smtplib
import datetime

def add_image(file):
    fp = open(file, "rb")
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msgImage.add_header('Content-Disposition', 'attachment', filename = file)
    return msgImage


def send_email(to_address, subject, content, plugin=None, from_address='e4ting@qq.com'):

    for i in range(10):
        try:
            msg = MIMEMultipart('related')

            msg["Subject"] = subject + ' ' + datetime.datetime.now().strftime("%m-%d %H:%M:%S")
            msg["From"] = from_address
            msg["To"] = to_address

            msg_text = MIMEText(datetime.datetime.now().strftime("%m-%d %H:%M:%S") + ' ' + content, 'plain', 'utf-8')
            msg_image = add_image(file)

            msg.attach(msg_text)
            msg.attach(msg_image)

            username = from_address
            password = 'admin123'

            server = smtplib.SMTP_SSL('smtp.qq.com', 465)
            # server.starttls()
            server.login(username, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            # print ("mail send success")
            break
        except Exception as e:
            print(e)
            # print ('邮件发送失败')
            # try_num += 1
            # if try_num > max_try_num:
            # break
            sleep(5)


def capture(file):

    cap = cv2.VideoCapture(0)
    # while True:

    # 这里不sleep一下拍到相片就是黑的
    sleep(1)
    # get a frame
    ret, frame = cap.read()
    # show a frame
    # cv2.imshow("capture", frame)
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    cv2.imwrite(file, frame)
    # break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # con = u"邮件发送成功"
    # import pdb; pdb.set_trace()
    # print (con)
    # sleep(5)
    file = "./test.jpeg"
    capture(file)
    send_email("e4ting@qq.com", "mac开机提醒", "这是打开你MAC的人 ： ", plugin=file)

