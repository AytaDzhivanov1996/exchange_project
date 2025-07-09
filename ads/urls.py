from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ads import views
from ads.api_views import AdViewSet, ExchangeProposalViewSet

router = DefaultRouter()
router.register(r'ads', AdViewSet)
router.register(r'exchange-proposals', ExchangeProposalViewSet, basename='exchangeproposal')

urlpatterns = [
    path('', views.ad_list, name='ad_list'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ads/create/', views.ad_create, name='ad_create'),
    path('ads/<int:pk>/edit/', views.ad_edit, name='ad_edit'),
    path('ads/<int:pk>/delete/', views.ad_delete, name='ad_delete'),
    path('ads/<int:ad_id>/exchange/', views.create_exchange_proposal, name='create_exchange_proposal'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/<int:proposal_id>/update/', views.update_proposal_status, name='update_proposal_status'),
    path('my-ads/', views.my_ads, name='my_ads'),
    path('api/', include(router.urls))
]