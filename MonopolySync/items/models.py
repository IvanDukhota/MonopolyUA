from django.db import models
from registration.models import User

class Item(models.Model):
    CATEGORY_CARD = 'card'
    CATEGORY_DICE = 'dice'
    CATEGORY_CASE = 'case'
    CATEGORY_CHOICES = [
        (CATEGORY_CARD, 'Card'),
        (CATEGORY_DICE, 'Dice'),
        (CATEGORY_CASE, 'Case'),
    ]

    RARITY_COMMON = 'common'
    RARITY_RARE = 'rare'
    RARITY_EPIC = 'epic'
    RARITY_LEGENDARY = 'legendary'
    RARITY_CHOICES = [
        (RARITY_COMMON, 'Common'),
        (RARITY_RARE, 'Rare'),
        (RARITY_EPIC, 'Epic'),
        (RARITY_LEGENDARY, 'Legendary'),
    ]

    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField(default=1)
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to="items/", null=True, blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.category})"


class CaseItemContent(models.Model):
    case = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='case_contents',
        limit_choices_to={'category': Item.CATEGORY_CASE}
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='contained_in_cases_contents'
    )
    def __str__(self):
        return f"{self.item.name} in case {self.case.name}"

class MarketListing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_listings')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user_price = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller.username} sells {self.quantity} x {self.item.name} at {self.price}"


class InventoryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=False)
    def __str__(self):
        return f"{self.user.username} - {self.item.name}"




