"""Shared word→vowel and word→IPA maps for the phonetics-video pipeline.

Extend these dicts when a practice video introduces new words. WORD_VOWEL drives which
Hillenbrand target band/ellipse a word is compared against; IPA_OVERRIDES beats
eng_to_ipa (which mangles rare words like "med"/"rad" and strips nothing else).
"""

WORD_VOWEL = {
    "bad": "æ", "sad": "æ", "mad": "æ", "hat": "æ", "had": "æ", "rad": "æ",
    "head": "ɛ", "med": "ɛ", "said": "ɛ", "red": "ɛ", "bed": "ɛ",
    "bin": "ɪ", "chip": "ɪ", "his": "ɪ", "it": "ɪ", "sit": "ɪ",
    "shit": "ɪ", "bitch": "ɪ",
    "bean": "i", "cheap": "i", "he's": "i", "eat": "i", "seat": "i",
    "sheet": "i", "beach": "i",
    "culture": "ʌ", "cultural": "ʌ", "cult": "ʌ", "cultivate": "ʌ",
    "custom": "ʌ", "customer": "ʌ", "customary": "ʌ",
    "cup": "ʌ", "cut": "ʌ", "butt": "ʌ", "bus": "ʌ", "fun": "ʌ", "run": "ʌ",
    "jump": "ʌ", "lunch": "ʌ", "much": "ʌ", "such": "ʌ",
    "number": "ʌ", "under": "ʌ", "hundred": "ʌ", "summer": "ʌ",
    "sunday": "ʌ", "subject": "ʌ", "sudden": "ʌ", "supper": "ʌ",
    "no": "oʊ",  # graded like any take; Dennis's [no] measures ~2 SD off /oʊ/
}

# stressed /ʌ/ immediately before dark (velarized) /l/: coarticulation drags F2 down
# ~400 Hz, so the Hillenbrand /hVd/ comparison is unfair — plot them, don't grade them
DARK_L = {"culture", "cultural", "cult", "cultivate"}

IPA_OVERRIDES = {
    "bad": "bæd", "sad": "sæd", "mad": "mæd", "hat": "hæt", "had": "hæd", "rad": "ræd",
    "head": "hɛd", "med": "mɛd", "said": "sɛd", "red": "rɛd", "bed": "bɛd",
    "bin": "bɪn", "chip": "tʃɪp", "his": "hɪz", "it": "ɪt", "sit": "sɪt",
    "shit": "ʃɪt", "bitch": "bɪtʃ",
    "bean": "biːn", "cheap": "tʃiːp", "he's": "hiːz", "eat": "iːt", "seat": "siːt",
    "sheet": "ʃiːt", "beach": "biːtʃ",
    "no": "no",  # Dennis's production is a monophthong /no/, not GA /noʊ/
    "culture": "ˈkʌltʃɚ", "cultural": "ˈkʌltʃərəl", "cult": "kʌlt",
    "cultivate": "ˈkʌltɪveɪt", "custom": "ˈkʌstəm", "customer": "ˈkʌstəmɚ",
    "customary": "ˈkʌstəmɛri",
    "cup": "kʌp", "cut": "kʌt", "butt": "bʌt", "bus": "bʌs", "fun": "fʌn",
    "run": "rʌn", "jump": "dʒʌmp", "lunch": "lʌntʃ", "much": "mʌtʃ", "such": "sʌtʃ",
    "number": "ˈnʌmbɚ", "under": "ˈʌndɚ", "hundred": "ˈhʌndrəd",
    "summer": "ˈsʌmɚ", "sunday": "ˈsʌndeɪ", "subject": "ˈsʌbdʒɪkt",
    "sudden": "ˈsʌdən", "supper": "ˈsʌpɚ",
}

# per-(word, variant) IPA: UK = non-rhotic ending /ə/, US = r-colored /ɚ/.
# A take's "variant" comes from final_takes.json and is VERIFIED acoustically
# (ending F3 ≈ 1700 Hz → r-colored; ≈ 2500 Hz → plain schwa) before labeling.
VARIANT_IPA = {
    # "XX" = deliberate mispronunciation gag take: the IPA of what was actually
    # said (here: "culture" with a /uː/ where the /ʌ/ belongs)
    ("culture", "XX"): "ˈkuːltʃə",
    ("culture", "UK"): "ˈkʌltʃə", ("culture", "US"): "ˈkʌltʃɚ",
    ("customer", "UK"): "ˈkʌstəmə", ("customer", "US"): "ˈkʌstəmɚ",
    ("customary", "UK"): "ˈkʌstəməri", ("customary", "US"): "ˈkʌstəmɛri",
    ("number", "UK"): "ˈnʌmbə", ("number", "US"): "ˈnʌmbɚ",
    ("under", "UK"): "ˈʌndə", ("under", "US"): "ˈʌndɚ",
    ("summer", "UK"): "ˈsʌmə", ("summer", "US"): "ˈsʌmɚ",
    ("supper", "UK"): "ˈsʌpə", ("supper", "US"): "ˈsʌpɚ",
}

