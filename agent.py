import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
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
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
        "note": None,                # set when the chosen item doesn't match a color the user asked for
    }


# ── parsing the query ─────────────────────────────────────────────────────────

# Sizes a user is likely to type. Matched as whole words so that the "M" in
# "Medium Wash" or the "L" in "L/XL" can't be mistaken for a request.
_SIZE_WORDS = r"XXS|XS|S|M|L|XL|XXL"

_PRICE_RE = re.compile(r"(?:under|below|less than|max|up to)?\s*\$\s*(\d+(?:\.\d+)?)", re.I)
_SIZE_RE = re.compile(rf"\bsize\s+({_SIZE_WORDS}|US\s*\d+(?:\.\d+)?|W\d+)\b", re.I)
_BARE_SIZE_RE = re.compile(rf",\s*({_SIZE_WORDS})\s*$", re.I)


def parse_query(query: str) -> dict:
    """
    Pull a description, a size and a price ceiling out of what the user typed.

    Regex rather than a model call, for three reasons worth writing down: it
    costs nothing, it returns the same answer twice (which the unit 4 state
    criterion depends on), and when it gets something wrong the reason is
    readable in the pattern instead of being a model's opinion.

    What it gives up is phrasing it has never seen. "nothing over thirty
    dollars" parses to no price at all, and the run then quietly ignores the
    ceiling. That limitation is in the README rather than hidden here.

    Returns a dict with keys `description` (str), `size` (str or None) and
    `max_price` (float or None).
    """
    text = query or ""

    max_price = None
    price_match = _PRICE_RE.search(text)
    if price_match:
        max_price = float(price_match.group(1))
        text = text[: price_match.start()] + " " + text[price_match.end() :]

    size = None
    size_match = _SIZE_RE.search(text) or _BARE_SIZE_RE.search(text)
    if size_match:
        size = re.sub(r"\s+", " ", size_match.group(1)).strip().upper()
        text = text[: size_match.start()] + " " + text[size_match.end() :]

    description = re.sub(r"[,\s]+", " ", text).strip(" ,")
    return {"description": description, "size": size, "max_price": max_price}


# ── planning loop ─────────────────────────────────────────────────────────────

def _search(parsed: dict) -> list[dict]:
    """
    Call search_listings through the MCP server.

    There is no direct-call fallback: if the MCP server is not reachable or
    the tool is not registered, this raises, so a broken MCP connection
    shows up immediately instead of being hidden.
    """

    from mcp_client import call_tool

    results = call_tool(
        "search_listings",
        {
            "description": parsed["description"],
            "size": parsed["size"],
            "max_price": parsed["max_price"],
        },
    )
    return results or []


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

    The branch rule, stated once so the code below can be read against it:

        If search_listings returns an empty list, put a message in
        session["error"] naming what the user could change, and return the
        session without calling suggest_outfit. Otherwise take the first
        result, put it in session["selected_item"], and continue.
    """
    session = new_session(query, wardrobe)
    steps = 0

    # ⚠️ UNIT 4, MILESTONE 2 — everything in the try/except is unit 3 code; the
    # handler around it is what unit 4 adds, so that a bad key produces a
    # sentence rather than a stack trace.
    try:
        steps += 1
        trace.check_iterations(steps)
        parsed = parse_query(query)
        session["parsed"] = parsed
        trace.step("parse_query", inputs=query, returned=str(parsed))

        steps += 1
        trace.check_iterations(steps)
        results = _search(parsed)
        session["search_results"] = results
        trace.step(
            "search_listings (via MCP)",
            inputs=str(parsed),
            returned=results,
            note=f"{len(results)} match(es)",
        )

        # ── THE BRANCH ────────────────────────────────────────────────────────
        if not results:
            session["error"] = _nothing_found_message(parsed)
            trace.step(
                "branch",
                note="search returned []: stopping before suggest_outfit",
            )
            return session

        steps += 1
        trace.check_iterations(steps)
        session["selected_item"] = results[0]
        trace.step("select_item", returned=session["selected_item"])
        # ── second branch: warn when the chosen item isn't the color asked for ──
        session["note"] = _color_mismatch(parsed, session["selected_item"])
        if session["note"]:
            trace.step("check_color", note=session["note"])

        steps += 1
        trace.check_iterations(steps)
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"], session["wardrobe"]
        )
        trace.step(
            "suggest_outfit",
            inputs=session["selected_item"],
            returned=session["outfit_suggestion"],
            note=f"{len(session['wardrobe'].get('items') or [])} wardrobe item(s)",
        )

        steps += 1
        trace.check_iterations(steps)
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"], session["selected_item"]
        )
        trace.step(
            "create_fit_card",
            inputs=session["selected_item"],
            returned=session["fit_card"],
        )

    except ModelUnavailable as exc:
        session["error"] = (
            f"The model couldn't be reached, so the outfit and caption steps "
            f"didn't run. The search worked — "
            f"{len(session['search_results'])} listing(s) were found. "
            f"Check GEMINI_API_KEY in your .env, then run the same query "
            f"again.\nWhat the service said: {exc}"
        )
        trace.step("model unavailable", note="stopping, search results kept")

    return session

# ── second branch: does the chosen item match the color asked for? ───────────

_COLOR_WORDS = {
    "black", "white", "brown", "red", "blue", "navy", "green", "grey", "gray",
    "pink", "purple", "cream", "tan", "khaki", "olive", "burgundy", "rust",
    "yellow", "orange", "beige",
}


def _color_mismatch(parsed: dict, item: dict) -> str | None:
    asked = [w for w in re.findall(r"[a-z]+", (parsed.get("description") or "").lower())
             if w in _COLOR_WORDS]
    if not asked:
        return None

    item_words = set(re.findall(
        r"[a-z]+",
        " ".join([item.get("title") or "", " ".join(item.get("colors") or [])]).lower(),
    ))
    missing = [c for c in asked if c not in item_words]
    if not missing:
        return None

    actual = ", ".join(item.get("colors") or []) or "not listed"
    return (
        f"No {' or '.join(missing)} match was found, so this is the closest "
        f"match instead. Its color is {actual}."
    )


def _nothing_found_message(parsed: dict) -> str:
    """
    What to say when the search comes back empty.

    "No results" is not this message. This one names the three things the user
    actually controls, and says which of them were in play — a ceiling they
    never set is not a ceiling worth suggesting they raise.
    """
    tried = [f"description {parsed['description']!r}"]
    if parsed["size"]:
        tried.append(f"size {parsed['size']}")
    if parsed["max_price"] is not None:
        tried.append(f"under ${parsed['max_price']:g}")

    suggestions = ["try broader words — 'jacket' finds more than 'cropped corduroy jacket'"]
    if parsed["size"]:
        suggestions.append("drop the size, or try a neighbouring one")
    if parsed["max_price"] is not None:
        suggestions.append(f"raise the price ceiling above ${parsed['max_price']:g}")

    return (
        "Nothing in the listings matched " + ", ".join(tried) + ".\n"
        "Things to change: " + "; ".join(suggestions) + "."
    )


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
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