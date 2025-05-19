from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=120, null=False)
    price = models.PositiveIntegerField(default=1)
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary')
    ]
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to="items/", null=True, blank=True)

    CATEGORY_CHOICES = [
        ('card', 'Card'),
        ('dice', 'Dice'),
    ]
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)

class Case(models.Model):
    name = models.CharField(max_length=120, null=False)
    price = models.PositiveIntegerField(default=1)
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary')
    ]
    rarity = models.CharField(max_length=15, choices=RARITY_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to="items/", null=True, blank=True)

    items = models.ManyToManyField(Item, related_name='cases')
