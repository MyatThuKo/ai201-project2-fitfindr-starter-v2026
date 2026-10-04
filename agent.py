"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card, compare_prices
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "price_comparison": None,    # what compare_prices returned
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

# Words that describe the request but never appear in a listing, so they would
# only add noise to the keyword match in search_listings.
_FILLER = {"looking", "for", "a", "an", "the", "i", "want", "need", "some", "in", "me", "find"}


def parse_query(query: str) -> dict:
    """
    Pull a description, a size, and a max_price out of a plain-language query,
    using regex.

        "vintage graphic tee under $30, size M"
            → {"description": "vintage graphic tee", "size": "M", "max_price": 30.0}

    size and max_price are None when the query doesn't mention them.
    """
    text = query.strip()

    # Price: "under $30", "below 30", "less than $30.50", "max $30", "$30 or less"
    max_price = None
    price_match = re.search(
        r"(?:under|below|less than|max|up to)\s*\$?(\d+(?:\.\d+)?)"
        r"|\$(\d+(?:\.\d+)?)\s*(?:or less|max)?",
        text,
        re.IGNORECASE,
    )
    if price_match:
        max_price = float(price_match.group(1) or price_match.group(2))
        text = text.replace(price_match.group(0), " ")

    # Size: "size M", "size S/M", "size US 8.5", "size W30", "size 8"
    size = None
    size_match = re.search(
        r"\b(?:in\s+)?size\s+(US\s*\d+(?:\.\d+)?|W\d+(?:\s*L\d+)?|[A-Za-z0-9./]+)",
        text,
        re.IGNORECASE,
    )
    if size_match:
        size = size_match.group(1).strip()
        text = text.replace(size_match.group(0), " ")

    # Whatever is left, minus punctuation and filler words, is the description.
    words = re.findall(r"[A-Za-z0-9'-]+", text)
    description = " ".join(w for w in words if w.lower() not in _FILLER)

    return {"description": description, "size": size, "max_price": max_price}


def _no_results_message(parsed: dict) -> str:
    """Tell the user what they could change, based on what they asked for."""
    tips = []
    if parsed["max_price"] is not None:
        tips.append(f"raise your price limit above ${parsed['max_price']:.0f}")
    if parsed["size"]:
        tips.append(f"drop the size filter ({parsed['size']})")
    tips.append("use broader words than \"" + parsed["description"] + "\"")
    return "No listings matched. Try: " + "; or ".join(tips) + "."


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.

    ─────────────────────────────────────────────────────────────────────────
    TODO — build this, following the branch rule you wrote in Milestone 2.

      1. Start a session with new_session().

      2. Count the times round the loop, and call trace.check_iterations(count)
         on each one before you go again. It raises when the count passes
         MAX_ITERATIONS in config.py — see trace.py.

      3. Parse the query into a description, a size, and a max_price. Regex,
         string splitting, or asking the model are all fine — say which you
         chose in your README. Put the result in session["parsed"].

      4. Call search_listings() with what you parsed.
         Put the results in session["search_results"].

         ⚠️ THIS IS THE BRANCH. If nothing came back:
              - put a message in session["error"] saying what the user could
                change — "No results" is not that message
              - return the session
              - do NOT call suggest_outfit with nothing

      5. Choose an item — the first result is fine. Put it in
         session["selected_item"].

      6. Call suggest_outfit() with the selected item and the wardrobe.
         Put the result in session["outfit_suggestion"].

      7. Call create_fit_card() with the outfit and the item.
         Put the result in session["fit_card"].

      8. Return the session.

    ─────────────────────────────────────────────────────────────────────────
    IN UNIT 4 you come back and add two things:

      • Trace calls. One per step. `trace.step("search_listings", inputs=...,
        returned=...)` — see trace.py. Your README needs the output.

      • A handler for ModelUnavailable, so a bad key produces a message rather
        than a stack trace. The import is already at the top of this file.
    """
    # 1. Start a session.
    session = new_session(query, wardrobe)
    iterations = 0

    # 2–3. Parse the query.
    iterations += 1
    trace.check_iterations(iterations)
    session["parsed"] = parse_query(query)
    parsed = session["parsed"]

    # 4. Search.
    iterations += 1
    trace.check_iterations(iterations)
    session["search_results"] = search_listings(
        parsed["description"],
        size=parsed["size"],
        max_price=parsed["max_price"],
    )

    # THE BRANCH: nothing found → explain what to change and stop here.
    # suggest_outfit and create_fit_card are never called on this path.
    if not session["search_results"]:
        session["error"] = _no_results_message(parsed)
        return session

    # 5. Choose the best match (search_listings returns best match first).
    session["selected_item"] = session["search_results"][0]

    # 5b. Stretch: compare the chosen item's price with the other results.
    iterations += 1
    trace.check_iterations(iterations)
    session["price_comparison"] = compare_prices(
        session["selected_item"], session["search_results"]
    )

    # 6. Suggest an outfit, reading the item back out of the session.
    iterations += 1
    trace.check_iterations(iterations)
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"], session["wardrobe"]
    )

    # 7. Write the fit card from what's in the session.
    iterations += 1
    trace.check_iterations(iterations)
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"], session["selected_item"]
    )

    # 8. Done.
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  price:    {session['price_comparison']['summary']}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
