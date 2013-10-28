import uuid

from django.conf import settings
import google_measurement_protocol as ga

FINGERPRINT_PARTS = [
    'HTTP_ACCEPT',
    'HTTP_ACCEPT_ENCODING',
    'HTTP_ACCEPT_LANGUAGE',
    'HTTP_USER_AGENT',
    'HTTP_X_FORWARDED_FOR',
    'REMOTE_ADDR']

UUID_NAMESPACE = uuid.UUID('fb4abc05-e2fb-4e3e-8b78-28037ef7d07f')


def get_client_id(request):
    parts = [request.META.get(key, '') for key in FINGERPRINT_PARTS]
    return uuid.uuid5(UUID_NAMESPACE, '_'.join(parts))


def _report(client_id, what):
    tracking_id = getattr(settings, 'GOOGLE_ANALYTICS_TRACKING_ID', None)
    if tracking_id and client_id:
        ga.report(tracking_id, client_id, what)


def report_view(client_id, path, host_name=None, referrer=None):
    pv = ga.PageView(path, host_name=host_name, referrer=referrer)
    _report(client_id, pv)


def report_order(client_id, order):
    for group in order:
        items = [ga.Item(oi.product_name,
                         oi.get_price_per_item(),
                         quantity=oi.quantity,
                         item_id=oi.product.sku)
                 for oi in group]
        trans = ga.Transaction('%s-%s' % (order.id, group.id), items,
                               revenue=group.get_total(), shipping=group.price)
        _report(client_id, trans)
