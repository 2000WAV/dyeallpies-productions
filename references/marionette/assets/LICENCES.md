# Assets — item 6 (neon rendering and assets)

**Nothing was downloaded into this folder.** The marionette is built entirely from MuJoCo
capsules and ellipsoids per the project brief, so an external mesh asset is optional, not
required. Sketchfab candidates were identified and their licences checked directly (not from
search-result summaries), but the actual model-file download requires an authenticated Sketchfab
session — confirmed by an anonymous request to the download API, which returned
`{"detail":"Authentication credentials were not provided."}` — and this research task is
scoped to literature/asset *research*, not to setting up new logins or credentials. The
candidates below are listed for Dennis to fetch by hand through a browser if an external mesh is
ever wanted.

| file | source url | author | licence | notes |
|---|---|---|---|---|
| (not downloaded) | https://sketchfab.com/3d-models/mannequincc0-db6ac59387c245d8bae086ce1ee17fec | WuYin (@WuYinCC03D) | **CC0** — confirmed on-page: "CC0, free to use, no rights reserved" | 5.3k triangles / 2.7k vertices; best candidate if an external mesh is wanted; page mirrored at `../papers/sketchfab-mannequincc0.html` |
| (not downloaded) | https://sketchfab.com/3d-models/marionette-2af427c39af44e80a5e4e8ad049e8288 | animator12 | **CC-BY (CC Attribution)** — confirmed on-page | usable but requires crediting the author if used; page mirrored at `../papers/sketchfab-marionette-animator12.html` |
| — excluded — | https://sketchfab.com/3d-models/artists-mannequin-113a7b64b1fe4976a9f5dbd1a26d9dd6 | timcoleman | `"license": null` in the page's own embedded JSON — unlicensed / possibly a paid store item | do not use; page mirrored at `../papers/sketchfab-artists-mannequin-timcoleman.html` |

Other sources checked with no usable result:

- **Poly Haven** (`polyhaven.com/models`) — browsed; its model library is HDRIs/textures/props/
  photogrammetry scans, no articulated mannequin or marionette figure found.
- **Wikimedia Commons** — `Commons:3D models` confirms `.stl` uploads exist and are searchable,
  but no specific artist's-mannequin or marionette STL was located.
- **Smithsonian Open Access** and **Blend Swap** — not reached within this pass; not searched due
  to the puppet-is-primitive-built / asset-optional note in the brief taking priority once a
  genuine CC0 candidate (WuYin's mannequin) was already confirmed on Sketchfab.

## Assets — item 10 (rendering routes and mannequin assets)

Four assets were actually downloaded this pass (all under the 30 MB/file limit, all verified by
size against the source's own reported size and by file-type sniffing after download). Full
search notes, additional non-downloaded candidates, and every URL are in
`../downloads-10.md`; the summary here is licence text only.

| folder | file(s) | source url | author | licence | size |
|---|---|---|---|---|---|
| `mannequiny-gdquest/` | `glb-mannequiny-0.4.0.zip` (452,803 B), extracted `mannequiny-0.4.0.glb` (1,560,072 B) | https://opengameart.org/content/mannequiny-the-open-3d-mannequin (OpenGameArt mirror of https://github.com/gdquest-demos/godot-3d-mannequin) | GDQuest, Luciano Muñoz, and contributors | **CC-BY 4.0** — "Mannequiny by GDQuest, Luciano Muñoz, and contributors licensed CC-BY 4.0" (GitHub release notes, quoted on the OpenGameArt page and in a maintainer comment resolving a licence dispute in the OpenGameArt comment thread). **Credit GDQuest and Luciano Muñoz if this asset is used.** Note: the project's code (Godot demo) is separately MIT-licensed; only the 3D model/animation is CC-BY and only the model was downloaded here. | 1.6 MB uncompressed |
| `lacquered_cherry_wood_1k/` | 4 JPGs (diff/nor_gl/rough/ao, 1k) | https://polyhaven.com/a/lacquered_cherry_wood | Poly Haven (contributor(s) credited on-site) | **CC0** (Poly Haven's site-wide licence for all assets) | 1.6 MB total |
| `paintedwood003_1k/` | `PaintedWood003_1K-JPG.zip` | https://ambientcg.com/view?id=PaintedWood003 | ambientCG | **CC0 / Public Domain** (page confirms both terms) | 7.9 MB |
| `plastic001_1k/` | `Plastic001_1K-JPG.zip` | https://ambientcg.com/view?id=Plastic001 | ambientCG | **CC0 / Public Domain** | 6.6 MB |

Sketchfab CC0/CC-BY ball-jointed-doll candidates (ChamberSu's two basemeshes, Drothari's rigged
BJD, rjducats' low-poly BJD) were identified and their licences read directly from each page's
embedded HTML (all four are **CC-BY**, not CC0 — the "cc0" string that also appears on those pages
is a shared CSS class name in Sketchfab's licence-icon markup, not the assigned licence; the
licence text itself reads "Creative Commons Attribution" on every one of the four) — see
`../downloads-10.md` for each URL. None were downloaded: Sketchfab's model-file download endpoint
requires an authenticated session (same finding as item 6), and rjducats' page states an explicit
poly budget (3,000 tris) while the other three render their triangle/vertex counts client-side in
JavaScript, so those numbers are **NOT FOUND** in the saved static HTML.
