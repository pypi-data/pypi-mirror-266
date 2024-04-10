import smtplib
from email.message import EmailMessage

from .config import EmailConfig


def seek_expert_reply(attachments: list[dict[str, str]] = [],
                      *,
                      config: EmailConfig):
    """Send an email to experts seeking expert feedback.

    Parameters
    ----------
    attachments: list[dict[str, str]]
        A list of attachments. Each is a dict with four keys: `data`,
        `maintype`, `subtype`, `filename`.

    Returns
    -------
    None

    """
    msg = EmailMessage()
    msg['From'] = config.email_from
    msg['To'] = config.email_to
    msg['Subject'] = config.subject
    message = config.email_body.strip()

    msg.set_content(message)

    # handle attachments
    for a in attachments:
        msg.add_attachment(
            a['data'],
            maintype=a['maintype'],
            subtype=a['subtype'],
            filename=a['filename'],
            cte='base64'
        )

    server = smtplib.SMTP(config.smtp_server, 587)
    server.starttls()
    # Login Credentials for sending the mail
    server.login(
       config.account,
       config.password
    )
    # send the message via the server.
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
