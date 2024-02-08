import sendgrid
from django.conf import settings
from sendgrid.helpers.mail import Email, Content, Mail, To


def send_email(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.SENDGRID_FROM_EMAIL)
    to_email = To(to_email)
    content = Content("text/plain", content)
    mail = Mail(from_email, to_email, subject, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code, response.body, response.headers


if __name__ == "__main__":
    status_code, body, headers = send_email(
        "test@example.com",
        "Sending with SendGrid is Fun",
        "and easy to do anywhere, even with Python",
    )
    print(status_code)  # noqa: T201
    print(body)  # noqa: T201
    print(headers)  # noqa: T201
