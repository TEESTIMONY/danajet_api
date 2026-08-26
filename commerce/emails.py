import logging
from html import escape
from threading import Thread

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from contacts.emails import _send_with_resend_api, admin_notification_html, send_admin_notification
from sitecontent.serializers import media_public_url

from .models import Order


logger = logging.getLogger(__name__)


def _order_summary(order):
    items = "\n".join(
        f"- {item.quantity}x {item.title}: {order.currency} {item.line_total}"
        for item in order.items.all()
    )
    address = order.shipping_address or {}
    address_text = ", ".join(str(value) for value in address.values() if value)
    payment_label = order.get_payment_method_display()
    return (
        f"Order number: {order.order_number}\n"
        f"Customer: {order.first_name} {order.last_name}\n"
        f"Email: {order.email}\n"
        f"Phone: {order.phone or 'Not provided'}\n"
        f"Address: {address_text or 'Not provided'}\n"
        f"Payment method: {payment_label}\n\n"
        f"Items:\n{items}\n\n"
        f"Subtotal: {order.currency} {order.subtotal}\n"
        f"Shipping: {order.currency} {order.shipping_total}\n"
        f"Total: {order.currency} {order.total}\n"
        f"Customer display total: {order.display_currency} {order.display_total}\n"
        f"Order notes: {order.notes or 'None'}"
    )


def send_order_emails(order_id):
    try:
        order = Order.objects.prefetch_related("items").get(pk=order_id)
        summary = _order_summary(order)
        customer_subject = f"Order Received - {order.order_number}"
        admin_subject = f"New Order - {order.order_number}"
        customer_body = (
            "Thank you :)\n\n"
            "We’ve received your payment notification. Orders are verified manually, usually within 24 hours. "
            "Once your payment is confirmed, you’ll receive an email with your download or the next steps for your order ✅\n\n"
            f"{summary}\n\nThe Danajet Team"
        )
        admin_body = f"A new Danajet order has been placed.\n\n{summary}"
        customer_html = (
            "<div style=\"margin:0;background:#f6f1e9;padding:28px 0;font-family:Arial,Helvetica,sans-serif;color:#171717;\">"
            "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:collapse;\">"
            "<tr><td align=\"center\" style=\"padding:0 18px;\">"
            "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:620px;border-collapse:collapse;background:#11100e;color:#fff;\">"
            "<tr><td style=\"padding:34px 34px 26px;border-bottom:1px solid #2e2a25;\">"
            "<p style=\"margin:0 0 18px;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#ef450b;\">Order Received</p>"
            "<h1 style=\"margin:0;font-size:34px;line-height:.98;text-transform:uppercase;\">Thank you :)</h1>"
            "</td></tr>"
            "<tr><td style=\"padding:28px 34px 34px;\">"
            "<p style=\"margin:0 0 18px;font-size:16px;line-height:1.65;color:#e8e1d7;\">We’ve received your payment notification. Orders are verified manually, usually within 24 hours. Once your payment is confirmed, you’ll receive an email with your download or the next steps for your order ✅</p>"
            f"<pre style=\"margin:0;font-size:14px;line-height:1.6;white-space:pre-wrap;color:#e8e1d7;\">{escape(summary)}</pre>"
            "</td></tr></table></td></tr></table></div>"
        )
        admin_html = (
            "<div style=\"margin:0;background:#f6f1e9;padding:28px 0;font-family:Arial,Helvetica,sans-serif;color:#171717;\">"
            "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"border-collapse:collapse;\">"
            "<tr><td align=\"center\" style=\"padding:0 18px;\">"
            "<table role=\"presentation\" width=\"100%\" cellspacing=\"0\" cellpadding=\"0\" style=\"max-width:620px;border-collapse:collapse;background:#11100e;color:#fff;\">"
            "<tr><td style=\"padding:34px 34px 26px;border-bottom:1px solid #2e2a25;\">"
            "<p style=\"margin:0 0 18px;font-size:12px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:#ef450b;\">New Order</p>"
            f"<h1 style=\"margin:0;font-size:34px;line-height:.98;text-transform:uppercase;\">{escape(order.order_number)}</h1>"
            "</td></tr>"
            "<tr><td style=\"padding:28px 34px 34px;\">"
            f"<pre style=\"margin:0;font-size:14px;line-height:1.6;white-space:pre-wrap;color:#e8e1d7;\">{escape(summary)}</pre>"
            "</td></tr></table></td></tr></table></div>"
        )

        if settings.RESEND_API_KEY:
            _send_with_resend_api(customer_subject, customer_body, customer_html, order.email)
        else:
            customer_message = EmailMultiAlternatives(
                customer_subject,
                customer_body,
                settings.DEFAULT_FROM_EMAIL,
                [order.email],
            )
            customer_message.attach_alternative(customer_html, "text/html")
            customer_message.send(fail_silently=False)

        # Bcc's the admin recipients so they don't see each other's addresses.
        send_admin_notification(admin_subject, admin_body, admin_html)
    except Exception:
        logger.exception("Order emails could not be sent for order %s", order_id)


def queue_order_emails(order_id):
    if not getattr(settings, "ORDER_EMAIL_ASYNC", True):
        send_order_emails(order_id)
        return

    Thread(target=send_order_emails, args=(order_id,), daemon=True).start()


def send_receipt_uploaded_email(order_id):
    try:
        order = Order.objects.get(pk=order_id)
        receipt_link = media_public_url(order.receipt.name) if order.receipt else ""
        summary = (
            f"Order number: {order.order_number}\n"
            f"Customer: {order.first_name} {order.last_name}\n"
            f"Email: {order.email}\n"
            f"Payment method: {order.get_payment_method_display()}\n"
            f"Total: {order.display_currency} {order.display_total}\n"
            f"Receipt: {receipt_link or 'Uploaded, view in the Danajet admin dashboard.'}"
        )
        subject = f"Receipt Uploaded - {order.order_number}"
        text_body = f"A payment receipt was uploaded for an order awaiting confirmation.\n\n{summary}"
        html_body = admin_notification_html("Receipt Uploaded", order.order_number, summary)
        send_admin_notification(subject, text_body, html_body)
    except Exception:
        logger.exception("Receipt uploaded email could not be sent for order %s", order_id)


def queue_receipt_uploaded_email(order_id):
    if not getattr(settings, "ORDER_EMAIL_ASYNC", True):
        send_receipt_uploaded_email(order_id)
        return

    Thread(target=send_receipt_uploaded_email, args=(order_id,), daemon=True).start()
