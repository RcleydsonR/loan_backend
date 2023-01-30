
from core.consts.urls import UUID4_URL

from django.urls import include, re_path

from loan.views import loan

urlpatterns = [
    re_path(r'^loan/', include([
        re_path(r'^$', loan.LoanAPIView.as_view(), name='loan-create-list'),

        re_path(r'^(?P<pk>{})/$'.format(UUID4_URL),
            loan.LoanRetrieveUpdateAPIView.as_view(),
            name='loan-detail-update'),
    ]))
]
