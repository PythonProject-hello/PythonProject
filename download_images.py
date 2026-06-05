import urllib.request
import os
from PIL import Image
from io import BytesIO

# Discord CDN URLs
urls = [
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508728319779278939/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508728444182073374/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508728702089953280/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508728854053654548/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508729016750702653/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508729391822274721/image.png",
    "https://cdn.discordapp.com/attachments/1502186146560741497/1508729647268106350/image.png",
]

filenames = ["mood1.png", "mood2.png", "mood3.png", "mood4.png", "mood5.png", "mood6.png", "mood7.png"]

os.makedirs("assets", exist_ok=True)

for i, url in enumerate(urls):
    try:
        print(f"Downloading image {i+1}/7...", end=" ", flush=True)
        response = urllib.request.urlopen(url, timeout=10)
        img_data = response.read()
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        # 크기를 300x260으로 리사이즈
        img.thumbnail((300, 260), Image.LANCZOS)
        # 가운데 정렬을 위해 새로운 이미지에 붙이기
        new_img = Image.new("RGBA", (300, 260), (0, 0, 0, 0))
        offset = ((300 - img.width) // 2, (260 - img.height) // 2)
        new_img.paste(img, offset, img)
        new_img.save(f"assets/{filenames[i]}")
        print("✓")
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n모든 이미지 다운로드 완료!")
