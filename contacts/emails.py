import logging
import json
from threading import Thread
from urllib import error as urlerror
from urllib import request as urlrequest

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger(__name__)


def queue_newsletter_welcome_email(subscription):
    if not getattr(settings, "NEWSLETTER_EMAIL_ASYNC", True):
        send_newsletter_welcome_email(subscription)
        return

    Thread(target=send_newsletter_welcome_email, args=(subscription,), daemon=True).start()


def _send_with_resend_api(subject, text_body, html_body, to_email):
    payload = json.dumps(
        {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
            "text": text_body,
        }
    ).encode("utf-8")
    request = urlrequest.Request(
        settings.RESEND_API_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urlrequest.urlopen(request, timeout=settings.EMAIL_TIMEOUT) as response:
            response.read()
    except urlerror.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend API returned {error.code}: {body}") from error


def _send_with_django_email(subject, text_body, html_body, to_email):
    message = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, [to_email])
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


def send_newsletter_welcome_email(subscription):
    if not subscription.email:
        return

    subject = "Welcome to the Danajet Network"
    to_email = subscription.email
    text_body = (
        "Welcome to the Danajet Network.\n\n"
        "Thank you for joining us. You are now on the list for thoughtful updates from Danajet, including book resources, learning notes, creative news, and selected offers.\n\n"
        "Danajet exists to help authors, learners, and creative brands turn ideas into polished work. We will keep our emails useful, clear, and worth your time.\n\n"
        "Warm regards,\n"
        "The Danajet Team"
    )
    html_body = """
    <div style="margin:0;background:#f6f1e9;padding:28px 0;font-family:Arial,Helvetica,sans-serif;color:#171717;">
      <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">
        <tr>
          <td align="center" style="padding:0 18px;">
            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;border-collapse:collapse;background:#11100e;color:#fff;">
              <tr>
                <td style="padding:34px 34px 26px;border-bottom:1px solid #2e2a25;">
                  <p style="margin:0 0 18px;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#ef450b;">Danajet Network</p>
                  <h1 style="margin:0;font-size:34px;line-height:.98;text-transform:uppercase;">Welcome to the Danajet Network.</h1>
                </td>
              </tr>
              <tr>
                <td style="padding:28px 34px 34px;">
                  <p style="margin:0 0 18px;font-size:16px;line-height:1.65;color:#e8e1d7;">Thank you for joining us. You are now on the list for thoughtful updates from Danajet, including book resources, learning notes, creative news, and selected offers.</p>
                  <p style="margin:0 0 24px;font-size:16px;line-height:1.65;color:#e8e1d7;">Danajet exists to help authors, learners, and creative brands turn ideas into polished work. We will keep our emails useful, clear, and worth your time.</p>
                  <p style="margin:0;font-size:15px;line-height:1.6;color:#fff;"><strong>Warm regards,</strong><br>The Danajet Team</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </div>
    """

    try:
        if settings.RESEND_API_KEY:
            _send_with_resend_api(subject, text_body, html_body, to_email)
        else:
            _send_with_django_email(subject, text_body, html_body, to_email)
    except Exception:
        logger.exception("Newsletter welcome email could not be sent to %s", subscription.email)
