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

-   session["wardrobe"]: the wardrobe dict passed into run_agent

-   session["parsed"]: dict with description, size, max_price

-   session["search_results"]: list returned by search_listings (called through MCP)

-   Branch: if session["search_results"] is empty, set session["error"] and return. session["selected_item"], session["outfit_suggestion"], and session["fit_card"] stay None.

-   session["selected_item"]: the first dict in session["search_results"]

-   session["outfit_suggestion"]: str returned by suggest_outfit(session["selected_item"], session["wardrobe"])

-   session["fit_card"]: str returned by create_fit_card(session["outfit_suggestion"], session["selected_item"])

------------------------------------------------------------------------

## Sample Run

```{=html}
<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->
```

**One full query**

```         
$ python app.py ask 'vintage graphic tee under $30'
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

**Moment 3**

-   *What I asked for: I asked why the criteria were all met.*

-   *What came back: They suggested that #3 and #4 are the clearest cases that my criteria are loose. Stating that I picked the test queries myself and I likely used wording that matches the listings.*

-   *What I changed: Write this in what's still broken and reflect on it.*

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

      python run_eval.py --label before  runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->
```

+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| Criterion                                                  | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
+============================================================+========+=======+=======+=======+=======+=======+=========+
| 1.  A matching query completes all three tools             | 4 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 2.  An impossible query stops before the second tool       | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 3.  The searched item is the item suggest_outfit receives  | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 4.  Something about the fit card                           | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 5.  If the wardrobe is empty, returns not empty suggestion | 4 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+

**Real output from one try**, pasted as text, naming the file and function that produced it:

Below are:

:   Real output from one try, pasted from results/run_2026-10-12_2111_before.md (produced by run_eval.py::main , which calls agent.py::run_agent ; tools in tools.py ). Try 1 of each scenario.

**Criterion 1:**

```         
### matching query completes

- Query:  vintage graphic tee under $30 
- Wardrobe: example

**Try 1**

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:

   
Outfit 1: Streetwear Contrast
Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark wash. Layer the black cropped zip hoodie unzipped over top. Finish with chunky white sneakers and the black crossbody bag to balance the fitted tee with the loose denim.

Outfit 2: Casual Vintage
Wear the Y2K Baby Tee — Butterfly Print tucked into your wide-leg khaki trousers. Add the vintage black denim jacket for an extra layer, and tie the look together with the brown leather belt and chunky white sneakers for an easy earth-toned everyday outfit.

Outfit 3: Grunge Edge
Style the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark wash. Throw on the vintage black denim jacket and ground the sweet butterfly print with your black combat boots and the black crossbody bag for a sharp high-low mix.
   

Fit card:

   
Scored this sweet Y2K butterfly tee for just $18 on depop! Obsessed with the pink and purple print—gonna style it with baggy denim and combat boots for that perfect high-low grunge vibe. 🦋✨
   

Trace:

   
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Outfit 1: Streetwear Contrast Pair the Y2K Baby Tee — Butterfly Print with your baggy straight-leg jeans, dark…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Scored this sweet Y2K butterfly tee for just $18 on depop! Obsessed with the pink and purple print—gonna style…
```

**Criterion 2:**

```         
### impossible query stops early

- Query:  designer ballgown size XXS under $5 
- Wardrobe: example

**Try 1**

- stopped early: yes — Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
- selected_item: (none)
- search_results: 0

Trace:

   
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
```

**Criterion 3 and 4:**

