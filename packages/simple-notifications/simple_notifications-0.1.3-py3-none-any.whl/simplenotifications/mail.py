#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Email sending
"""

import os
import smtplib
import mimetypes
from string import Template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

# --- Simple Email sender ----


class mail_error(Exception):
    """
    Mail error exception, raised by the ```mail``` class in case of errors.

    """
    pass

class mail:
    """
    Class for sending emails with minimal effort. Supports simple file attachments and html formatted mails.

    """
    def __init__(self,
                 a_sServer,
                 a_sUser,
                 a_sPassword,
                 a_nPort,
                 a_bStarttls = False,
                 a_sMailAddrFrom = "noreply@example.com"):
        """
        Constructor.

        Args:
            a_sServer: Mail server to connect to (str)
            a_sUser: Mail server username (str)
            a_sPassword: Mail server password (str)
            a_nPort: TCP port for mail server connection (int)
            a_bStarttls: Use StartTLS (bool)
            a_sMailAddrFrom: "From" email address (str)

        """
        self._sServer = a_sServer
        self._sUser = a_sUser
        self._sPassword = a_sPassword
        self._nPort = a_nPort
        self._bStarttls = a_bStarttls
        self._sMailAddrFrom = a_sMailAddrFrom
        self.SetHtmlBodyFormat()

    def SetHtmlBodyFormatToPreFormattedText(self):
        """
        Set the HTML body start/end tags so that the whole email message will by enclosed by HTML ```<pre>``` tags. This is just a convenience function which calls *SetHtmlBodyFormat* with certain 'preset' values.

        """
        self.SetHtmlBodyFormat('<html><body><pre>',
                               '</pre></body></html>')

    def SetHtmlBodyFormat(self,
                          a_sHtmlBodyStart = '<html><body>',
                          a_sHtmlBodyEnd   = '</body></html>'):
        """
        Set the HTML body start/end tags for the mail body.

        Args:
            a_sHtmlBodyStart: Start tags for mail body (str)
            a_sHtmlBodyEnd: End tags for mail body (str)

        """
        self.sHtmlBodyStart = a_sHtmlBodyStart
        self.sHtmlBodyEnd = a_sHtmlBodyEnd

    def _prepare_message(self,
                      a_sMailAddrTo,
                      a_sMsg,
                      a_sSubject,
                      a_tFileAttachments,
                      a_bEmbedImages = False):
        """
        Prepare the mail. Uses the HTML start/end tags defined from e.g. *SetHtmlBodyFormat*

        Args:
            a_sMailAddrTo: Mail recipient (str)
            a_sMsg: Mail body/message (str)
            a_sSubject: Mail subject (str)
            a_tFileAttachments: List of file paths to attach (list of str)
            a_bEmbedImages: Embed image attachments in mail body (bool)

        Returns:
            mail message object (email.mime.multipart.MIMEMultipart)

        Raises:
            mail_error on any error.
        """
        # Main message
        message = MIMEMultipart("mixed")
        message["Subject"] = a_sSubject
        message["From"] = self._sMailAddrFrom
        message["To"] = a_sMailAddrTo

        # Message body
        message_body = MIMEMultipart("alternative")
        message_body.attach(MIMEText(a_sMsg, "plain"))
        message_body.attach(MIMEText(f'{self.sHtmlBodyStart}{a_sMsg}{self.sHtmlBodyEnd}', "html"))
        message.attach(message_body)

        # File attachments
        for f in a_tFileAttachments:
            #file_path = os.path.join(dir_path, f)
            try:
                type, enc = mimetypes.guess_type(f)
                if a_bEmbedImages and "image/" in type:
                    attachment = MIMEImage(open(f, "rb").read())
                    attachment.add_header('Content-ID',f'<{os.path.basename(f)}>') ## shorten filename, do not use full path
                    attachment.add_header('Content-Disposition','attachment', filename=os.path.basename(f)) ## shorten filename, do not use full path
                else:
                    attachment = MIMEApplication(open(f, "rb").read(), _subtype = 'octet-stream')
                    attachment.add_header('Content-Disposition','attachment', filename=os.path.basename(f)) ## shorten filename, do not use full path
                # Attach to main message
                message.attach(attachment)
            except OSError as e:
                raise mail_error(f'Could not attach file {f}: {str(e)}')

        #return message.as_string()
        return message

    def send_template(self,
                      a_sMailAddrTo,
                      a_sMsgTemplateFile,
                      a_tMsgTemplateDict,
                      a_sSubject,
                      a_tFileAttachments = list(),
                      a_bEmbedImages = False):
        """
        Send mail. Instead of expecting the message as a complete text, this function allows to supply a dictionary and a template file.

        Args:
            a_sMailAddrTo: Mail recipient (str)
            a_sMsgTemplateFile: Path of a template file (str)
            a_tMsgTemplateDict: Dictionary holding the keys/values for the template. All occurences of every ```$<key>``` in the template file will be replaced with the respective value from the dict. (dict)
            a_sSubject: Mail subject (str)
            a_tFileAttachments: List of file paths to attach (list of str)
            a_bEmbedImages: Embed image attachments in mail body (bool)

        Raises:
            mail_error on any internal simple-notifications error.
            any smtplib exception
        """
        try:
            with open(a_sMsgTemplateFile, 'r') as f:
                tpl = Template(f.read())
                msg = tpl.safe_substitute(a_tMsgTemplateDict)
                self.send(a_sMailAddrTo, msg, a_sSubject, a_tFileAttachments, a_bEmbedImages)
        except OSError as e:
               raise mail_error(f'Could not read template file {a_sMsgTemplateFile}: {str(e)}')

    def send(self,
             a_sMailAddrTo,
             a_sMsg,
             a_sSubject,
             a_tFileAttachments = list(),
             a_bEmbedImages = False):
        """
        Send mail with optional file attachments. This is the basic mail function.

        Args:
            a_sMailAddrTo: Mail recipient (str)
            a_sMsg: Mail body/message (str)
            a_sSubject: Mail subject (str)
            a_tFileAttachments: List of file paths to attach (list of str)
            a_bEmbedImages: Embed image attachments in mail body (bool)

        Raises:
            mail_error on any internal simple-notifications error.
            any smtplib exception
        """
        try:
            if self._bStarttls:
                with smtplib.SMTP(host = self._sServer, port = self._nPort) as mailer:
                    mailer.starttls()
                    mailer.login(user = self._sUser, password = self._sPassword)
                    mailer.send_message(from_addr = self._sMailAddrFrom,
                                        to_addrs = a_sMailAddrTo,
                                        msg = self._prepare_message(a_sMailAddrTo,
                                                                    a_sMsg,
                                                                    a_sSubject,
                                                                    a_tFileAttachments,
                                                                    a_bEmbedImages))
            else:
                with smtplib.SMTP_SSL(host = self._sServer, port = self._nPort) as mailer:
                    mailer.login(user = self._sUser, password = self._sPassword)
                    mailer.send_message(from_addr = self._sMailAddrFrom,
                                        to_addrs = a_sMailAddrTo,
                                        msg = self._prepare_message(a_sMailAddrTo,
                                                                    a_sMsg,
                                                                    a_sSubject,
                                                                    a_tFileAttachments,
                                                                    a_bEmbedImages))
        except Exception as e:
            raise
