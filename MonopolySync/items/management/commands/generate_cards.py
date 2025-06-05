from django.core.management.base import BaseCommand
import os
import random
from django.conf import settings
from items.models import Item
from django.core.files import File


class Command(BaseCommand):
    help = "Generate items from images in media/items"

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        items_path = os.path.join(media_root, "items")

        # image_files = [f for f in os.listdir(items_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        # if not image_files:
        #     self.stdout.write(self.style.ERROR("No image files found in media/items"))
        #     return
        #
        # for image_file in image_files:
        #     name = os.path.splitext(image_file)[0]
        #     price = random.randint(1, 10)
        #     category = 'card'
        #     rarity = 'common'
        #
        #     image_path = os.path.join("items", image_file)
        #
        #     Item.objects.create(
        #         name=name,
        #         price=price,
        #         rarity=rarity,
        #         category=category,
        #         image=image_path,
        #         is_default=True
        #     )
        #
        # self.stdout.write(self.style.SUCCESS(f"Created {len(image_files)} items successfully."))


        non_default_images = [
            "xiaomi.png",
            "versace.png",
            "ubisoft.png",
            "twitter.png",
            "tiktok.png",
            "starbucks.png",
            "shahtar.png",
            "pinterest.png",
            "Iv.png",
            "gucci.png",
            "gmail.png",
            "dynamo.png"
        ]

        rarities = ['common', 'rare', 'epic', 'legendary']
        category = 'card'

        for image_file in non_default_images:
            name = os.path.splitext(image_file)[0]
            price = random.randint(10, 100)
            rarity = random.choice(rarities)

            image_path = os.path.join("items", image_file)
            Item.objects.create(
                name=name,
                price=price,
                rarity=rarity,
                category=category,
                image=image_path,
                is_default=False
            )

        self.stdout.write(
            self.style.SUCCESS(f"Created {len(non_default_images)} non-default items with random rarity successfully."))
