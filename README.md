# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ``` bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet. That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

------------------------------------------------------------------------

```{=html}
<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->
```

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a three-tool thrifting agent that finds a listing, works out what it would go with, and writes a caption for it.

A user types what they want in plain language, and FitFindr searches listings.

If it finds one, it suggests 2 to 3 outfits that pair the item with pieces from the user's wardrobe and writes a short caption they could post with the look.

------------------------------------------------------------------------

## Tool Inventory

```{=html}
<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->
```

### `search_listings`

-   **What it does:** Searches listings and returns those matching the description, size, and price limit.
-   **Inputs:** description (str), size (str/None), max_price (float/None)
-   **Returns:** A list of matching listing dicts, best match first. Each listing contains id(str), title (str), description (str), category (str), style_tags (list of str), size (str), condition (str), price (float), colors (list of str), brand (str/None), platform (str).
-   **When it has nothing:** Only returns an empty list.
-   Matching rules:
    -   Description: lowercase it, split it into words, and drop filler words and single characters. Each word found in the title, category, or style_tags scores 2 points; each word found only in the description, brand, or colors scores 1 point. Listings scoring 0 are dropped. Ties are broken by lower price. At most 10 results. 
    -   Size: remove anything in parentheses from the listing's size, split it on "/", and uppercase it. A listing matches if the user's size equals one of those parts. Listings whose size starts with "One Size" match any size. 
    -   Price: a listing matches if price \<= max_price. 
    -   If size or max_price is None, that filter is skipped.

### `suggest_outfit`

-   **What it does:** Given a thrifted item and the user's wardrobe, calls the model to suggest outfits that pair the new item with pieces from the user's wardrobe.
-   **Inputs:** new_item (dict), wardrobe (dict with one key: "items", with a list of those fields: id (str), name (str), category (str), colors (list), style_tags (list), notes (str) )
-   **Returns:** An str containing outfit ideas.
-   **When it has nothing:**
    -   If wardrobe["items"] is empty, returns general styling advice for the item rather than raising or returning "".
    -   If new_item is empty or None, returns "" without calling the model.

### `create_fit_card`

-   **What it does:** Write a short caption someone would actually post about the outfit.
-   **Inputs:** outfit (str), new_item (dict)
-   **Returns:** A two-to-four sentence caption, mentioning the item and its price and platform once each, and being specific about the vibe.
-   **When it has nothing:**
    -   If outfit is empty, returns a caption about new_item alone.
    -   If new_item is empty or None, returns "".

------------------------------------------------------------------------

## Planning Loop

```{=html}
<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->
```

**Branch rule:** If search_listings returns an empty list, put a message repeating the description, size, and max price that were searched and suggest the user to change one in the session and stop. Otherwise take the first result and go to suggest_outfit.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** regex. The word after "size"(XXS to XXL, US 7, etc...) or a bare size at the end after a comma, becomes size, uppercased. Any number after or before the '\$' sign and after "under", "below", or "max" becomes max_price. Everything else becomes description. If it contains no price, max_price is None. If it contains no size, then size is None.

**What moves through the session:**

-   session["query"]: the raw query string the user entered

-   session["parsed"]: dict with description, size, max_price

-   session["results"]: list returned by search_listings

-   session["selected_item"]: the first dict in session["results"]

-   session["outfit"]: str returned by suggest_outfit(session["selected_item"], wardrobe)

-   session["fit_card"]: str returned by create_fit_card(session["outfit"], session["selected_item"])

------------------------------------------------------------------------

## Sample Run

```{=html}
<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->
```

**One full query**

```         
$ python app.py ask '...'
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[suggest_outfit] received item id: lst_002
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Outfit 1: Streetwear Contrast Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans. Laye…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Score this vintage butterfly baby tee for just $18 on Depop and I am obsessed. The pink and purple print gives…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Streetwear Contrast
Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans. Layer the black cropped zip hoodie on top, left unzipped to show the graphic. Finish with chunky white sneakers and your black crossbody bag for an easy everyday look.

Outfit 2: Model-Off-Duty Grunge
Wear the Y2K Baby Tee — Butterfly Print tucked into your wide-leg khaki trousers. Add the vintage black denim jacket and anchor the look with black combat boots. Cinch the waist with your brown leather belt to pull the earth tones together. 

Outfit 3: Layered Transition
Slip the Y2K Baby Tee — Butterfly Print underneath your oversized grey crewneck sweatshirt, letting the pink and purple butterfly hem peek out the bottom. Pair with your baggy straight-leg jeans and chunky white sneakers for a cozy, texture-rich outfit.

  Fit card: Score this vintage butterfly baby tee for just $18 on Depop and I am obsessed. The pink and purple print gives the ultimate Y2K model-off-duty vibe. Can't wait to style this with baggy jeans and chunky sneakers!

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```         
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}]

