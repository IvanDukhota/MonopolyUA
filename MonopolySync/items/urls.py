from django.urls import path
from .views import ItemsListAPIView, ItemView, BuyItemAPIView


urlpatterns = [
    path('items/', ItemsListAPIView.as_view()),
    path('item/<int:item_id>', ItemView.as_view()),
    path('item/buy/<int:listing_id>', BuyItemAPIView.as_view())
]