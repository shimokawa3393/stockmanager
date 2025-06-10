from django.urls import path
from .views import MainView, SearchSymbolView, FetchCompanyDataView, SaveStockSymbolView, RemoveStockSymbolView

urlpatterns = [
    path('main/', MainView.as_view(), name='main'),
    path('search/', SearchSymbolView.as_view(), name='search'),
    path('fetch/', FetchCompanyDataView.as_view(), name='fetch'),
    path('save/', SaveStockSymbolView.as_view(), name='save'),
    path('remove/', RemoveStockSymbolView.as_view(), name='remove'),
]