```         
Criteria 3 and 4, state check: belt, Try 1 (from  results/run_2026-10-12_2111_before.md , produced by  run_eval.py::main  calling  agent.py::run_agent):

### state check: belt

- Query:  black leather belt under $21 
- Wardrobe: example

**Try 1**

- stopped early: no
- selected_item: Leather Belt — Brown, Braided ($12.0, thredUp)
- search_results: 3

Outfit suggestion:

   
Outfit 1: Casual Denim
Pair the Leather Belt — Brown, Braided with the baggy straight-leg jeans, dark wash, white ribbed tank top, vintage black denim jacket, and chunky white sneakers. Cinch the high-waisted jeans with the braided belt to break up the indigo denim and white tank, finishing with the cropped jacket and sneakers.

Outfit 2: Earth Tone Minimalist
Wear the Leather Belt — Brown, Braided with the wide-leg khaki trousers, white ribbed tank top, and black combat boots. Thread the brown belt through the khaki trousers for contrast against the fitted white tank, and anchor the look with the chunky black boots. 

Outfit 3: Cozy Streetwear
Style the Leather Belt — Brown, Braided with the baggy straight-leg jeans, black cropped zip hoodie, and black combat boots. Let the braided leather belt peek out below the cropped black hoodie to add texture to the dark wash jeans, paired with the lace-up boots.
   

Fit card:

   
Found this gorgeous vintage braided leather belt on thredUp for just $12! Obsessed with how the rich brown earth tones elevate a simple jeans and a tank combo. Such a versatile piece for fallback styling.
   

Trace:

   
[1] parse_query
      in:  black leather belt under $21
      out: {'description': 'black leather belt', 'size': None, 'max_price': 21.0}
[2] search_listings (via MCP)
      in:  {'description': 'black leather belt', 'size': None, 'max_price': 21.0}
      out: 3 items: Leather Belt — Brown, Braided, Biker Shorts — Black, Shiny, Mesh Long-Sleeve Top — Black
      →    3 match(es)
[3] select_item
      out: Leather Belt — Brown, Braided ($12.0, thredUp)
[4] suggest_outfit
      in:  Leather Belt — Brown, Braided ($12.0, thredUp)
      out: Outfit 1: Casual Denim Pair the Leather Belt — Brown, Braided with the baggy straight-leg jeans, dark wash, wh…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Leather Belt — Brown, Braided ($12.0, thredUp)
      out: Found this gorgeous vintage braided leather belt on thredUp for just $12! Obsessed with how the rich brown ear…
      
[suggest_outfit] received item id: lst_014 (retrieved from console_before.txt)
```

**Criterion 5:**

````         
### empty wardrobe

- Query: `denim jacket under $50`
- Wardrobe: empty

**Try 1**

- stopped early: no
- selected_item: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
- search_results: 7

Outfit suggestion:

```
Here are three ways to style your Wrangler Denim Jacket — Light Wash, Cropped. 

Off-Duty Streetwear: Pair the jacket with black leggings, a white cotton t-shirt, and chunky sneakers. Add a baseball cap for an easy, everyday look.

Retro Casual: Layer the cropped denim over a striped long-sleeve t-shirt tucked into straight-leg black jeans. Finish with canvas sneakers and a canvas tote bag.

Dressed-Down Slip Dress: Throw the light wash jacket over a solid black midi slip dress and add worn-in white sneakers or ankle boots to balance the feminine silhouette with vintage texture.
```

Fit card:

```
Obsessed with this vintage cropped Wrangler denim jacket I just scored on Poshmark for $42! The light wash has that perfect broken-in feel for throwing over a slip dress or pairing with black leggings for off-duty days. Such a good find.
```

Trace:

```
[1] parse_query
      in:  denim jacket under $50
      out: {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
[2] search_listings (via MCP)
      in:  {'description': 'denim jacket', 'size': None, 'max_price': 50.0}
      out: 7 items: Denim Jacket — Light Wash, Cropped, High-Waisted Denim Shorts — Cutoff, Denim Vest — Medium Wash, Studded … +4 more
      →    7 match(es)
[3] select_item
      out: Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
[4] suggest_outfit
      in:  Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      out: Here are three ways to style your Wrangler Denim Jacket — Light Wash, Cropped.   Off-Duty Streetwear: Pair the…
      →    0 wardrobe item(s)
[5] create_fit_card
      in:  Denim Jacket — Light Wash, Cropped ($42.0, poshmark)
      out: Obsessed with this vintage cropped Wrangler denim jacket I just scored on Poshmark for $42! The light wash has…
```
````

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

