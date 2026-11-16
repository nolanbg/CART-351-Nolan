import hashlib
import random
import re

# Rough lat/lon boxes: (lat_min, lat_max, lon_min, lon_max)
CITIES = [
    (40.7, -74.0), (34.1, -118.2), (41.9, -87.6), (29.8, -95.4),   # US
    (51.5, -0.1), (48.9, 2.4), (52.5, 13.4), (41.9, 12.5),         # Europe
    (28.6, 77.2), (19.1, 72.9), (23.8, 90.4),                      # South Asia
    (35.7, 139.7), (37.6, 127.0), (31.2, 121.5),                   # East Asia
    (-23.5, -46.6), (-34.6, -58.4), (4.7, -74.1),                  # South America
    (6.5, 3.4), (-1.3, 36.8), (30.0, 31.2),                        # Africa
    (-33.9, 151.2),                                                # Australia
]

def random_location(rng):
    lat, lon = rng.choice(CITIES)
    return round(lat + rng.uniform(-1.5, 1.5), 2), round(lon + rng.uniform(-1.5, 1.5), 2)

ADJECTIVES = ["Patriot", "Concerned", "Real", "Free", "Awake", "Honest", "Curious", "Furious", "Outraged", "Dogmatic", "Unhinged", "SuperSmart", "Humble"]
NOUNS = ["Eagle", "Mom", "Truth", "Voice", "Citizen", "Wolf", "Patriot", "Conspiracy", "Skeptic", "Thinker", "Guy", "Bigot", "OwnPoopEater", "LizardPerson", "Sheep",]

SYNONYMS = {
    # reporting verbs -> loaded verbs
    "said": "claimed",
    "says": "admits",
    "told": "warned",
    "stated": "confessed",
    "announced": "revealed",
    "reported": "exposed",
    "found": "uncovered",
    "showed": "proved",
    "suggests": "proves",
    "think": "know",
    "believe": "know",
    "thinks": "knows",

    # size / intensity
    "big": "massive",
    "large": "enormous",
    "small": "tiny",
    "many": "countless",
    "some": "thousands of",
    "most": "nearly all",
    "few": "almost no",
    "new": "shocking new",
    "old": "ancient",
    "fast": "lightning-fast",
    "huge": "unbelievable",

    # good / bad
    "bad": "disastrous",
    "good": "perfect",
    "wrong": "criminal",
    "problem": "crisis",
    "issue": "scandal",
    "mistake": "cover-up",
    "change": "takeover",
    "plan": "agenda",
    "idea": "scheme",
    "rule": "mandate",
    "law": "decree",
    "ban": "crackdown",
    "study": "leaked study",
    "report": "secret report",
    "test": "experiment",

    # people / institutions
    "government": "regime",
    "officials": "insiders",
    "scientists": "so-called experts",
    "experts": "paid experts",
    "doctors": "doctors (silenced)",
    "company": "corporation",
    "companies": "mega-corporations",
    "media": "mainstream media",
    "people": "citizens",
    "everyone": "everybody who's awake",
    "nobody": "not a single person",
    "they": "THEY",

    # everyday words
    "closing": "shutting down",
    "closed": "shut down",
    "open": "exposed",
    "start": "launch",
    "stop": "shut down",
    "end": "collapse",
    "ending": "collapsing",
    "early": "suddenly",
    "late": "way too late",
    "soon": "any day now",
    "week": "seven days",
    "today": "RIGHT NOW",
    "tomorrow": "within hours",
    "again": "yet again",
    "never": "NEVER EVER",
    "always": "every single time",
    "secret": "classified",
    "hidden": "buried",
    "true": "confirmed",
    "false": "debunked",
    "fake": "staged",
    "real": "100% real",
    "happening": "unfolding",
    "happened": "went down",
    "going": "headed",
    "using": "weaponizing",
    "wants": "demands",
    "need": "must",
    "should": "MUST",
    "might": "WILL",
    "could": "will",
    "maybe": "definitely",
    "probably": "certainly",
    "allegedly": "undeniably",
}
INTENSIFIERS = ["literally", "absolutely", "100%", "completely", "totally", "unbelievably", "incredibly", "extremely", "utterly", "positively", "definitely",]
EMOJI = ["🔥", "😡", "🚨", "👀",("🙏"), "💯", ]

# Every mutation has the same shape: (text, rng) -> text.
# Passing rng in (instead of using the global random) keeps results repeatable.

def swap_synonyms(text, rng):
    out = []
    for w in text.split():
        # split into leading punctuation, the word itself, trailing punctuation
        m = re.match(r"^(\W*)(.*?)(\W*)$", w)
        pre, core, post = m.groups()
        swap = SYNONYMS.get(core.lower())
        if swap:
            if core[:1].isupper():          # keep a capital letter if there was one
                swap = swap[:1].upper() + swap[1:]
            out.append(pre + swap + post)
        else:
            out.append(w)
    return " ".join(out)
def exaggerate(text, rng):
    words = text.split()
    words.insert(rng.randrange(len(words) + 1), rng.choice(INTENSIFIERS))
    return " ".join(words)

def caps(text, rng):
    return text.upper()

def add_emoji(text, rng):
    return text + " " + "".join(rng.choices(EMOJI, k=rng.randint(1, 3)))

def breaking_prefix(text, rng):
    return "BREAKING: " + text

def question_frame(text, rng):
    # TODO: wrap in "Why is nobody talking about ..." / "Just asking questions: ..."
    return text

def typo(text, rng):
    # TODO: swap two adjacent letters at a random position
    return text

def add_hashtag(text, rng):
    # TODO: use the longest word in the sentence as a hashtag
    return text

# A voice = a personality: which mutations it can pick from.
VOICES = {
    "outraged":  [caps, exaggerate, add_emoji, breaking_prefix],
    "concerned": [question_frame, swap_synonyms, add_emoji],
    "cheerful":  [add_emoji, add_hashtag, exaggerate],
    "sloppy":    [typo, swap_synonyms, add_hashtag],
}

def make_handle(rng):
    return f"{rng.choice(ADJECTIVES)}{rng.choice(NOUNS)}{rng.randint(1000, 9999)}"

def generate_swarm(text, n=40):
    # Seed from the text itself so the same sentence gives the same swarm.
    seed = int(hashlib.sha256(text.encode()).hexdigest(), 16)
    rng = random.Random(seed)

    bots = []
    for _ in range(n):
        voice = rng.choice(list(VOICES))
        chosen = rng.sample(VOICES[voice], k=min(rng.randint(2, 3), len(VOICES[voice])))
        mutated = text
        for fn in chosen:
            mutated = fn(mutated, rng)
            
            lat, lon = random_location(rng)
            
        bots.append({
            "handle": make_handle(rng),
            "text": mutated,
            "voice": voice,
            "mutations": [fn.__name__ for fn in chosen],
            # exponential distribution: most bots land early, a few trail in
            "delay_ms": int(rng.expovariate(1 / 600)),
            "lat": lat,                          # <-- 2. add the two keys
            "lon": lon,
        })
    return bots