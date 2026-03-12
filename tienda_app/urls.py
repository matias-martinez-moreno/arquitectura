from django.urls import path
from .api.views import CompraAPIView
from .views import CompraView, CompraRapidaView, compra_rapida_fbv, home

urlpatterns = [
    path('', home, name='home'),
    path('compra/<int:libro_id>/', CompraView.as_view(), name='finalizar_compra'),
    path('compra-rapida/<int:libro_id>/', CompraRapidaView.as_view(), name='compra_rapida_fbv'),
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]