# On-screen spelling when it should differ from the word key — e.g. swear words the
# speaker self-censors in the audio get star-censored text to match the joke (and to
# be safe for Instagram); the IPA stays uncensored, phonetics is the point.
DISPLAY_WORD = {
    "shit": "sh*t",
    "bitch": "b*tch",
    "sunday": "Sunday",
}

# Twemoji codepoint (file tools/assets/emoji/<code>.png) illustrating each word's
# MEANING for non-English-speaking viewers. Pick concrete, unambiguous images; for
# abstract words (had) settle for the closest gesture. Download new ones from
# https://cdn.jsdelivr.net/gh/jdecked/twemoji@15.1.0/assets/72x72/<code>.png
WORD_EMOJI = {
    # --- RP vowel-inventory reel (2026-09-04): p_t / b_d / h_d minimal-pair frames
    "pet": "1f436",     # dog face (a pet)
    "pat": "270b",      # raised hand (a pat)
    "part": "1f9e9",    # puzzle piece (a part)
    "pot": "1f372",     # pot of food
    "putt": "26f3",     # flag in hole (golf putt)
    "pert": "1f60f",    # smirking face (pert = cheeky, lively)
    "port": "2693",     # anchor (harbour)
    "pull": "1f9f2",    # magnet (pulls)
    "pool": "1f3ca",    # swimmer
    "bod": "1f4aa",     # flexed biceps (body)
    "but": "1f6d1",     # stop sign (objection)
    "bird": "1f426",    # bird
    "bored": "1f971",   # yawning face
    "book": "1f4d6",    # open book
    "boot": "1f97e",    # hiking boot
    "hot": "1f525",     # fire
    "hard": "1faa8",    # rock
    "hut": "1f6d6",     # hut
    "hurt": "1f915",    # face with head-bandage
    "hoard": "1f4b0",   # money bag
    "hood": "1f9e5",    # coat with a hood
    "who'd": "2753",    # question mark (who would)
    "mad": "1f620",   # angry face
    "med": "1f48a",   # pill (medicine)
    "hat": "1f3a9",   # top hat
    "head": "1f464",  # bust silhouette
    "sad": "1f622",   # crying face
    "said": "1f4ac",  # speech balloon
    "rad": "1f60e",   # sunglasses face (cool)
    "red": "1f7e5",   # red square
    "bad": "1f44e",   # thumbs down
    "bed": "1f6cf",   # bed
    "hat": "1f3a9",   # top hat
    "bin": "1f5d1",   # wastebasket
    "bean": "1fad8",  # beans
    "chip": "1f35f",  # fries
    "cheap": "1f3f7", # price tag
    "his": "1f468",   # man (possessive of him)
    "he's": "1f468",  # man (he is)
    "it": "1f449",    # pointing at a thing
    "eat": "1f37d",   # fork and knife with plate
    "sit": "1f9d8",   # person sitting cross-legged
    "seat": "1fa91",  # chair
    "shit": "1f4a9",  # pile of poo
    "sheet": "1f4c4", # page
    "bitch": "1f92c", # face with symbols over mouth (swear word)
    "beach": "1f3d6", # beach with umbrella
    "no": "1f645",       # person gesturing NO
    "culture": "1f3ad",  # performing arts masks
    "cultural": "1f3db", # classical building
    "cult": "1f56f",     # candle (ritual)
    "cultivate": "1f331",# seedling
    "custom": "1f4dc",   # scroll (tradition)
    "customer": "1f6cd", # shopping bags
    "customary": "1f501",# repeat (habitual practice)
    "cup": "2615",       # hot beverage
    "cut": "2702",       # scissors
    "butt": "1f351",     # peach
    "bus": "1f68c",      # bus
    "fun": "1f389",      # party popper
    "run": "1f3c3",      # person running
    "jump": "1f998",     # kangaroo
    "lunch": "1f371",    # bento box
    "much": "2795",      # plus sign (a lot)
    "such": "2728",      # sparkles
    "number": "1f522",   # 1234 input
    "under": "2b07",     # down arrow
    "hundred": "1f4af",  # hundred points
    "summer": "2600",    # sun
    "sunday": "1f4c5",   # calendar
    "subject": "1f4da",  # books
    "sudden": "26a1",    # lightning
    "supper": "1f958",   # shallow pan of food
}

