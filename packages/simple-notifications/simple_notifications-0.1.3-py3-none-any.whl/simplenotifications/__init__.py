"""
A small class library to send emails or webhook requests.

## Installation

  * Install from pypi: ```pip install simple-notifications```

## How to use

### Send email with file attachments

main.py
```
from simplenotifications import mail

if __name__ == '__main__':
    try:
        mailer = mail.mail("myserver", "myuser", "mypassword", 25, "sender@example.com")

        mailer.send('receiver@example.com',
                    'My message',
                    'My subject',
                    ['c:\\test.txt',
                     'c:\\test.png'])

    except mail.mail_error as e:
        print(e)
```

### Send email from template file

main.py
```
from simplenotifications import mail

if __name__ == '__main__':
    try:
        mailer = mail.mail("myserver", "myuser", "mypassword", 25, "sender@example.com")
        mailer.send_template("receiver@example.com",
                             "./template.txt'"
                             { "name": "John"},
                             'Testsubject')
    except mail.mail_error as e:
        print(e)
```

template.txt
```
Hello, $name!
```

### Send webhook message (http post request)

main.py
```
from simplenotifications import webhook

if __name__ == '__main__':
    hook = webhook.webhook_post("http://example.com/webhook")
    try:
        hook.post("Hello, world!")
    except webhook.webhook_error as e:
        print(e)
```

"""