"""Media-slot compositions. All footage and screenshots come from imported inputs."""
from pathlib import Path

from PIL import Image, ImageDraw

from .graphics import text_box
from .models import COMPOSITION_IDS, ValidationError


def even(value):
    return max(2, int(value) // 2 * 2)


def boxes(project, size):
    w, h = size
    c = project["composition"]
    foreground = (int(c["x"] * w), int(c["y"] * h), even(c["width"] * w), even(c["height"] * h))
    if project["format"] == "stack":
        cut = even(c["height"] * h)
        return (0, cut, w, h - cut), (0, 0, w, cut)
    return (0, 0, w, h), foreground


def require_inputs(project):
    if project["format"] not in COMPOSITION_IDS:
        return
    for index, scene in enumerate(project["scenes"]):
        if not scene["media"]:
            raise ValidationError(f"Shot {index+1}: add your background/primary clip. No footage is generated automatically.")
        if project["format"] != "focus" and not scene["secondary_media"]:
            raise ValidationError(f"Shot {index+1}: add your foreground screenshot or clip.")


def empty_canvas(project, scene, size, path):
    w, h = size
    image = Image.new("RGB", size, "#121212")
    draw = ImageDraw.Draw(image)
    bg, fg = boxes(project, size)
    if not scene["media"]:
        text_box(draw, "BACKGROUND CLIP", (w*.10, h*.65, w*.80, h*.06), "#999999", w*.035, True, "center", minimum=5)
        text_box(draw, "Your footage goes here", (w*.10, h*.72, w*.80, h*.04), "#777777", w*.025, False, "center", minimum=5)
    if project["format"] != "focus" and not scene["secondary_media"]:
        x, y, fw, fh = fg
        draw.rectangle((x, y, x+fw, y+fh), fill="#242424", outline="#777777", width=1)
        text_box(draw, "SCREENSHOT / CLIP", (x+fw*.08, y+fh*.38, fw*.84, fh*.16), "#eeeeee", w*.032, True, "center", minimum=5)
    image.save(path)


def cta_image(project, size, path):
    w, h = size
    width, height = even(w*.76), even(h*.061)
    image = Image.new("RGBA", (width, height))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((0, 0, width-1, height-1), radius=int(height*.22), fill="#ffffff")
    play_x = int(height*.28)
    draw.rounded_rectangle((play_x, height*.25, play_x+height*.66, height*.75), radius=height*.08, fill="#e32b2b")
    draw.polygon([(play_x+height*.26,height*.34),(play_x+height*.26,height*.66),(play_x+height*.49,height*.5)], fill="white")
    text_box(draw, project["composition"]["cta_text"], (height*1.15,height*.24,width-height*1.3,height*.55),
             "#111111", height*.34, True, "center", minimum=max(5,int(height*.18)))
    image.save(path)


def scene_inputs(project, scene, index, assets, work, size, preview_time=None):
    w, h = size
    c = project["composition"]
    fps = project["fps"]
    bg_box, fg_box = boxes(project, size)
    base = Path(work)/f"composition-{index}-base.png"
    empty_canvas(project, scene, size, base)
    args = ["-loop","1","-framerate",str(fps),"-i",str(base)]
    filters = []
    current = "0:v"
    next_input = 1
    selected_audio = None
    source_key = {"background":"media","foreground":"secondary_media"}.get(c["audio_source"])
    if project["format"]=="focus" and source_key is not None:
        source_key="media"
    time_expr = "t" if preview_time is None else f"(t+{preview_time:.4f})"
    at = scene["effect_at"]
    pulse = f"max(0,1-abs({time_expr}-{at})/{c['effect_duration']})"

    def add_input(key):
        nonlocal next_input, selected_audio
        asset = assets[scene[key]]
        slot = next_input
        next_input += 1
        if asset["kind"] == "image":
            args.extend(["-loop","1","-framerate",str(fps),"-i",str(asset["path"])])
        else:
            offset = scene["media_start" if key=="media" else "secondary_start"]
            if preview_time is not None:
                offset = (offset+preview_time) % asset["duration"]
            args.extend(["-stream_loop","-1","-ss",str(round(offset,4)),"-i",str(asset["path"])])
        if scene["source_audio"] and key == source_key and asset["has_audio"]:
            selected_audio = slot
        return slot

    def fit(slot, rect, mode, label, blur=False):
        _, _, pw, ph = rect
        if mode == "contain":
            scale = f"scale={pw}:{ph}:force_original_aspect_ratio=decrease:force_divisible_by=2"
        else:
            scale = (f"scale={pw}:{ph}:force_original_aspect_ratio=increase:force_divisible_by=2,"
                     f"crop={pw}:{ph}:(iw-ow)*{scene['focus_x']}:(ih-oh)*{scene['focus_y']}")
        filters.append(f"[{slot}:v]setpts=PTS-STARTPTS,{scale},setsar=1,fps={fps},format=rgba"+
                       (",gblur=sigma=24" if blur else "")+f"[{label}]")

    if scene["media"]:
        bg = add_input("media")
        fit(bg, bg_box, "cover" if project["format"]=="focus" else scene["fit"], "bg", project["format"]=="focus")
        x,y,bw,bh = bg_box
        filters.append(f"[{current}][bg]overlay=x='{x}+({bw}-overlay_w)/2':y='{y}+({bh}-overlay_h)/2':shortest=1[withbg]")
        current = "withbg"
    foreground_key = "media" if project["format"]=="focus" else "secondary_media"
    if scene[foreground_key]:
        foreground = add_input(foreground_key)
        fit(foreground, fg_box, c["foreground_fit"], "fgfit")
        foreground_label = "fgfit"
        border = round(c["border_width"]*w/720)
        if border:
            filters.append(f"[{foreground_label}]drawbox=x=0:y=0:w=iw:h=ih:color={c['border_color'].replace('#','0x')}:t={max(1,border)}[bordered]")
            foreground_label = "bordered"
        # Keep intermediate frame dimensions constant. Dynamic-size scaling before
        # split/pad/gblur can corrupt FFmpeg's frame buffers on Windows builds.
        # The final fixed-size zoom below supplies the timed punch instead.
        x,y,fw,fh = fg_box
        shake_x = f"+{w*.009}*{pulse}*sin({time_expr}*85)" if c["effect"]=="shake" else ""
        shake_y = f"+{h*.004}*{pulse}*cos({time_expr}*72)" if c["effect"]=="shake" else ""
        # Contain preserves the screenshot, centered horizontally and anchored at its top.
        center_y = f"+({fh}-overlay_h)/2" if project["format"] in ("focus","stack") else ""
        if c["glow"]:
            radius = max(1,c["glow"]*w/720)
            margin = even(radius*3)
            filters.append(f"[{foreground_label}]split[sharp][halo_source]")
            filters.append(f"[halo_source]pad=iw+{margin*2}:ih+{margin*2}:{margin}:{margin}:color=0x00000000,gblur=sigma={radius}[halo]")
            halo_y=f"{y}+({fh}-overlay_h)/2" if center_y else f"{y}-{margin}"
            filters.append(f"[{current}][halo]overlay=x='{x}+({fw}-overlay_w)/2{shake_x}':y='{halo_y}{shake_y}':shortest=1[withhalo]")
            current = "withhalo"; foreground_label = "sharp"
        filters.append(f"[{current}][{foreground_label}]overlay=x='{x}+({fw}-overlay_w)/2{shake_x}':y='{y}{center_y}{shake_y}':shortest=1[composited]")
        current = "composited"
    if c["effect"]=="punch":
        zoom_time=str(preview_time) if preview_time is not None else 'in_time'
        zoom_pulse=f"max(0,1-abs(({zoom_time}-{at})/{c['effect_duration']}))"
        filters.append(f"[{current}]zoompan=z='1+0.065*{zoom_pulse}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w}x{h}:fps={fps}[punched]")
        current='punched'
    if c["effect"]=="flash":
        filters.append(f"[{current}]drawbox=x=0:y=0:w=iw:h=ih:color=white@0.65:t=fill:enable='between({time_expr},{at},{at+.075})'[flashed]")
        current = "flashed"
    if c["cta"]:
        elapsed = sum(s["duration"] for s in project["scenes"][:index])
        start = c["cta_at"]-elapsed
        end = start+c["cta_duration"]
        path = Path(work)/"cta.png"
        cta_image(project,size,path)
        args.extend(["-loop","1","-framerate",str(fps),"-i",str(path)])
        # Entrance is a short slide; the label is part of the composition, not YouTube's UI.
        filters.append(f"[{current}][{next_input}:v]overlay=x='(main_w-overlay_w)/2':y='{h*.83}+{h*.025}*max(0,1-({time_expr}-{start})/.18)':enable='between({time_expr},{start},{end})':shortest=1[withcta]")
        current = "withcta"
    filters.append(f"[{current}]format=yuv420p,setsar=1[v]")
    return args, filters, selected_audio
