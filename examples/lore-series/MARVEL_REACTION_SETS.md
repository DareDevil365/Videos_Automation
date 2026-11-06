# Reusable Marvel reaction sets

The story plays in the upper panel, with dialogue captions between that panel and the reaction strip. A set describes the location. Its cast and props are separately registered transparent PNGs. The same Strange cutout can appear in his own sanctum or in an ensemble about a Doomsday theory. The cameo is a framing choice. The script and source brief determine what the Short can claim.

| Preset | Setting | First local cast and props |
| --- | --- | --- |
| `crossover-theater` | `cinema` | Doom, Miles and Iron Man in theater seats with animated popcorn |
| `iron-man-workshop` | `workshop` | Seated Tony on the leather sofa, lit armor bays, a flame-painted Ford roadster and an Audi R8 |
| `spider-man-city` | `city` | Miles on a swinging web above the skyline |
| `captain-america-and-bucky` | `living_room` | Cap and Bucky with the shield in a living room |
| `doctor-strange-sanctum` | `sanctum` | Strange framed by a circular magic motif |

## Use a set in a Short

Add this field to a normal `comic_lore` or `movie_brief` request after installing the local library. Supply the topic, source brief and other usual production fields as well.

```json
{
  "playbook": "movie_brief",
  "test_only": true,
  "reaction_preset": "doctor-strange-sanctum"
}
```

To mix the cast, use `reaction_set` in place of `reaction_preset`. Read the registered IDs from `library.json`. The cast is laid out left to right, with up to three characters and two optional background props.

```json
{
  "setting": "cinema",
  "cast": ["<doom asset ID>", "<strange asset ID>"],
  "props": []
}
```

Choose the set around the subject of the episode. Use the theater for teams and crossovers, the workshop for armor, the city for Spider-Man, and home or sanctum settings for smaller stories. Keep specific movie theories in the script clearly framed as theories. The set renderer can swap in approved Wanda, MJ, Ned, pets or other cutouts when they are added to the local registry. The initial pack does not include those characters, and it uses simple motion on still cutouts.

## Build or inspect the local library

The [library tool](../../tools/create_marvel_set_library.py) lists the filenames and original photo credits. Prepare transparent cutouts from your sourced images and put them in one folder. For the workshop, prepare a sofa cutout and a separate room backdrop. The [reference composition tool](../../tools/compose_workshop_reference.py) reproduces the demonstrated crop from the two supplied reference screenshots and the two car photographs. The generic workshop recipe accepts a different registered backdrop and one seated cutout.

```powershell
.venv/Scripts/python.exe tools/create_marvel_set_library.py PATH_TO_CUTOUTS Resources/Productions/marvel-set-library-v2
```

The output contains a contact sheet, five silent 720 × 288 motion previews, the photo layers and `library.json`. A second JSON file in the local pipeline workspace installs the names for future jobs. When a video uses a set, the editor renders it on the episode's timeline, including across scene boundaries. The workshop layers move at slightly different rates to give the room depth. The short MP4 previews are for reviewing or reusing the strip in an external editor.

The supplied cosplay images show recognizable costumes. Photo credits and license links are carried in the library, and the installed assets are marked for local review. If you use a separately cleared asset, register it with its own usage evidence before building a publication-ready set.
