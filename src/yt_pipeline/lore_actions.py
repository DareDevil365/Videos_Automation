"""Reusable geometric action overlays. Coordinates follow the 720px story canvas."""
import math

from PIL import Image, ImageDraw

from .core import Held


COLORS = {
    "optic_blast": ("#e64549", "#ffdddd"),
    "repulsor": ("#58b9db", "#ecfdff"),
    "hammer_lightning": ("#729dec", "#e4f6ff"),
    "doom_magic": ("#44bc7a", "#c4ffe2"),
    "sorcerer_rings": ("#da893b", "#ffe2a0"),
    "ground_impact": ("#74ac69", "#e9f5b3"),
}


def resolve_actions(request, script):
    raw = request.get("lore_actions", {})
    if not isinstance(raw, dict) or raw.keys() - {unit["id"] for unit in script["units"]}:
        raise Held("lore_action", "Assign actions to existing comic beats.")
    result = {}
    for unit, row in raw.items():
        if (not isinstance(row, dict) or not isinstance(row.get("kind"), str) or row["kind"] not in COLORS
                or row.get("actor", "effect_only") not in ("symbolic", "effect_only")):
            raise Held("lore_action", "Choose a supported action and symbolic or effect-only staging.")
        origin = action_point(row.get("origin", [365, 500]))
        target = action_point(row["target"]) if "target" in row else None
        result[unit] = (row["kind"], origin, row.get("actor") == "symbolic", target)
    return result


def action_point(point):
    if (not isinstance(point, list) or len(point) != 2
            or any(type(value) is not int for value in point)
            or not 70 <= point[0] <= 650 or not 245 <= point[1] <= 785):
        raise Held("lore_action", "Keep action anchors inside the main story panel.")
    return tuple(point)


def draw_action(frame, action, second, duration):
    kind, (x, y), symbolic, target = action
    color, light = COLORS[kind]
    art = Image.new("RGBA", (720, 690))
    d = ImageDraw.Draw(art)
    y -= 194
    p = min(1, second / duration)
    if kind == "ground_impact":
        draw_impact(d, x, y, p, symbolic, color, light)
        frame.paste(art, (0, 194), art)
        return
    ramp = min(1, max(0, (p - .08) * 4))
    pulse = .85 + .15 * math.sin(second * 11)
    reach = -1 if x > 385 else 1
    if symbolic:
        # A single articulated silhouette with a readable hand or visor anchor.
        head_x = x - reach * (22 if kind == "optic_blast" else 107)
        head_y = y if kind == "optic_blast" else y - 45
        d.polygon([(head_x-48, head_y+64), (head_x+48, head_y+64),
                   (head_x+70, head_y+218), (head_x-70, head_y+218)],
                  fill="#223638", outline=color, width=4)
        elbow = (head_x + 55 * reach, y + 58 - 28 * ramp)
        d.line([(head_x, head_y+81), elbow, (x, y)], fill=color, width=24, joint="curve")
        d.line([(head_x, head_y+81), elbow, (x, y)], fill="#314647", width=16, joint="curve")
        d.polygon([(head_x-35, head_y-23), (head_x, head_y-47), (head_x+36, head_y-22),
                   (head_x+30, head_y+26), (head_x, head_y+48), (head_x-29, head_y+25)],
                  fill="#48595a", outline=light, width=3)
        d.line((head_x-21, head_y, head_x+25, head_y), fill=light, width=6)
        if kind == "hammer_lightning":
            d.line((x, y+17, x, y-40), fill="#c9ab80", width=8)
            d.rectangle((x-25, y-53, x+25, y-30), fill="#819aab", outline=light, width=3)
    if ramp:
        if kind in ("optic_blast", "repulsor"):
            tx, ty = (target[0], target[1]-194) if target else (x + reach * 300, y - (18 if kind == "repulsor" else 0))
            line = [(x, y), (x + (tx-x)*ramp, y + (ty-y)*ramp)]
            d.line(line, fill=color, width=max(4, round(23 * pulse)))
            d.line(line, fill=light, width=6)
        elif kind == "hammer_lightning":
            points = [(x, y-44)]
            tx, ty = (target[0], target[1]-194) if target else (x, y-254)
            for n in range(1, 6):
                t = n / 5 * ramp
                jitter = math.sin(n*2.15 + second*25)*22 if n < 5 else 0
                points.append((x + (tx-x)*t + jitter, y-44 + (ty-y+44)*t))
            d.line(points, fill=color, width=14, joint="curve")
            d.line(points, fill=light, width=5, joint="curve")
        else:
            for n in range(3):
                radius = round((24 + 24*n) * ramp * pulse)
                d.arc((x-radius,y-radius,x+radius,y+radius),
                      second*(78+18*n)+n*42, second*(78+18*n)+n*42+287,
                      fill=light if n == 0 else color, width=3 if n else 5)
            if kind == "doom_magic":
                d.ellipse((x-10,y-10,x+10,y+10), fill=light)
            for n in range(7):
                angle = n * math.tau / 7 + second * .9
                dx, dy = math.cos(angle) * 89 * ramp, math.sin(angle) * 89 * ramp
                d.ellipse((x+dx-2,y+dy-2,x+dx+2,y+dy+2), fill=color)
        if target and .46 <= p < .72:
            tx, ty = target[0], target[1]-194
            for i in range(8):
                angle = math.tau*i/8
                length = (p-.44)*156
                dx, dy = math.cos(angle)*length, math.sin(angle)*length
                d.line([(tx+dx*.45,ty+dy*.45),(tx+dx,ty+dy)], fill=light, width=4)
    frame.paste(art, (0, 194), art)


def draw_impact(draw, x, y, p, symbolic, color, light):
    drop = min(1, p / .46)
    land = max(0, min(1, (p-.46)*8))
    feet = y - 230*(1-drop**2) + 46*land
    if symbolic:
        shoulder = feet - 129 + 17*land
        draw.polygon([(x-79,shoulder),(x-36,shoulder-22),(x+36,shoulder-22),
                      (x+79,shoulder),(x+58,feet-48),(x+30,feet-39),
                      (x+62,feet),(x+17,feet),(x,feet-31),(x-17,feet),
                      (x-62,feet),(x-30,feet-39),(x-58,feet-48)],
                     fill="#274c38", outline=color, width=5)
        draw.polygon([(x-27,shoulder-31),(x-22,shoulder-62),(x+19,shoulder-64),
                      (x+31,shoulder-40),(x+23,shoulder-17),(x-20,shoulder-17)],
                     fill="#6c9a56", outline=light, width=3)
        draw.line((x-15,shoulder-41,x+17,shoulder-41),fill="#203128",width=5)
    if .46 <= p <= .83:
        for side in (-1,1):
            spread = (p-.46)*230
            draw.line([(x+side*32,y),(x+side*(56+spread),y-9),
                       (x+side*(93+spread),y-42)], fill=light, width=4)