# Actually the output is quite hard to read,so used another command to have a clearer structure:
python -c 'from tools import search_listings; [print(r["id"], "$" + format(r["price"], "g"), r["size"], r["platform"], r["title"], sep="  |  ") for r in search_listings("graphic tee", max_price=30)]'

lst_002  |  $18  |  S/M  |  depop  |  Y2K Baby Tee — Butterfly Print
lst_033  |  $19  |  L  |  depop  |  Vintage Band Tee — Faded Grey
lst_006  |  $24  |  L  |  depop  |  Graphic Tee — 2003 Tour Bootleg Style
lst_017  |  $15  |  S/M  |  depop  |  Mesh Long-Sleeve Top — Black
lst_015  |  $26  |  L  |  depop  |  Vintage Graphic Hoodie — Faded Black
lst_011  |  $27  |  W29  |  poshmark  |  Low-Rise Cargo Pants — Khaki
```

```         
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

[suggest_outfit] received item id: lst_001
Outfit 1: Casual Streetwear
Pair the Vintage Levi's 501 Jeans — Medium Wash with the white ribbed tank top, the black cropped zip hoodie layered on top, and the chunky white sneakers. Add the black crossbody bag to complete the look.

Outfit 2: Cozy Contrast
Combine the Vintage Levi's 501 Jeans — Medium Wash with the oversized grey crewneck sweatshirt and the brown leather belt cinched at the waist. Finish with the black combat boots for a grounded streetwear silhouette.

Outfit 3: Double Denim
Style the Vintage Levi's 501 Jeans — Medium Wash with the white ribbed tank top and the vintage black denim jacket. Accessorize with the brown leather belt and the black combat boots.
```

```         
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Scored these vintage Levi's 501 jeans for just $38 on depop and the wash is so good. Can't wait to wear them with crisp white sneakers for that effortless 90s off-duty look.
```

------------------------------------------------------------------------

## How I Used AI

```{=html}
<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->
```

**Moment 1**

-   *What I asked for: I gave claude my version of what this does mixing different languages and ask it to tweak my wording.*
-   *What came back: Claude pointed out grammar problems and translated my words in other languages.*
-   *What I changed: I changed the grammar problems, and rephrase the sentences to my liking.*

**Moment 2**

-   *What I asked for: I pasted the criteria into Claude and asked what they'd do.*
-   *What came back: They suggested the moves that I could check it.*
-   *What I changed: I keep those in mind as I move on to the next milestone.*

```{=html}
<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->
```

------------------------------------------------------------------------

## Run Log — Before

```{=html}
<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->
```

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|-----------|--------|-------|-------|-------|-------|-------|---------|
| 1\.       |        |       |       |       |       |       |         |
| 2\.       |        |       |       |       |       |       |         |
| 3\.       |        |       |       |       |       |       |         |
| 4\.       |        |       |       |       |       |       |         |
| 5\.       |        |       |       |       |       |       |         |

**Real output from one try**, pasted as text, naming the file and function that produced it:

```         
```

------------------------------------------------------------------------

## Verdicts and Diagnoses

```{=html}
<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->
```

| \#  | Criterion | Target | Verdict | How I decided |
|-----|-----------|--------|---------|---------------|
| 1   |           |        |         |               |
| 2   |           |        |         |               |
| 3   |           |        |         |               |
| 4   |           |        |         |               |
| 5   |           |        |         |               |

**Diagnoses**

------------------------------------------------------------------------

## Loop Trace

```{=html}
<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->
```

**Happy path**

```         
```

**Empty search**

```         
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

------------------------------------------------------------------------

## The Improvement

```{=html}
<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->
```

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|-----------|--------|-------|-------|-------|-------|-------|---------|
| 1\.       |        |       |       |       |       |       |         |
| 2\.       |        |       |       |       |       |       |         |
| 3\.       |        |       |       |       |       |       |         |
| 4\.       |        |       |       |       |       |       |         |
| 5\.       |        |       |       |       |       |       |         |

**Did it help, and how do I know:**

```{=html}
<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->
```

------------------------------------------------------------------------

## What's Still Broken

```{=html}
<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->
```

```{=html}
<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->
```

------------------------------------------------------------------------

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
