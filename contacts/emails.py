import logging
import json
from threading import Thread
from urllib import error as urlerror
from urllib import request as urlrequest

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .models import ContactMessage, ProjectRequest, TransportWaitlist


logger = logging.getLogger(__name__)


def queue_newsletter_welcome_email(subscription):
    if not getattr(settings, "NEWSLETTER_EMAIL_ASYNC", True):
        send_newsletter_welcome_email(subscription)
        return

    Thread(target=send_newsletter_welcome_email, args=(subscription,), daemon=True).start()


def queue_free_resource_email(subscription, course):
    Thread(target=send_free_resource_email, args=(subscription, course), daemon=True).start()


def _send_with_resend_api(subject, text_body, html_body, to_email):
    to_list = to_email if isinstance(to_email, (list, tuple)) else [to_email]
    payload = json.dumps(
        {
            "from": settings.RESEND_FROM_EMAIL,
            "to": to_list,
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
            "Accept": "application/json",
            "Authorization": f"Bearer {settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Danajet API/1.0 (https://danajet-api.onrender.com)",
        },
    )

    try:
        with urlrequest.urlopen(request, timeout=settings.EMAIL_TIMEOUT) as response:
            body = response.read().decode("utf-8", errors="replace")
            logger.info("Email sent to %s via Resend API: %s", to_list, body)
    except urlerror.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend API returned {error.code}: {body}") from error


def _send_with_django_email(subject, text_body, html_body, to_email):
    to_list = to_email if isinstance(to_email, (list, tuple)) else [to_email]
    message = EmailMultiAlternatives(subject, text_body, settings.DEFAULT_FROM_EMAIL, to_list)
    message.attach_alternative(html_body, "text/html")
    message.send(fail_silently=False)


def admin_notification_html(eyebrow, heading, body_text):
    from html import escape

    return (
        "<div style=\"margin:0;background:#f6f1e9;padding:28px 0;font-family:Arial,Helvetica,sans-serif;color:#171717;\">"
        "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:collapse;\">"
        "<tr><td align=\"center\" style=\"padding:0 18px;\">"
        "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:620px;border-collapse:collapse;background:#11100e;color:#fff;\">"
        "<tr><td style=\"padding:34px 34px 26px;border-bottom:1px solid #2e2a25;\">"
        f"<p style=\"margin:0 0 18px;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#ef450b;\">{escape(eyebrow)}</p>"
        f"<h1 style=\"margin:0;font-size:30px;line-height:1.05;text-transform:uppercase;\">{escape(heading)}</h1>"
        "</td></tr>"
        "<tr><td style=\"padding:28px 34px 34px;\">"
        f"<pre style=\"margin:0;font-size:14px;line-height:1.6;white-space:pre-wrap;color:#e8e1d7;\">{escape(body_text)}</pre>"
        "</td></tr></table></td></tr></table></div>"
    )


def send_admin_notification(subject, text_body, html_body):
    if settings.RESEND_API_KEY:
        _send_with_resend_api(subject, text_body, html_body, settings.ADMIN_NOTIFICATION_EMAILS)
    else:
        _send_with_django_email(subject, text_body, html_body, settings.ADMIN_NOTIFICATION_EMAILS)


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


