import smtplib
import email
import sys

def send_gmail(acct, pw, to, subject, message):
    tos = ""
    if type(to) is list:
        tos = ', '.join([x.rstrip() for x in to])
    else:
        tos = to

    addr = "%s@gmail.com" % (acct,)

    msg = email.MIMEText.MIMEText(message, "plain")
    msg['From'] = addr
    msg['To'] = tos
    msg['Subject'] = subject

    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    #mailServer.set_debuglevel(1)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(addr, pw)
    mailServer.sendmail(addr, to, msg.as_string())
    mailServer.close()

if __name__ == "__main__":
    send_gmail(*sys.argv)

