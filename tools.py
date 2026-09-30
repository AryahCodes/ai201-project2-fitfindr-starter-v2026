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

import config
from generate import generate
from utils.data_loader import load_listings


def _size_matches(listing_size: str, query_size: str) -> bool:
    """Case-insensitive size match without single-letter false positives."""
    listing_lower = listing_size.lower()
    query_lower = query_size.lower().strip()

    parts = [p for p in re.split(r"[/\s(),]+", listing_lower) if p]
    if query_lower in parts:
        return True

    if len(query_lower) == 1:
        return bool(
            re.search(
                rf"(^|[/\s(,]){re.escape(query_lower)}([/\s),/]|$)",
                listing_lower,
            )
        )

    return query_lower in listing_lower


def _keyword_score(listing: dict, keywords: list[str]) -> int:
    text = " ".join(
        [
            listing.get("title") or "",
            listing.get("description") or "",
            " ".join(listing.get("style_tags") or []),
        ]
    ).lower()
    return sum(1 for word in keywords if word in text)


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
    keywords = [w.lower() for w in description.split() if w.strip()]
    results: list[tuple[int, dict]] = []

    for listing in load_listings():
        price = listing.get("price")
        if max_price is not None and (price is None or price > max_price):
            continue

        listing_size = listing.get("size") or ""
        if size is not None and listing_size and not _size_matches(listing_size, size):
            continue
        if size is not None and not listing_size:
            continue

        score = _keyword_score(listing, keywords) if keywords else 1
        if score > 0:
            results.append((score, listing))

    results.sort(key=lambda pair: pair[0], reverse=True)
    return [listing for _, listing in results[: config.SEARCH_RESULT_LIMIT]]


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
    title = new_item.get("title") or "this item"
    item_desc = new_item.get("description") or ""
    category = new_item.get("category") or ""
    style_tags = ", ".join(new_item.get("style_tags") or [])
    colors = ", ".join(new_item.get("colors") or [])

    items = wardrobe.get("items") or []
    system = (
        "You are a personal stylist helping someone shop secondhand. "
        "Be specific, practical, and concise. Suggest one or two outfits."
    )

    if not items:
        prompt = (
            f"The user is considering this thrift find:\n"
            f"- Title: {title}\n"
            f"- Description: {item_desc}\n"
            f"- Category: {category}\n"
            f"- Style tags: {style_tags}\n"
            f"- Colors: {colors}\n\n"
            f"Their wardrobe is empty, so you cannot name pieces they already own. "
            f"Give general styling advice — what kinds of bottoms, shoes, and layers "
            f"would work with this item and why."
        )
    else:
        wardrobe_lines = []
        for piece in items:
            name = piece.get("name") or "unnamed piece"
            piece_category = piece.get("category") or ""
            piece_colors = ", ".join(piece.get("colors") or [])
            piece_tags = ", ".join(piece.get("style_tags") or [])
            wardrobe_lines.append(
                f"- {name} ({piece_category}, {piece_colors}, tags: {piece_tags})"
            )
        wardrobe_text = "\n".join(wardrobe_lines)

        prompt = (
            f"The user is considering this thrift find:\n"
            f"- Title: {title}\n"
            f"- Description: {item_desc}\n"
            f"- Category: {category}\n"
            f"- Style tags: {style_tags}\n"
            f"- Colors: {colors}\n\n"
            f"Their wardrobe:\n{wardrobe_text}\n\n"
            f"Suggest one or two outfits that combine the new item with pieces "
            f"they already own. Name the specific wardrobe pieces in each outfit."
        )

    result = generate(prompt, system=system).strip()
    if result:
        return result
    return (
        f"Style {title} with relaxed denim and clean sneakers for an easy "
        f"everyday look, or layer it under an oversized jacket for more edge."
    )


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
    title = new_item.get("title") or "this find"
    price = new_item.get("price")
    platform = new_item.get("platform") or "a thrift app"
    price_text = f"${price:.0f}" if isinstance(price, (int, float)) else "unknown price"

    if not outfit or not outfit.strip():
        return (
            f"Scored {title} on {platform} for {price_text} — "
            f"still putting together the full fit card."
        )

    style_tags = ", ".join(new_item.get("style_tags") or [])
    colors = ", ".join(new_item.get("colors") or [])

    prompt = (
        f"Write a short social-media caption (2-4 sentences) about a thrift find.\n\n"
        f"Item: {title}\n"
        f"Price: {price_text}\n"
        f"Platform: {platform}\n"
        f"Colors: {colors}\n"
        f"Style: {style_tags}\n\n"
        f"Outfit idea to reference:\n{outfit.strip()}\n\n"
        f"Mention the item, its price, and {platform} once each. "
        f"Sound like a real person posting a find, not a product listing. "
        f"Be specific about the vibe."
    )
    system = (
        "You write concise, natural thrift-shopping captions for social media. "
        "No hashtags unless they feel organic. Keep it to 2-4 sentences."
    )

    result = generate(prompt, system=system).strip()
    if result:
        return result
    return (
        f"Could not miss this {title} on {platform} for {price_text}. "
        f"Already planning to wear it with the look above."
    )
