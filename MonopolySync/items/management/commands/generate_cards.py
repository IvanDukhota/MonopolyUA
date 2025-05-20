from django.core.management.base import BaseCommand
import random
import os
import requests
from django.conf import settings
from items.models import Item

class Command(BaseCommand):
    help = "Generate 60 cards"

    def handle(self, *args, **kwargs):
        media_root = settings.MEDIA_ROOT
        items_path = os.path.join(media_root, "items")
        os.makedirs(items_path, exist_ok=True)


        def download_card_image(card_id):
            url = f"https://picsum.photos/200"
            response = requests.get(url)
            if response.status_code == 200:
                filename = f"card_{card_id}.jpg"
                filepath = os.path.join(items_path, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return f"items/{filename}"
            return None

        for i in range(1, 41):
            name = f"Card {i}"
            price = random.randint(1, 10)
            category = 'card'
            image_path = download_card_image(i)

            Item.objects.create(
                name=name,
                price=price,
                rarity="common",
                category=category,
                image=image_path,
                is_default=True
            )

        self.stdout.write(self.style.SUCCESS("Success"))
