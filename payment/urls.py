
from core.consts.urls import UUID4_URL

from django.urls import include, re_path

from payment.views import payment

urlpatterns = [
    re_path(r'^payment/', include([
        re_path(r'^$', payment.PaymentAPIView.as_view(), name='payment-create-list'),

        re_path(r'^(?P<pk>{})/$'.format(UUID4_URL),
            payment.PaymentRetrieveUpdateAPIView.as_view(),
            name='payment-detail-update'),
    ]))
]