+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| \# | Criterion                                              | Target  | Verdict | How I decided                                                                                                                                                            |
+====+========================================================+=========+=========+==========================================================================================================================================================================+
| 1  | A matching query completes all three tools             | 4 of 5  | MET     | All five tries ended with a fit card in session["fit_card"] and session["error"] still None.                                                                             |
+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2  | An impossible query stops before the second tool       | 5 of 5  | MET     | All five traces end at step 3.                                                                                                                                           |
+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 3  | The searched item is the item suggest_outfit receives  | 5 of 5  | MET     | For each of the five queries, the id printed inside the suggest_outfit(console_before.txt) matched the listing id of session['selected_item] in all five runs, 25 of 25. |
+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 4  | Something about the fit card                           | 5 of 5  | MET     | All 25 fit cards for the five items show the exact price matching the listing price. No card needed the size fallback.                                                   |
+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| 5  | If the wardrobe is empty, returns not empty suggestion | 4 of 5  | MET     | All five outfit suggestions were non-empty and named the item by its title.                                                                                              |
+----+--------------------------------------------------------+---------+---------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

**Diagnoses**

(This is awkward... I thought I was very strict when I was writing the criteria...)

No criterion was missed reading the results. I would say my targets are too easy because of the following reasons:

-   Criterion 3 is deterministic paths and 5 of 5 was the only honest target the meeting was expected.

-   Criterion 4 only checks prices in sizes so it passed even when a card had a different kind of problem: such as in Corduroy Try 3, the model output has added content. It was not asked for in one of 25 runs. ( " Buy recommendation: Yes...")

-   Criterion 5 allowed the item's title "or a recognizable part of it". In the before run the model always used the full title, so the looser wording was never needed.

    (In the after run it was needed twice: Try 1 and Try 4 called the item "Wrangler light wash, cropped denim jacket" instead of its title, but I still counted those as PASS under the wording I wrote.)

------------------------------------------------------------------------

## Loop Trace

```{=html}
<!-- One full run, printed step by step, with the MCP call visible in it.

      python app.py ask '...' --trace  once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->
```

**Happy path**

```         
% python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
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
```

**Empty search**

```         
% python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
```

**On the MCP move:**

Following the code from the class, I modified the agent.py: \_search() now calls mcp_client.call_tool("search_listings", ...) instead of calling the function directly, and I removed the starter's fallback to a direct call so that a broken MCP connection raises instead of being hidden.

And I also registered search_listings in mcp_server.py with a typed contract and a description that states the matching rules and the empty case.

Nothing behaved differently afterwards, I got the same results in the same order with the same query.

**Triggering failures:**

-   Empty search:

```         
python app.py ask 'designer ballgown size XXS under $5'
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
[2] search_listings (via MCP)
      in:  {'description': 'designer ballgown', 'size': 'XXS', 'max_price': 5.0}
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit

  Nothing in the listings matched description 'designer ballgown', size XXS, under $5.
Things to change: try broader words — 'jacket' finds more than 'cropped corduroy jacket'; drop the size, or try a neighbouring one; raise the price ceiling above $5.
```

-   Empty wardrobe:

```         
python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
(running with an empty wardrobe)
[1] parse_query
      in:  vintage graphic tee under $30
      out: {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
[2] search_listings (via MCP)
      in:  {'description': 'vintage graphic tee', 'size': None, 'max_price': 30.0}
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[suggest_outfit] received item id: lst_002
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Here are three outfit ideas for the Y2K Baby Tee — Butterfly Print:  1. Casual Streetwear: Pair the baby tee w…
      →    0 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Found this dreamy butterfly baby tee thrifting and I am so obsessed with the pink and purple print! Just liste…

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Here are three outfit ideas for the Y2K Baby Tee — Butterfly Print:

1. Casual Streetwear: Pair the baby tee with high-waisted medium-wash straight-leg jeans, white canvas sneakers, and a small shoulder bag for an easy everyday look.

2. Y2K Edge: Layer the baby tee over a long-sleeve black mesh top, add a pleated black mini skirt, knee-high boots, and a chunky silver chain necklace.

3. Soft Cottagecore: Tuck the baby tee into an olive green utility midi skirt, slip on brown leather clogs, and wear a simple cardigan over your shoulders for cooler weather.

  Fit card: Found this dreamy butterfly baby tee thrifting and I am so obsessed with the pink and purple print! Just listed it on depop for $18. Can't wait to style it with straight-leg jeans for an easy streetwear look or layer it over mesh for total Y2K vibes. 🦋✨

2 model calls this session, 465 prompt + 197 output tokens
```

-   Model unavailable:

```         
AI201_CACHE=0 python app.py ask 'black leather belt under $21'
[1] parse_query
      in:  black leather belt under $21
      out: {'description': 'black leather belt', 'size': None, 'max_price': 21.0}
[2] search_listings (via MCP)
      in:  {'description': 'black leather belt', 'size': None, 'max_price': 21.0}
      out: 3 items: Leather Belt — Brown, Braided, Biker Shorts — Black, Shiny, Mesh Long-Sleeve Top — Black
      →    3 match(es)
[3] select_item
      out: Leather Belt — Brown, Braided ($12.0, thredUp)
[suggest_outfit] received item id: lst_014
[4] model unavailable
      →    stopping, search results kept

  The model couldn't be reached, so the outfit and caption steps didn't run. The search worked — 3 listing(s) were found. Check GEMINI_API_KEY in your .env, then run the same query again.
What the service said: The model rejected your API key. Check GEMINI_API_KEY in your .env file, or create a fresh key at aistudio.google.com.

1 model calls this session
```

------------------------------------------------------------------------

## The Improvement

```{=html}
<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

      python run_eval.py --label after  -->
```

**What I changed:**

After the loop picks session["selected_item"], a new function, \_color_mismatch(), checks whether the user's description contains a color word (black, brown, navy, and so on) that does not appear in the chosen item's title or colors. If it finds one, it stores a message in a new session field, session["note"], and records a check_color step in the trace.

**Which failure it was meant to fix:**

It was meant to fix the fact that the agent silently returns a different color than the user asked for. For "black leather belt under \$21", all five runs selected the braided brown leather belt (lst_014). That is the only belt in data, and the only black leather item is a \$75 bomber jacket (lst_022), so search_listings returned the closest match, which is correct for a keyword search. The failure is in the loop: run_agent takes the first result without checking it against what the user asked for, so the user gets a brown belt, three outfits, and a caption with no sign that it is not black.

### Run Log — After

+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| Criterion                                                  | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
+============================================================+========+=======+=======+=======+=======+=======+=========+
| 1.  A matching query completes all three tools             | 4 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 2.  An impossible query stops before the second tool       | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 3.  The searched item is the item suggest_outfit receives  | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 4.  Something about the fit card                           | 5 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+
| 5.  If the wardrobe is empty, returns not empty suggestion | 4 of 5 | pass  | pass  | pass  | pass  | pass  | MET     |
+------------------------------------------------------------+--------+-------+-------+-------+-------+-------+---------+

**Did it help, and how do I know:**

```{=html}
<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->
     Scored the same way as the before run: for criteria 3 and 4, each try is one of the five queries, and a query passes only if all five of its runs pass. All five criteria are still MET, so the change did not break anything it was not meant to touch. It only partly fixes the user's experience, though. 
     In the before run, none of the five belt runs told the user the belt was brown. In the after run, all five did, with a check_color step right after select_item: "No black match was found, so this is the closest match instead. Its color is brown." 
```

------------------------------------------------------------------------

## What's Still Broken

```{=html}
<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->
     * The parser ignores written-out sizes: "small", "medium", and "large" are not read as sizes, so the size is silently dropped. The fix is to map those words to S, M, and L in agent.py::parse_query. I did not pick it as my improvement because no scenario in my before run used a written-out size, so I could not have measured the change against it.
     * My color warning is only in the trace. The message is stored in session["note"] and printed as a trace step, but the summary lines do not show it, and suggest_outfit and create_fit_card are not told about it, so the fit card still presents the brown belt as a great find. 
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
