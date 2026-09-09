# Background plates and their required credit lines

## First set (2026-09-05) — `jungle_plate.jpg`

A 9:16 crop of "Palawan, Tropical jungle rainforest.jpg" by Vyacheslav Argenberg,
CC BY 4.0, via Wikimedia Commons:
https://commons.wikimedia.org/wiki/File:Palawan,_Tropical_jungle_rainforest.jpg

Required credit line for the post: **"Background: Vyacheslav Argenberg / CC BY 4.0"**.

## Second set (2026-09-07) — `jungle_monkeys_plate.jpg`

The same rainforest canopy with four monkeys composited into it (built by
`pullup/work2/build_plate.py`; the cutouts were made with GrabCut). Three sources, so the
post needs all three credits:

| element | source | licence | credit needed |
|---|---|---|---|
| canopy | "Palawan, Tropical jungle rainforest.jpg", Vyacheslav Argenberg | CC BY 4.0 | yes |
| capuchin (used twice) | "A curious Capuchin monkey perched on a branch.jpg", Nasehi2277 | **CC0** | not required, given anyway |
| langur (used twice) | "Langur Monkey in tree Betla 2025.jpg", Dev0745 | CC BY 4.0 | yes |

Links:
- https://commons.wikimedia.org/wiki/File:Palawan,_Tropical_jungle_rainforest.jpg
- https://commons.wikimedia.org/wiki/File:A_curious_Capuchin_monkey_perched_on_a_branch.jpg
- https://commons.wikimedia.org/wiki/File:Langur_Monkey_in_tree_Betla_2025.jpg

Required credit line for the post:
**"Background: Vyacheslav Argenberg, Dev0745 / CC BY 4.0; capuchin by Nasehi2277 / CC0
(Wikimedia Commons)."**

Note on licences: everything here is CC BY or CC0 on purpose. ShareAlike images were
rejected during the search — a CC BY-SA element would push the whole Reel into
ShareAlike, which is not what we want for a post.

Files kept locally and gitignored (not mirrored publicly): `palawan_jungle_full.jpg`,
`monkey_capuchin.jpg`, `monkey_langur.jpg`, `monkey_macaque.png` (downloaded but unused;
it is a PD illustration and clashed with the photographic plate).

## Third set (2026-09-08) — `jungle3_plate.jpg`

Base: a 9:16 crop of "Mata Atlantica in the Reserva Kaetés" by Jens Lallensack, CC BY 4.0, darkened 20 %. Seven monkey cut-outs (rembg isnet, alpha matting) placed on its trunks and branches by `pullup/work3/build_plate3.py`. All CC BY or CC0; every credit below is required except the CC0 ones, which are given anyway.

| element | source file | author | licence | page |
|---|---|---|---|---|
| spider_monkey_04 | Central american spider monkey natural lodge caño negro 4.17.25 monkeys DSC 9577-topaz-rawdenoise.jpg | lwolfartist | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Central_american_spider_monkey_natural_lodge_caño_negro_4.17.25_monkeys_DSC_9577-topaz-rawdenoise.jpg |
| spider_monkey_09 | Central american spider monkey natural lodge caño negro 4.17.25 monkeys DSC 9525-topaz-rawdenoise.jpg | lwolfartist | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Central_american_spider_monkey_natural_lodge_caño_negro_4.17.25_monkeys_DSC_9525-topaz-rawdenoise.jpg |
| spider_monkey_10 | Central american spider monkey natural lodge caño negro 4.17.25 monkeys DSC 9470-topaz-rawdenoise.jpg | lwolfartist | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Central_american_spider_monkey_natural_lodge_caño_negro_4.17.25_monkeys_DSC_9470-topaz-rawdenoise.jpg |
| howler_monkey_02 | Black Howler Monkey - Flickr - GregTheBusker (2).jpg | Greg Schechter from San Francisco, USA | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Black_Howler_Monkey_-_Flickr_-_GregTheBusker_(2).jpg |
| capuchin_monkey_05 | Capuchin Monkey (8458171320).jpg | shankar s. from Dubai, united arab emirates | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Capuchin_Monkey_(8458171320).jpg |
| marmoset_00 | Callithrix jacchus in Parque Bondinho Pão de Açúcar, Rio de Janeiro.jpg | Wilfredor | CC0 | https://commons.wikimedia.org/wiki/File:Callithrix_jacchus_in_Parque_Bondinho_Pão_de_Açúcar,_Rio_de_Janeiro.jpg |
| golden_lion_tamarin_01 | Leontopithecus rosalia (43770458982).jpg | Tomasz Baranowski from Lelystad, Holland | CC BY 2.0 | https://commons.wikimedia.org/wiki/File:Leontopithecus_rosalia_(43770458982).jpg |
| mata_atlantica_00 | Mata Atlantica in the Reserva Kaetés.jpg | Jens Lallensack | CC BY 4.0 | https://commons.wikimedia.org/wiki/File:Mata_Atlantica_in_the_Reserva_Kaetés.jpg |

Required credit line for the post: **"Background: Jens Lallensack / CC BY 4.0 (Mata Atlântica); monkeys by lwolfartist, Greg Schechter, Tomasz Baranowski / CC BY 2.0 and Wilfredor / CC0, via Wikimedia Commons."**

Downloaded but unused this time (kept in `pullup/assets/commons/`, gitignored): the other spider monkey, howler, capuchin, squirrel monkey, lupuna and canopy files listed in `pullup/assets/commons/CREDITS.json`.
