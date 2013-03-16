import smtplib
import email
import sys

def send_gmail(acct, pw, to, subject, message):
    msg = email.MIMEText.MIMEText(message, "plain")
    msg['Subject'] = subject

    addr = "%s@gmail.com" % (acct,)
    mailServer = smtplib.SMTP("smtp.gmail.com", 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(addr, pw)
    mailServer.sendmail(
        addr,
        ','.join(to) if type(to) is list else to
        , msg.as_string())
    mailServer.close()

if __name__ == "__main__":
    send_gmail(*sys.argv)

