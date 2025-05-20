from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Item, InventoryItem, MarketListing, CaseItemContent
from registration.models import User
from .serializers import ItemSerializer
from django.db import transaction
from .serializers import MarketListingSerializer, UserListingSerializer, InventoryItemSerializer
import random

class ItemsListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

class UserSellListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_listings = MarketListing.objects.filter(seller=request.user)
        serializer = UserListingSerializer(user_listings, many=True, context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    def delete(self, request, listing_id):
        if not listing_id:
            return Response({'detail': 'Не вказано listing_id.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            listing = MarketListing.objects.get(id=listing_id, seller=request.user)
        except MarketListing.DoesNotExist:
            return Response({'detail': 'Лот не знайдено або не належить вам.'}, status=status.HTTP_404_NOT_FOUND)

        inventory_item, created = InventoryItem.objects.get_or_create(
            user=request.user,
            item=listing.item,
            defaults={'quantity': 1}
        )
        if not created:
            inventory_item.quantity += 1
            inventory_item.save()

        listing.delete()

        return Response({'detail': 'Лот знято з продажу та повернуто в інвентар.'}, status=status.HTTP_200_OK)

class ItemView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)
        serializer = ItemSerializer(item, context={'request': request})
        return Response(serializer.data)


class InventoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        if category:
            category = category.strip().lower()

        inventory_items = InventoryItem.objects.filter(user=request.user).select_related('item')

        if category:
            valid_categories = [choice[0].lower() for choice in Item.CATEGORY_CHOICES]
            print("Valid categories:", valid_categories)
            print("Category from request:", category)

            if category not in valid_categories:
                raise ValidationError({'category': 'Invalid category value'})

            inventory_items = inventory_items.filter(item__category__iexact=category)

        serializer = InventoryItemSerializer(inventory_items, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)




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


class BuyMultipleItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, item_id):
        item = get_object_or_404(Item, id=item_id)

        try:
            user_price = request.data.get('user_price')
            user_quantity = int(request.data.get('user_quantity'))
            if user_quantity <= 0 or user_price <= 0:
                raise ValueError
        except (TypeError, ValueError):
            return Response({'error': 'Invalid price or quantity'}, status=status.HTTP_400_BAD_REQUEST)

        buyer = request.user

        market_listings = MarketListing.objects.filter(item=item, user_price__lte=user_price).order_by('user_price')

        total_available = market_listings.count()
        if total_available < user_quantity:
            return Response({'error': 'Not enough items available in market.'}, status=status.HTTP_400_BAD_REQUEST)

        total_spent = 0
        total_bought = 0

        listings_to_buy = market_listings[:user_quantity]

        for listing in listings_to_buy:
            price = listing.user_price
            if buyer.game_currency < price:
                return Response({'error': 'Not enough money.'}, status=status.HTTP_400_BAD_REQUEST)

            buyer.game_currency -= price
            buyer.save(update_fields=['game_currency'])

            seller = listing.seller
            seller.game_currency += price
            seller.save(update_fields=['game_currency'])

            inv_item, created = InventoryItem.objects.get_or_create(
                user=buyer,
                item=item,
                defaults={'quantity': 0}
            )
            inv_item.quantity += 1
            inv_item.save(update_fields=['quantity'])

            listing.delete()

            total_spent += price
            total_bought += 1

        return Response({
            'message': f'You bought {total_bought} × {item.name} for {total_spent}',
            'item_id': item.id,
        }, status=status.HTTP_200_OK)


class SellItemView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")
        price_item = request.data.get("price")

        if not item_id or not quantity or not price_item:
            return Response({"message": "item_id, quantity and price are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(quantity)
            price_item = int(price_item)
            if quantity <= 0 or price_item <= 0:
                return Response({"message": "quantity and price must be positive nums."},
                                status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"message": "quantity and price must be integers."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response({"message": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            inventory = InventoryItem.objects.get(user=request.user, item=item)
        except InventoryItem.DoesNotExist:
            return Response({"message": "Item not in inventory."}, status=status.HTTP_404_NOT_FOUND)

        if inventory.quantity < quantity:
            return Response({"message": "Not enough items in inventory."}, status=status.HTTP_400_BAD_REQUEST)

        inventory.quantity -= quantity
        if inventory.quantity == 0:
            inventory.delete()
        else:
            inventory.save()

        for i in range(0, quantity):
            MarketListing.objects.create(
                seller=request.user,
                item=item,
                user_price=price_item,
            )

        return Response({"message": f"Successfully listed {quantity} x {item.name} for sale at price {price_item}."},
                        status=status.HTTP_201_CREATED)



RARITY_WEIGHTS = {
    Item.RARITY_COMMON: 50,
    Item.RARITY_RARE: 30,
    Item.RARITY_EPIC: 20,
    Item.RARITY_LEGENDARY: 10,
}

from collections import Counter

class OpenCaseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        case_id = request.data.get("case_id")
        case = get_object_or_404(Item, id=case_id, category=Item.CATEGORY_CASE)

        contents = CaseItemContent.objects.filter(case=case).select_related('item')
        if not contents.exists():
            return Response({'detail': 'Empty case'}, status=status.HTTP_400_BAD_REQUEST)

        rarity_counts = Counter()
        for content in contents:
            rarity_counts[content.item.rarity] += 1

        items = []
        weights = []

        for content in contents:
            rarity = content.item.rarity
            if rarity in RARITY_WEIGHTS and rarity_counts[rarity] > 0:
                items.append(content.item)
                weight_per_item = RARITY_WEIGHTS[rarity] / rarity_counts[rarity]
                weights.append(weight_per_item)

        if not items:
            return Response({'detail': 'No items.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_item = random.choices(items, weights=weights, k=1)[0]

        serializer = ItemSerializer(selected_item)
        return Response(serializer.data, status=status.HTTP_200_OK)




index_list = [1, 3, 6, 8, 9, 11, 13, 14, 16, 18, 19, 21, 23, 24, 26, 27, 29, 31, 32, 34, 37, 39]
card_list = [
    (162, 163), (162, 163), (162, 163), (107, 108), (109, 110),
    (111, 112), (113, 114), (115, 116), (117, 118), (119, 120),
    (121, 122), (123, 124), (162, 163), (127, 128), (129, 130),
    (131, 132), (133, 134), (135, 136), (137, 138), (139, 140),
    (141, 142), (162, 163)
]

class DefaultBoardAPIView(APIView):
    def get(self, request):
        default_cards = list(Item.objects.filter(category=Item.CATEGORY_CARD, is_default=True))
        if len(default_cards) < 40:
            raise ValueError("Not enough default cards")

        selected_defaults = random.sample(default_cards, 40)
        board = []

        for index in range(40):
            cell_number = index + 1
            default_card = selected_defaults[index]
            options = [default_card]

            if cell_number in index_list:
                pos = index_list.index(cell_number)
                skin_ids = card_list[pos]
                skins = list(Item.objects.filter(id__in=skin_ids, is_default=False))
                options.extend(skins)

            cell_data = {
                'cell': cell_number,
                'options': [
                    {
                        'id': card.id,
                        'name': card.name,
                        'rarity': card.rarity,
                        'image': request.build_absolute_uri(card.image.url) if card.image else None,
                    } for card in options
                ]
            }

            board.append(cell_data)

        return Response({'board': board})
