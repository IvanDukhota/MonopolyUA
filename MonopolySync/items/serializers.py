from rest_framework import serializers
from .models import MarketListing, Item, InventoryItem

class MarketListingSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    is_own_listing = serializers.SerializerMethodField()

    class Meta:
        model = MarketListing
        fields = ['id', 'seller_username', 'user_price', 'created_at', 'is_own_listing']

    def get_is_own_listing(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.seller == request.user
        return False

class UserListingSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source='item.name', read_only=True)
    image = serializers.ImageField(source='item.image', read_only=True)
    class Meta:
        model = MarketListing
        fields = '__all__'

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None



class ItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()

    category = serializers.SerializerMethodField()
    rarity = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = [
            'id', 'name', 'category', 'price', 'rarity', 'image',
            'min_price', 'amount'
        ]

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def get_market_listings(self, obj):
        listings = MarketListing.objects.filter(item=obj)
        serializer = MarketListingSerializer(listings, many=True, context=self.context)
        return serializer.data

    def get_min_price(self, obj):
        min_listing = MarketListing.objects.filter(item=obj).order_by('user_price').first()
        return min_listing.user_price if min_listing else 0

    def get_amount(self, obj):
        return MarketListing.objects.filter(item=obj).count()

    def get_category(self, obj):
        return obj.get_category_display()

    def get_rarity(self, obj):
        return obj.get_rarity_display()

class CaseSerializer(serializers.ModelSerializer):
    case_items = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'price', 'case_items']

    def get_case_items(self, obj):
        if obj.category != Item.CATEGORY_CASE:
            return []

        case_contents = obj.case_contents.all()
        items = [content.item for content in case_contents]

        return ItemSerializer(items, many=True, context=self.context).data


class InventoryItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()

    class Meta:
        model = InventoryItem
        fields = ['id', 'item', 'quantity']