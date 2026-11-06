"""Compile the hand-authored photo revisions into local, test-only source Shorts."""
from argparse import ArgumentParser
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shorts_editor.store import write_json
from yt_pipeline.assets import register_asset
from yt_pipeline.contracts import script_contract
from yt_pipeline.core import Workspace, digest, now
from yt_pipeline.curated_music import select_genre_music
from yt_pipeline.playbooks import validate_playbook_script


SERIES = (
    (
        "Doom Saved Reality. Then Made It Kneel.",
        (
            ("Doom saved reality and made himself its god. Doom's Broken Worlds, part one.", "DOOM'S BROKEN WORLDS · PART 1", "dominion", "2 4"),
            ("Two universes were about to collide. Reed Richards built a raft to get people out.", "REED BUILDS A LIFE RAFT", "life_raft", "1 3"),
            ("Doom gathered fragments from the realities that had already been destroyed.", "DOOM KEEPS THE PIECES", "collapse", "2"),
            ("He joined those pieces into one planet. He called it Battleworld.", "BROKEN WORLDS → BATTLEWORLD", "battleworld", "2"),
            ("The people living there answered to Doom. To them, he was the god who made their world.", "THE GOD OF BATTLEWORLD", "portrait", "2 4"),
            ("Then the raft survivors arrived. Some still remembered the worlds that had existed before.", "THE SURVIVORS REMEMBER", "memory", "6 13"),
            ("Doom could tell his subjects their world began with him. He couldn't tell that story to the people who'd seen what came before.", "SOMEONE KNEW THE TRUTH", "control", "4 13"),
            ("Watch part two next. We’re going beneath Doom’s castle to find the man who kept him in power.", "PART 2 · THE MAN UNDER THE CASTLE", "hidden_power", "5 7"),
        ),
    ),
    (
        "The Hamburger That Earned Spider-Man a Favor",
        (
            ("A hamburger earned Spider-Man a favor from Doom's power source. Doom's Broken Worlds, part two.", "DOOM'S BROKEN WORLDS · PART 2", "meal_detail", "5 8"),
            ("Miles Morales is Spider-Man. He escaped his dying universe on a life raft.", "MILES MORALES", "portrait", "6"),
            ("The survivors looked for the source of Doom's power and found someone buried beneath his castle.", "UNDER DOOM'S CASTLE", "hidden_power", "5 7"),
            ("Molecule Man had the power to rebuild worlds. What he wanted from Miles was something to eat.", "MOLECULE MAN WAS HUNGRY", "source_closeup", "5 8 11"),
            ("Miles reached into his pocket and gave him a hamburger.", "ONE HAMBURGER", "meal", "8"),
            ("Miles had already lost his mother. The hamburger was just something he could share with a stranger.", "MILES HAD LOST HIS MOTHER", "absence", "8 12"),
            ("The man who kept Doom on his throne remembered the kid who gave him lunch.", "MOLECULE MAN REMEMBERED", "meal_detail", "5 8 12"),
            ("Watch part three for the fall of Doom and how that favor came back to Miles.", "PART 3 · THE FAVOR COMES BACK", "duel", "10 12"),
        ),
    ),
    (
        "The Admission That Cost Doom His World",
        (
            ("One admission cost Doom his godhood. Doom's Broken Worlds, part three.", "DOOM'S BROKEN WORLDS · PART 3", "consequence", "9 10"),
            ("Reed Richards confronted Doom about what he'd done with all that power.", "REED CONFRONTS DOOM", "duel", "9"),
            ("Doom finally admitted that Reed would have done a better job saving reality.", "DOOM ADMITS IT", "throne", "9"),
            ("Molecule Man took the power away from Doom and passed it to Reed.", "DOOM → REED", "confrontation", "10"),
            ("Reed and his family helped bring back separate realities. Battleworld had never been their only option.", "WORLDS REBUILT", "rebuilding", "2 11"),
            ("Molecule Man still remembered the hamburger Miles gave him.", "THE HAMBURGER MATTERED", "meal_detail", "8 12"),
            ("When Miles Morales found himself in the rebuilt world, his mother was alive.", "MILES GETS HIS MOTHER BACK", "restoration", "12"),
            ("That's the end of Doom's Broken Worlds. Follow for the next comic story.", "DOOM'S BROKEN WORLDS · FINALE", "consequence", ""),
        ),
    ),
)

