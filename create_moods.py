from PIL import Image, ImageDraw

# mood 상태별 색상 및 이미지 생성
specs = [
    ("mood1.png", (255, 107, 107), "😤", "hard_work"),  # Red - 힘들어
    ("mood2.png", (255, 209, 102), "😫", "hungry"),      # Yellow - 배고파
    ("mood3.png", (98, 168, 255), "😢", "sad"),          # Blue - 어디있어?
    ("mood4.png", (98, 168, 255), "😋", "full"),         # Blue variant - 배불러
    ("mood5.png", (185, 140, 204), "😌", "calm"),        # Purple - 조용함
    ("mood6.png", (125, 216, 125), "😊", "good"),        # Green - 좋아
    ("mood7.png", (125, 216, 125), "😌", "peaceful"),    # Green - 편안해
]

import os
os.makedirs("assets", exist_ok=True)

for filename, color, emoji, mood in specs:
    path = os.path.join("assets", filename)
    # 300x260 크기의 이미지 생성
    img = Image.new("RGBA", (300, 260), color + (255,))
    draw = ImageDraw.Draw(img)
    
    # 하얀 원형 몸체
    draw.ellipse((30, 20, 270, 240), fill=(255, 255, 255, 255))
    
    # 선글라스 눈 (큰 사각형)
    draw.rectangle((90, 85, 135, 115), fill=(30, 30, 30, 255))
    draw.rectangle((165, 85, 210, 115), fill=(30, 30, 30, 255))
    
    # 광택 (highlight)
    draw.ellipse((100, 90, 115, 100), fill=(255, 255, 255, 200))
    draw.ellipse((175, 90, 190, 100), fill=(255, 255, 255, 200))
    
    # 볼
    draw.ellipse((95, 130, 125, 150), fill=(255, 182, 193, 255))
    draw.ellipse((175, 130, 205, 150), fill=(255, 182, 193, 255))
    
    # 입: 미소
    draw.arc((128, 120, 160, 150), start=200, end=340, fill=(60, 60, 60, 255), width=3)
    
    img.save(path)
    print(f"✓ {filename} created")

print(f"\n총 {len(specs)}개 이미지 생성 완료!")
