from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Item, InventoryItem, MarketListing
from registration.models import User
from .serializers import ItemSerializer
from django.db import transaction

class ItemsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)


class ItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        serializer = ItemSerializer(item, context={'request': request})
        return Response(serializer.data)

class InventoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        inventory_items = InventoryItem.objects.filter(user=request.user).select_related('item')
        data = []
        for inv in inventory_items:
            data.append({
                'inventory_item_id': inv.id,
                'item_id': inv.item.id,
                'name': inv.item.name,
                'category': inv.item.category,
                'quantity': inv.quantity,
                'image': inv.item.image.url if inv.item.image else None,
            })
        return Response(data)


class BuyItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, listing_id):
        listing = get_object_or_404(MarketListing, id=listing_id)


        price = listing.user_price
        buyer = request.user
        seller = listing.seller

        if buyer.game_currency < price:
            return Response({'error': 'Not enough money.'}, status=status.HTTP_400_BAD_REQUEST)

        buyer.game_currency -= price
        buyer.save(update_fields=['game_currency'])

        seller.game_currency += price
        seller.save(update_fields=['game_currency'])

        inv_item, created = InventoryItem.objects.get_or_create(
            user=buyer,
            item=listing.item,
            defaults={'quantity': 0}
        )
        inv_item.quantity += 1
        inv_item.save(update_fields=['quantity'])

        listing.delete()

        return Response({
            'message': f'You bought 1 × {listing.item.name}',
            'item_id': listing.item.id,
            'remaining_in_listing': listing.quantity if listing.pk else 0
        }, status=status.HTTP_200_OK)




