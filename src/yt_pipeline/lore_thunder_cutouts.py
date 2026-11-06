"""Source-cutout cast for the same geometric Thor shot recipes."""
from dataclasses import dataclass
import math

from PIL import Image, ImageEnhance, ImageOps

from .assets import asset_record
from .core import Held


@dataclass(frozen=True)
class Sprite:
    image: Image.Image
    start: tuple
    end: tuple
    shoulder: tuple | None = None


def load_thunder_cast(workspace, request):
    names = request.get("thunder_cast")
    if names is None:
        return None, []
    if not isinstance(names, dict) or set(names) != {"bill", "thor"}:
        raise Held("thunder_cast", "Supply registered cutout layers for Bill and Thor.")
    actors = {}
    assets = []
    preview = request.get("test_only") is True
    for who, parts in names.items():
        if not isinstance(parts, dict) or set(parts) != {"body", "upper", "forearm"}:
            raise Held("thunder_cast", "A source actor needs a body, upper arm and forearm.")
        actors[who] = {}
        for role, asset_id in parts.items():
            if not isinstance(asset_id, str):
                raise Held("thunder_cast", "Use registered IDs for the cast layers.")
            asset = asset_record(workspace, asset_id, allow_preview=preview)
            if asset["kind"] != "image" or (asset["test_only"] and not preview):
                raise Held("thunder_cast", "The cast needs eligible transparent images.")
            with Image.open(asset["path"]) as original:
                image = original.convert("RGBA")
            start = _point(asset, image, "start")
            end = _point(asset, image, "end")
            if (image.getchannel("A").getextrema() != (0, 255) or math.dist(start, end) < 12
                    or (role == "body" and end[1] <= start[1]+12)):
                raise Held("thunder_cast", "The layer needs a transparent edge and distinct anchors.")
            rgb = ImageEnhance.Color(image.convert("RGB")).enhance(.85)
            rgb = ImageEnhance.Contrast(rgb).enhance(1.02)
            rgb.putalpha(image.getchannel("A"))
            actors[who][role] = Sprite(rgb, start, end, _point(asset, image, "shoulder") if role == "body" else None)
            assets.append(asset)
    return ThunderCutouts(actors), assets


def _point(asset, image, key):
    point = asset.get("evidence", {}).get(key)
    if (not isinstance(point, list) or len(point) != 2
            or any(type(value) not in (int, float) or not 0 <= value < bound
                   for value, bound in zip(point, image.size))):
        raise Held("thunder_cast", "Each registered layer needs two valid pixel anchors.")
    return tuple(point)


class ThunderCutouts:
    def __init__(self, actors):
        self.actors = actors
        self.bodies = {}

    def warrior(self, layer, who, x, y, scale, facing):
        key = (who, scale, facing)
        if key not in self.bodies:
            sprite = self.actors[who]["body"]
            base = (165 if who == "bill" else 175) * scale / (sprite.end[1] - sprite.start[1])
            target = sprite.image.resize(tuple(max(1, round(value * base)) for value in sprite.image.size),
                                         Image.Resampling.LANCZOS)
            start, shoulder = sprite.start, sprite.shoulder
            if facing == -1:
                target = ImageOps.mirror(target)
                start = (sprite.image.width - 1 - start[0], start[1])
                shoulder = (sprite.image.width - 1 - shoulder[0], shoulder[1])
            self.bodies[key] = (target, (start[0]*base, start[1]*base),
                                ((shoulder[0]-start[0])*base, (shoulder[1]-start[1])*base))
        target, head, shoulder = self.bodies[key]
        layer.alpha_composite(target, dest=(round(x-head[0]), round(y-head[1])))
        return who, (x+shoulder[0], y+shoulder[1]), facing

    def reach(self, layer, actor, elbow, hand, scale):
        who, shoulder, facing = actor
        layers = self.actors[who]
        # Move the elbow onto the new source shoulder's arm plane without
        # changing the authored hand contact with the hammer or other actor.
        self._limb(layer, layers["upper"], shoulder, elbow, facing, scale)
        self._limb(layer, layers["forearm"], elbow, hand, facing, scale)

    @staticmethod
    def _limb(layer, sprite, start, end, facing, scale):
        x0, y0 = sprite.start
        x1, y1 = sprite.end
        source_length = math.hypot(x1-x0, y1-y0)
        sx, sy = (x1-x0)/source_length, (y1-y0)/source_length
        dx, dy = end[0]-start[0], end[1]-start[1]
        length = math.hypot(dx, dy)
        if length < 5:
            return
        ux, uy = dx/length, dy/length
        along = length/source_length
        across = 33*scale / max(23, min(sprite.image.size))
        # The perpendicular basis can flip independently for the reverse view.
        across *= facing
        width, height = sprite.image.size
        corners = []
        for px, py in ((0,0),(width,0),(0,height),(width,height)):
            a = ((px-x0)*sx+(py-y0)*sy)*along
            b = (-(px-x0)*sy+(py-y0)*sx)*across
            corners.append((start[0]+a*ux-b*uy,start[1]+a*uy+b*ux))
        left = max(0, math.floor(min(x for x, _ in corners)))
        top = max(0, math.floor(min(y for _, y in corners)))
        right = min(layer.width, math.ceil(max(x for x, _ in corners)))
        bottom = min(layer.height, math.ceil(max(y for _, y in corners)))
        if right <= left or bottom <= top:
            return
        a = sx*ux/along + sy*uy/across
        b = sx*uy/along - sy*ux/across
        d = sy*ux/along - sx*uy/across
        e = sy*uy/along + sx*ux/across
        offset_x, offset_y = left-start[0], top-start[1]
        part = sprite.image.transform((right-left, bottom-top), Image.Transform.AFFINE,
                                      (a,b,x0+a*offset_x+b*offset_y,d,e,y0+d*offset_x+e*offset_y),
                                      Image.Resampling.BICUBIC)
        layer.alpha_composite(part, dest=(left,top))