MOVIE = (
    ("Robert Downey Junior is playing Doctor Doom. Does that make him Tony Stark?", "SAME ACTOR. IS IT TONY?", "media", "1 2"),
    ("Disney confirmed Downey as Doom. The Tony Stark connection is still a theory.", "DOWNEY IS PLAYING DOOM", "media", "1 2"),
    ("Doctor Doom rules a country of his own. It's called Latveria.", "LATVERIA · THE COUNTRY HE RULES", "media", "4"),
    ("What makes him dangerous is that he's mastered both sorcery and technology.", "SORCERY + TECHNOLOGY", "powers", "4"),
    ("If you want to meet the team tied to Doom's history, watch The Fantastic Four: First Steps.", "THE FANTASTIC FOUR: FIRST STEPS", "media", "5 6"),
    ("It introduces Reed Richards and his team. You can still go into Doomsday without watching it.", "OPTIONAL VIEWING", "ticket", "5 6"),
    ("If you're picking just one movie for context on the team, that's the one I'd pick.", "ONE MOVIE FOR CONTEXT", "ensemble", "6"),
)

COMMONS = "https://commons.wikimedia.org/wiki/File:"
DOOM = COMMONS + "Universal_Studios_Florida_-_Doctor_Doom_cosplay.jpg"
MILES = COMMONS + "WonderCon_2018_-_Miles_Morales_Cosplayer.jpg"
IRON = COMMONS + "Iron_Man_Mark_I.jpg"
CC = "https://creativecommons.org/"
SOURCES = {
    "doom-cutout.png": (DOOM, CC + "licenses/by-sa/2.0/", "Remy Sharp. Background masked."),
    "miles-cutout.png": (MILES, CC + "licenses/by/2.0/", "pinguino k. Background masked."),
    "miles-theater.png": (MILES, CC + "licenses/by/2.0/", "pinguino k. Masked and cropped."),
    "iron-cutout.png": (IRON, CC + "licenses/by-sa/4.0/", "Fred Cherrygarden. Background masked."),
    "iron.jpg": (IRON, CC + "licenses/by-sa/4.0/", "Fred Cherrygarden. Cropped to frame by the editor."),
    "ruins.jpg": (COMMONS + "Ruined_arches._(17171050176).jpg", CC + "publicdomain/zero/1.0/", "Archive ruins photograph. Illustrative."),
    "cargo.jpg": (COMMONS + "MSC_IRINA_Trivandrum_Port.jpg", CC + "publicdomain/zero/1.0/", "Archive cargo photograph at Trivandrum Port. Illustrative."),
    "india.png": (COMMONS + "Flag_of_India.svg", "Public-domain flag design. See file page.", "Flag of India."),
    "nz.png": (COMMONS + "Flag_of_New_Zealand.svg", "Public-domain flag design. See file page.", "Flag of New Zealand."),
    "film-doom.jpg": ("https://www.disneyplus.com/explore/articles/avengers-doomsday", "No reuse license verified. Local review only.", "© Marvel Studios / Disney. Doomsday publicity still."),
    "film-ff.jpg": ("https://www.disneyplus.com/browse/entity-2142a7a9-4c49-438d-a492-296c4e08b714", "No reuse license verified. Local review only.", "© Marvel Studios / Disney. The Fantastic Four: First Steps key art."),
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def script(title, rows, description, *, hosts=False, payoff=-1):
    units = [{
        "id": f"u{index + 1}", "speaker": "Host" if hosts and index in (0, len(rows)-1) else "Narrator",
        "text": line, "kind": "transition" if not claims or (hosts and index == len(rows)-1) else "fact",
        "claim_ids": ["c"+claim for claim in claims.split()], "onscreen": label,
        "visual_kind": "image", "visual_query": label,
    } for index, (line, label, _, claims) in enumerate(rows)]
    return {
        "version": 1, "title": title, "description": description, "format": "lesson", "fiction": False,
        "hook": units[0]["text"], "payoff": units[payoff]["text"], "units": units,
        "edit": {"effect": "none", "payoff_unit_id": units[payoff]["id"], "cta": False},
    }


def item(name, playbook, channel, data, brief, music):
    return {"id": name, "kind": "playbook", "playbook": playbook, "channel": channel, "topic": data["title"],
            "request": {"script": data, "brief": brief, "motion_graphics": True, "test_only": True,
                        "fiction": False, "auto_publish": False, "hook_options": False, "editorial_review": "off",
                        "visual_review": "off", "bottom_kind": "none", "require_music": True, "music_id": music}}


def build(ws, directory, plan_dir, output):
    missing = [name for name in SOURCES if not (directory / name).is_file()]
    if missing:
        raise ValueError("Missing local source files: " + ", ".join(missing))
    assets = {}
    for name, (url, license, credit) in SOURCES.items():
        stock = name not in ("film-doom.jpg", "film-ff.jpg")
        record = register_asset(ws, directory / name, "licensed_stock" if stock else "test",
                                {"url": url, "license": license, "checked_at": now()}, commercial=stock,
                                editing=stock, attribution=credit, test_only=True)
        assets[name] = record["id"]

    def panel(name, box, fit="contain"):
        return {"asset_id": assets[name], "box": box, "fit": fit}

    def cinema(*names):
        return {"setting": "cinema", "cast": [assets[name] for name in names]}

    def previous(batch, item_id, genre):
        path = output / batch / "batch.json"
        if path.is_file():
            prior = next((row["job_id"] for row in load(path)["items"] if row["id"] == item_id and row.get("job_id")), None)
            if prior:
                job = ws.get(prior)
                return prior, job["request"]["music_id"]
        return None, select_genre_music(ws, genre, selection_key=item_id)["id"]

    brief = load(ROOT / "research/content-lore/SECRET_WARS_2015_BRIEF.json")
    brief["editorial_verified"] = True
    brief["notes"] += " Local script checked against the listed canon claims and publisher recaps."
    comic = []
    for number, (title, rows) in enumerate(SERIES, 1):
        name = f"part-{number}"
        data = script(title, rows, f"Doom's Broken Worlds, part {number}. Original spoiler recap of Marvel Comics’ Secret Wars (2015), by Jonathan Hickman and Esad Ribić. The series covers the comic continuity.", hosts=True, payoff=-2)
        ancestor, music = previous("doom-secret-wars-2015-v2", name, "mystery")
        entry = item(name, "comic_lore", "entertainment", data, brief, music)
        request = entry["request"]
        request.update(
            series={"id": "doom-secret-wars-2015", "title": "Doom's Broken Worlds", "canon": "Marvel Comics Secret Wars (2015)", "part": number, "total": 3, "next_part": number + 1 if number < 3 else None},
            source_review={"reviewer": "Codex", "supported": True, "brief_digest": digest(brief), "script_digest": digest(data), "limitations": "Publisher recaps and reading list. Full issues were unavailable."},
            lore_scenes={f"u{i}": row[2] for i, row in enumerate(rows, 1)},
            source_delivery={"speed": 1.11, "pause_after": .07, "pauses_after": {"u6": .2, "u7": .18}, "linked_phrases": ["Miles Morales", "Reed Richards", "Molecule Man", "Doctor Doom"]},
            reaction_set=cinema("doom-cutout.png", "miles-theater.png", "iron-cutout.png"),
            source_panels=(
                {"u1": [panel("doom-cutout.png", [232, 260, 600, 825])],
                 "u4": [panel("ruins.jpg", [46, 710, 674, 865], "cover")],
                 "u5": [panel("doom-cutout.png", [168, 223, 552, 861])]} if number == 1 else
                {"u2": [panel("miles-cutout.png", [44, 316, 675, 781])]} if number == 2 else
                {"u2": [panel("doom-cutout.png", [373, 270, 659, 821])],
                 "u7": [panel("miles-theater.png", [75, 300, 280, 690])]}
            ),
        )
        if ancestor:
            request["prototype_revision_of"] = ancestor
        comic.append(entry)

    title = "What to Watch Before Avengers: Doomsday"
    data = script(title, MOVIE, "Disney confirmed Robert Downey Jr. as Doctor Doom. Here is what we know about the character and which Fantastic Four movie to watch for context.")
    ancestor, music = previous("source-short-pilots-20261106-v3", "doomsday-context", "cinematic")
    movie = item("doomsday-context", "movie_brief", "entertainment", data,
                 load(ROOT / "examples/movie-content/doomsday-actor-character.brief.json"), music)
    movie["request"].update(
        brief_motifs={f"u{i}": row[2] for i, row in enumerate(MOVIE, 1)},
        source_delivery={"speed": 1.08, "pause_after": .08, "linked_phrases": ["The Fantastic Four: First Steps", "Tony Stark", "Doctor Doom", "Reed Richards"]},
        reaction_set=cinema("iron-cutout.png", "doom-cutout.png", "miles-theater.png"),
        source_panels={"u1": [panel("iron.jpg", [47, 230, 673, 843], "cover")],
                       "u2": [panel("film-doom.jpg", [47, 239, 673, 830], "contain")],
                       "u3": [panel("doom-cutout.png", [154, 215, 566, 867])],
                       "u5": [panel("film-ff.jpg", [48, 225, 672, 852])]},
    )
    if ancestor:
        movie["request"]["prototype_revision_of"] = ancestor

    data = load(ROOT / "examples/current-affairs/india-nz-fta.script.json")
    music = load(ws.root / "curated-music-library.json")["tracks"]["mixkit-565"]["asset_id"]
    ancestor, _ = previous("source-short-pilots-20261106-v3", "india-nz-trade", "learning")
    news = item("india-nz-trade", "current_affairs", "education", data,
                load(ROOT / "examples/current-affairs/india-nz-fta.brief.json"), music)
    flags = [panel("india.png", [58, 460, 238, 634]), panel("nz.png", [482, 460, 662, 634])]
    news["request"].update(
        brief_motifs=dict(zip((u["id"] for u in data["units"]), ("routes", "date", "route", "route", "filter", "origin", "costs", "routes"))),
        source_delivery={"speed": 1.05, "pause_after": .09, "linked_phrases": ["New Zealand"]},
        source_cues={"u2": "transition", "u3": "reveal", "u4": "impact", "u6": "transition"},
        source_panels={"u1": [panel("cargo.jpg", [48, 215, 672, 439], "cover"), *flags],
                       "u3": flags, "u4": [panel("nz.png", flags[0]["box"]), panel("india.png", flags[1]["box"])],
                       "u8": flags},
    )
    if ancestor:
        news["request"]["prototype_revision_of"] = ancestor

    for entry in [*comic, movie, news]:
        request = entry["request"]
        validate_playbook_script(script_contract(request["script"], request["brief"], "lesson"), entry["playbook"], request)
    for name, items in (("doom-broken-worlds-photo-20261106", comic), ("movie-news-recut-20261106", [movie, news])):
        path = plan_dir / f"{name}.json"
        if not path.exists():
            write_json(path, {"version": 1, "id": name, "created_at": now(), "output_root": str(output),
                              "note": "Local review only. Supplied writing, traced photos and code-drawn sets.", "items": items})
        print(path)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("assets", type=Path, help="Folder with the local files listed in SOURCES")
    args = parser.parse_args()
    build(Workspace(ROOT / "data/pipeline"), args.assets.resolve(), ROOT / "Resources/Plans", ROOT / "Resources/Productions")


if __name__ == "__main__":
    main()