def send_free_resource_email(subscription, course):
    if not subscription.email or not course.access_url:
        return

    subject = f"Your Danajet download: {course.title}"
    text_body = (
        f"Hello {subscription.name or 'there'},\n\n"
        f"Your free resource, {course.title}, is ready.\n\n"
        f"Download it here: {course.access_url}\n\n"
        "Thank you for downloading this free resource. We hope it helps you on your publishing journey.\n\n"
        "The Danajet Team"
    )
    html_body = f"""
    <div style="margin:0;background:#f6f1e9;padding:32px 18px;font-family:Arial,Helvetica,sans-serif;color:#171717;">
      <div style="max-width:620px;margin:0 auto;background:#fff;padding:36px;border-top:5px solid #ef450b;">
        <p style="margin:0 0 12px;color:#ef450b;font-size:12px;font-weight:800;text-transform:uppercase;">Danajet Free Resource</p>
        <h1 style="margin:0 0 18px;font-size:32px;line-height:1.05;">Your download is ready!</h1>
        <p style="font-size:16px;line-height:1.65;">Your copy of <strong>{course.title}</strong> is ready. Use the button below to download it now or return to it later.</p>
        <p style="margin:26px 0;"><a href="{course.access_url}" style="display:inline-block;padding:14px 20px;background:#ef450b;color:#fff;text-decoration:none;font-weight:800;">Download Resource</a></p>
        <p style="font-size:15px;line-height:1.65;color:#59534d;">Thank you for downloading this free resource. We hope it helps you on your publishing journey.</p>
      </div>
    </div>
    """
    try:
        if settings.RESEND_API_KEY:
            _send_with_resend_api(subject, text_body, html_body, subscription.email)
        else:
            _send_with_django_email(subject, text_body, html_body, subscription.email)
    except Exception:
        logger.exception("Free resource email could not be sent to %s", subscription.email)


def send_project_request_notification(request_id):
    try:
        entry = ProjectRequest.objects.get(pk=request_id)
        summary = (
            f"Name: {entry.name}\n"
            f"Email: {entry.email}\n"
            f"Phone: {entry.phone or 'Not provided'}\n"
            f"Service: {entry.service or 'Not specified'}\n"
            f"Budget: {entry.budget or 'Not specified'}\n"
            f"Stage: {entry.stage or 'Not specified'}\n"
            f"Timeline: {entry.timeline or 'Not specified'}\n"
            f"Preferred contact: {entry.get_preferred_contact_method_display()}\n\n"
            f"Message:\n{entry.message}"
        )
        subject = f"New Project Request - {entry.name}"
        text_body = f"A new project request was submitted on the Danajet website.\n\n{summary}"
        html_body = admin_notification_html("New Project Request", entry.name, summary)
        send_admin_notification(subject, text_body, html_body)
    except Exception:
        logger.exception("Project request notification could not be sent for id %s", request_id)


def queue_project_request_notification(request_id):
    Thread(target=send_project_request_notification, args=(request_id,), daemon=True).start()


def send_contact_message_notification(message_id):
    try:
        entry = ContactMessage.objects.get(pk=message_id)
        summary = (
            f"Name: {entry.name}\n"
            f"Email: {entry.email}\n"
            f"Phone: {entry.phone or 'Not provided'}\n"
            f"Reason: {entry.reason or 'Not specified'}\n\n"
            f"Message:\n{entry.message}"
        )
        subject = f"New Contact Message - {entry.name}"
        text_body = f"A new contact message was submitted on the Danajet website.\n\n{summary}"
        html_body = admin_notification_html("New Contact Message", entry.name, summary)
        send_admin_notification(subject, text_body, html_body)
    except Exception:
        logger.exception("Contact message notification could not be sent for id %s", message_id)


def queue_contact_message_notification(message_id):
    Thread(target=send_contact_message_notification, args=(message_id,), daemon=True).start()


def send_transport_waitlist_notification(entry_id):
    try:
        entry = TransportWaitlist.objects.get(pk=entry_id)
        summary = (
            f"Email: {entry.email}\n"
            f"Name: {entry.name or 'Not provided'}\n"
            f"Phone: {entry.phone or 'Not provided'}\n"
            f"City: {entry.city or 'Not provided'}\n"
            f"Notes: {entry.notes or 'None'}"
        )
        subject = f"New Transport Waitlist Signup - {entry.email}"
        text_body = f"A new Danajet Transport waitlist signup was submitted.\n\n{summary}"
        html_body = admin_notification_html("Transport Waitlist", entry.email, summary)
        send_admin_notification(subject, text_body, html_body)
    except Exception:
        logger.exception("Transport waitlist notification could not be sent for id %s", entry_id)


def queue_transport_waitlist_notification(entry_id):
    Thread(target=send_transport_waitlist_notification, args=(entry_id,), daemon=True).start()