# A SECOND, different picture for the other side of the word. Two complementary images
# read faster than one repeated twice, and they disambiguate homophone-ish words for
# viewers who do not read English (e.g. "hoard" = money bag + gem, not "horde").
WORD_EMOJI_ALT = {
    "pet": "1f431",    # cat
    "pat": "1f44f",    # clapping hands
    "part": "2702",    # scissors (to part)
    "pot": "1fab4",    # potted plant
    "putt": "1f3af",   # direct hit
    "pert": "2728",    # sparkles (lively)
    "port": "1f6a2",   # ship
    "pull": "1faa2",   # knot (pulled tight)
    "pool": "1f30a",   # wave
    "bed": "1f634",    # sleeping face
    "bad": "1f480",    # skull
    "bod": "1f9b4",    # bone
    "but": "1f645",    # person gesturing no
    "bird": "1fab6",   # feather
    "bored": "1f610",  # neutral face
    "book": "1f4da",   # stack of books
    "boot": "1f463",   # footprints
    "head": "1f9e0",   # brain
    "hat": "1f452",    # woman's hat
    "hot": "1f975",    # hot face
    "hard": "1f9f1",   # brick
    "hut": "1f3e0",    # house
    "hurt": "1fa79",   # adhesive bandage
    "hoard": "1f48e",  # gem
    "hood": "1f9e2",   # billed cap
    "who'd": "1f914",  # thinking face
}


# variant → flag / marker PNG (same Twemoji directory), shown left of the word
VARIANT_EMOJI = {
    "UK": "1f1ec-1f1e7",  # British ending: no R, plain /ə/
    "US": "1f1fa-1f1f8",  # American ending: r-colored /ɚ/
    "XX": "274c",         # mispronounced gag take
}

# Hillenbrand et al. (1995) men, steady state: (f1_mean, f1_sd, f2_mean, f2_sd)
# from references/hillenbrand1995-means.csv — extend when new target vowels appear
TARGETS_MEN = {
    "æ": (591, 42, 1930, 133),
    "ɛ": (588, 41, 1803, 117),
    "ɪ": (429, 31, 2034, 122),
    "i": (343, 28, 2323, 136),
    "ʌ": (621, 30, 1181, 87),
    "oʊ": (498, 43, 910, 98),
    "eɪ": (476, 41, 2090, 140),
}

# The R-ending test: F3 is THE acoustic cue for r-coloring. Men's steady-state F3,
# computed from references/hillenbrand-vowdata.dat (col 6, zeros excluded):
#   /ɝ/ ("heard"): 1711 ± 108 Hz → an American /ɚ/ ending should sit here
#   /ʌ/ ("hud"):   2548 ± 142 Hz → plain vowels sit here, so a British /ə/
#                                  ending should keep its F3 up there
F3_RHOTIC = (1711, 108)
F3_PLAIN = (2548, 142)
RHOTIC_F3_MAX = 2000  # ending F3 below this counts as r-colored (men)

# letter grade from Mahalanobis distance d (in reference SDs): the bands double as
# the academic footnote — A+ within 1 SD of the Hillenbrand mean, F beyond 4 SD
GRADE_BANDS = [(1.0, "A+"), (1.75, "A"), (2.5, "B"), (3.25, "C"), (4.0, "D")]

def grade_of(d):
    return next((g for lim, g in GRADE_BANDS if d <= lim), "F")

def vowel_distance(word, f1, f2):
    """2-D Mahalanobis-style distance (SD units) from the word's vowel target."""
    return target_distance(WORD_VOWEL[word], f1, f2)

def target_distance(ipa, f1, f2):
    m1, s1, m2, s2 = TARGETS_MEN[ipa]
    return (((f1 - m1) / s1) ** 2 + ((f2 - m2) / s2) ** 2) ** 0.5

def dark_l_distance(word, f1):
    """Grade distance for a stressed vowel before dark /l/: F1 only (the dark /l/
    coarticulates F2 away, so the 2-D comparison is unfair), with the tolerance
    widened x2 for the residual F1 coarticulation uncertainty."""
    m1, s1 = TARGETS_MEN[WORD_VOWEL[word]][:2]
    return abs(f1 - m1) / (2 * s1)

def ending_distance(f3_end, variant):
    """1-D distance of an ending's F3 from its variant's target (US /ɚ/, UK /ə/)."""
    mean, sd = F3_RHOTIC if variant == "US" else F3_PLAIN
    return abs(f3_end - mean) / sd

def match_percent(word, f1, f2):
    """How close a token is to the textbook (Hillenbrand men) mean for its vowel.

    Mahalanobis-style distance d in SD units over (F1, F2), mapped through
    exp(-d^2/8)*100 — i.e. a Gaussian with a 2-SD tolerance instead of 1 SD.
    100 = dead on the mean; ~60% at 2 SD; ~10% at 4+ SD. The widened tolerance is
    deliberate: the strict population percentile (exp(-d^2/2)) flattens everything
    past 2 SD to ~0%, which erases feedback ordering — and Hillenbrand's Northern
    Cities /ae/ (raised, F2 1930) sits systematically off modern General American,
    so cross-dialect distances of 2-3 SD are expected even for decent productions.
    """
    import math
    return round(100 * math.exp(-vowel_distance(word, f1, f2) ** 2 / 8))

def ipa_of(word, variant=None):
    if variant and (word, variant) in VARIANT_IPA:
        return VARIANT_IPA[(word, variant)]
    if word in IPA_OVERRIDES:
        return IPA_OVERRIDES[word]
    try:
        import eng_to_ipa
        return eng_to_ipa.convert(word).strip("ˈˌ")
    except Exception:
        return word
