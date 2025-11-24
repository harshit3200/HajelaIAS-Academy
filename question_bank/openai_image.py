from openai import OpenAI
import requests
from django.core.files.base import ContentFile
from django.conf import settings
from .models import GeneratedImage
from decouple import config

# 🔐 Setup OpenAI client
client = OpenAI(api_key=config("OPENAI_API_KEY"))

def generate_image(prompt, size="1024x1024", count=1):
    generated_images = []

    try:
        # 🌟 Generate one or more images
        response = client.images.generate(
            prompt=prompt,
            n=count,
            size=size,
            model="dall-e-3",  # More realistic results (if supported)
            response_format="url"
        )

        # Loop through each returned image
        for index, image_data in enumerate(response.data):
            image_url = image_data.url
            img_response = requests.get(image_url)

            if img_response.status_code == 200:
                img_data = img_response.content
                img_name = f"generated_{prompt[:30].replace(' ', '_')}_{index + 1}.png"

                image_obj = GeneratedImage(prompt=prompt)
                image_obj.image.save(img_name, ContentFile(img_data), save=True)
                generated_images.append(image_obj)

        return generated_images

    except Exception as e:
        print("OpenAI Image Generation Error:", e)
        return []
