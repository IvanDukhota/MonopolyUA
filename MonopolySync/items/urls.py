from django.urls import path
from .views import *


urlpatterns = [
    path('items/', ItemsListAPIView.as_view()),
    path('item/<int:item_id>', ItemView.as_view()),
    path('item/buy/<int:listing_id>', BuyItemAPIView.as_view()),
    path('item/buy-multiple/<int:item_id>', BuyMultipleItemAPIView.as_view()),
    path('user-sell/', UserSellListView.as_view()),
    path('user-sell/delete/<int:listing_id>', UserSellListView.as_view()),
    path('user-inventory/', InventoryView.as_view()),
    path('item/sell/', SellItemView.as_view()),
    path('open-case/', OpenCaseAPIView.as_view()),
    path('default-board/', DefaultBoardAPIView.as_view())
]