import smtplib, ssl
from email.mime.text import MIMEText

class Search_Sender:
    
    
    def __init__(self, user, sender, pw):
        self._receiver = user
        self._sender = sender
        self._pw = pw
        self._port = 465
        self._smtp_server = "smtp.gmail.com"
        
   
        prefix = (self._receiver.split('@'))[0]
        to_send = prefix + '_property_lists.txt'
        with open(to_send, 'r') as fp:
            self._message= MIMEText(fp.read())
        self._message["Subject"] = "New Listings Meet Your Criteria"
        self._message["From"] = self._sender
        self._message["To"] = self._receiver
            
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self._smtp_server, self._port, context=context) as server:
            server.login(self._sender, self._pw)
            server.sendmail(self._sender, self._receiver, self._message.as_string())