"""Small readable app palettes and original, optional patterned wallpapers."""
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageOps, ImageEnhance


@dataclass(frozen=True)
class Theme:
    background: str
    chrome: str
    ink: str
    muted: str
    incoming: str
    outgoing: str
    incoming_ink: str
    accent: str


PALETTES = {
    'light': Theme('#ffffff', '#f7f7f9', '#18181b', '#85858d', '#e9e9eb', '#007aff', '#151518', '#007aff'),
    'dark': Theme('#10151d', '#181e28', '#f3f5fa', '#a7b0c1', '#2c3545', '#2867c9', '#f4f6fb', '#84b4ff'),
    'rose': Theme('#fff4f6', '#fff8fa', '#342b36', '#887384', '#ffffff', '#ae3d78', '#342b36', '#ae3d78'),
    'sage': Theme('#eff5f0', '#f6faf7', '#20372f', '#71877b', '#ffffff', '#267862', '#20372f', '#267862')}


def wallpaper(name='light', photo=None):
    theme = PALETTES[name]
    image = Image.new('RGB', (720, 1280), theme.background)
    if photo is not None:
        photo = ImageOps.fit(photo, image.size, method=Image.Resampling.LANCZOS)
        image = Image.blend(image, ImageEnhance.Color(photo).enhance(.4), .16 if name != 'dark' else .28)
    elif name != 'light':
        layer = Image.new('RGBA', image.size); d = ImageDraw.Draw(layer)
        color = (170, 186, 210, 18) if name == 'dark' else (175, 113, 151, 16) if name == 'rose' else (74, 128, 110, 16)
        for y in range(220, 1124, 110):
            for x in range(-30, 750, 110):
                # Original code-drawn speech outlines; no downloaded app artwork.
                d.rounded_rectangle((x, y, x+32, y+25), radius=9, outline=color, width=2)
                d.line((x+8,y+25,x+5,y+31,x+18,y+25),fill=color,width=2)
        image = Image.alpha_composite(image.convert('RGBA'), layer).convert('RGB')
    return image
