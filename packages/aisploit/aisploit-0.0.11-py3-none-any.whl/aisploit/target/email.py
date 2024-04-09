import time
import smtplib
import imaplib
import email
from email.mime.text import MIMEText

from ..core import BaseTarget, BasePromptValue
from ..utils import SMTPClient


class EmailTarget(BaseTarget):
    def __init__(
        self,
        *,
        smtp_host: str,
        imap_host: str,
        from_addr: str,
        to_addr: str,
    ) -> None:
        self._smtp_host = smtp_host
        self._imap_host = imap_host
        self._from_addr = from_addr
        self._to_addr = to_addr

    def send_prompt(self, prompt: BasePromptValue) -> str:
        # self._listen_for_emails(timeout=120)
        return self._send_email("Test", "TEST")

    def _send_email(self, subject: str, body: str):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = self._from_addr
        msg["To"] = self._to_addr

        with SMTPClient(self._smtp_host, 465) as client:
            client.login(self._from_addr, "PASSWORD")
            client.sendmail(self._from_addr, self._to_addr, msg.as_string())

    def _listen_for_emails(self, timeout=None):
        start_time = time.time()
        with imaplib.IMAP4_SSL(self._imap_host, 993) as server:
            server.login(self._from_addr, "PASSWORD")
            server.select("INBOX")
            server.send(b"IDLE\r\n")
            # server.idle()

            while True:
                elapsed_time = time.time() - start_time
                if timeout is not None and elapsed_time >= timeout:
                    break  # Exit the loop if the timeout has elapsed

                response = server.idle_check(
                    timeout=(
                        min(60, timeout - elapsed_time) if timeout is not None else None
                    )
                )
                if response:
                    try:
                        _, data = server.search(None, "UNSEEN")
                        email_ids = data[0].split()

                        for email_id in email_ids:
                            _, msg_data = server.fetch(email_id, "(RFC822)")
                            msg = email.message_from_bytes(msg_data[0][1])

                            sender = msg["From"]
                            subject = msg["Subject"]
                            body = None

                            if msg.is_multipart():
                                for part in msg.walk():
                                    content_type = part.get_content_type()
                                    if content_type == "text/plain":
                                        body = part.get_payload(decode=True).decode(
                                            "utf-8"
                                        )
                            else:
                                body = msg.get_payload(decode=True).decode("utf-8")

                            print(f"From: {sender}\nSubject: {subject}\nBody: {body}\n")
                    except Exception as e:
                        print(f"An error occurred while processing emails: {e}")

            # Stop IDLE mode
            server.idle_done()
