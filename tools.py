"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import re
import config  # noqa: F401 — you'll use this in search_listings
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    query_words = _keywords(description)
    if not query_words:
        return []

    scored = []
    for listing in load_listings():
        if max_price is not None and listing["price"] > max_price:
            continue
        if size and not _size_matches(size, listing["size"]):
            continue

        score = _score(query_words, listing)
        if score > 0:
            scored.append((score, listing))

    # sorted() is stable, so ties keep their order from the data file.
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in scored[: config.SEARCH_RESULT_LIMIT]]


# Words that carry no meaning about the item, so they shouldn't earn points.
_STOPWORDS = {"a", "an", "and", "the", "for", "with", "in", "of", "to", "or", "on"}


def _normalize_word(word: str) -> str:
    """Lowercase and strip a plural 's' so "tees" matches "tee"."""
    word = word.lower()
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word


def _keywords(text: str) -> set[str]:
    """Split text into a set of normalized keywords, dropping stopwords."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {_normalize_word(w) for w in words if len(w) > 1 and w not in _STOPWORDS}


def _score(query_words: set[str], listing: dict) -> int:
    """
    Keyword overlap between the query and a listing.

    A word found in the title, category, or style tags is worth 2 — those
    fields say what the item *is*. A word found only in the description,
    colors, or brand is worth 1.
    """
    strong = _keywords(" ".join([listing["title"], listing["category"], *listing["style_tags"]]))
    weak = _keywords(" ".join([listing["description"], *listing["colors"], listing["brand"] or ""]))

    score = 0
    for word in query_words:
        if word in strong:
            score += 2
        elif word in weak:
            score += 1
    return score


def _size_tokens(size: str) -> set[str]:
    """
    Break a size string into whole size tokens.

        "S/M"            → {"S", "M"}
        "XL (oversized)" → {"XL"}
        "W30 L30"        → {"W30", "L30"}
        "US 8.5"         → {"US8.5"}
        "8.5"            → {"US8.5"}   (a bare number is a shoe size)
    """
    size = re.sub(r"\(.*?\)", " ", size.upper())        # drop "(oversized)" notes
    size = re.sub(r"\bUS\s+", "US", size)                # "US 8.5" → "US8.5"
    tokens = set()
    for token in re.split(r"[\s/]+", size):
        if not token:
            continue
        if re.fullmatch(r"\d+(\.\d+)?", token):
            token = "US" + token
        tokens.add(token)
    return tokens


def _size_matches(requested: str, listing_size: str) -> bool:
    """
    True when the requested size matches the listing's size as a whole token.

    "M" matches "M", "S/M", and "M/L" but not "XL" or "US 9". "L" does not
    match "W30 L30". A "One Size" listing matches any requested size.
    """
    if listing_size.strip().upper().startswith("ONE SIZE"):
        return True
    return bool(_size_tokens(requested) & _size_tokens(listing_size))


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, ask the model for general styling ideas for this item.
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []
    item_text = _describe_item(new_item)

    if not items:
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            "They haven't told us what's in their wardrobe. Suggest one or two "
            "outfits built around this item, using common basics most people own "
            "(say what kind of piece, e.g. 'straight-leg blue jeans'). For each "
            "outfit, give it a short name, list the pieces, and say in one "
            "sentence why it works."
        )
    else:
        wardrobe_text = "\n".join(_describe_wardrobe_item(w) for w in items)
        prompt = (
            f"Someone is thinking about buying this thrifted item:\n{item_text}\n\n"
            f"Here is what they already own:\n{wardrobe_text}\n\n"
            "Suggest one or two outfits that pair the new item with pieces from "
            "their wardrobe. Name each wardrobe piece exactly as it is written "
            "above, and only use pieces from that list. For each outfit, give it "
            "a short name, list the pieces, and say in one sentence why it works."
        )

    response = generate(prompt, system=_STYLIST_SYSTEM).strip()
    if not response:
        return (
            f"No outfit suggestion came back for the {new_item['title']}. "
            "Try pairing it with simple basics in neutral colors."
        )
    return response


_STYLIST_SYSTEM = (
    "You are a practical thrift stylist. Keep suggestions short and concrete: "
    "plain text, no preamble, no more than two outfits."
)


def _describe_item(item: dict) -> str:
    """One listing as a few readable lines for a prompt. Brand may be None."""
    lines = [
        f"- {item['title']} ({item['category']})",
        f"  Colors: {', '.join(item['colors'])}",
        f"  Style: {', '.join(item['style_tags'])}",
        f"  Details: {item['description']}",
    ]
    if item.get("brand"):
        lines.insert(1, f"  Brand: {item['brand']}")
    return "\n".join(lines)


def _describe_wardrobe_item(item: dict) -> str:
    """One wardrobe piece as a single prompt line. Notes may be None."""
    line = (
        f"- {item['name']} "
        f"({item['category']}; "
        f"colors: {', '.join(item['colors'])}; "
        f"style: {', '.join(item['style_tags'])})"
    )

    if item.get("notes"):
        line += f" — {item['notes']}"

    return line


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    if not outfit or not outfit.strip():
        return "Couldn't write a fit card — no outfit suggestion was provided."

    price = f"${new_item['price']:.0f}" if new_item["price"] == int(new_item["price"]) else f"${new_item['price']:.2f}"
    prompt = (
        f"Write a caption for a social post about this thrift find.\n\n"
        f"The item:\n{_describe_item(new_item)}\n"
        f"  Price: {price}\n"
        f"  Platform: {new_item['platform']}\n\n"
        f"How they're styling it:\n{outfit.strip()}\n\n"
        "Rules:\n"
        "- 2 to 4 sentences, written in first person like a real post, not a product listing. "
        "The poster BOUGHT this item on the platform; they are not selling it.\n"
        f"- Mention the item, the price, and the platform exactly once each. "
        f"Write the price as digits, exactly \"{price}\" — never spelled out in words.\n"
        "- Pick ONE outfit from the styling notes and be specific about its vibe.\n"
        "- No hashtags, no quotation marks around the caption, no preamble."
    )

    response = generate(prompt, system=_CAPTION_SYSTEM).strip()
    if not response:
        return f"Thrifted the {new_item['title']} for {price} on {new_item['platform']} — styling post coming soon."
    return response


_CAPTION_SYSTEM = (
    "You write short, natural social captions about thrifted outfits. "
    "Follow the user's formatting and content requirements exactly."
)
