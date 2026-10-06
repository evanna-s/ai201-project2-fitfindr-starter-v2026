# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->
     
My search is a keyword match. If the user describes the item differently from 
how the listing does, such as "t-shirt" instead of "tee" or "medium" instead 
of "M", the search misses it even though 
a matching listing exists. 
Two of the three tools also call the model, and a model call can fail.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->
This path must never continue: if the loop went on, suggest_outfit would 
receive nothing and the run would break. It only parses the query with regex 
and filters the listings file, with no model call,so the same query gives the 
same result every time. If it works once it works every time, so anything below 
5 of 5 means a bug.

---

## 3. The searched item is the item suggest_outfit receives

<!-- YOU WRITE THIS ONE.

     How would you know that the item your search found is the same item the
     next tool received? Name something countable or observable.

     This is the criterion people find hardest, because state failure doesn't
     look like state failure — it looks like a tool problem. Something that
     compares session["selected_item"] against what actually reached
     suggest_outfit is the shape you're after. -->
     
For 5 different queries that each match at least one listing, the id of 
session["selected_item"] is the same as the id of the new_item that 
suggest_outfit received (printed inside suggest_outfit), in 5 of 5 runs.


**Why this target:**

Listing ids are unique, so matching ids means it is the same item. Moving the 
item from the session into suggest_outfit involves no model call and no 
randomness, so it either works every time or is broken.

---

## 4. Something about the fit card

<!-- YOU WRITE THIS ONE.

     The fit card calls a model, so the same input can produce different words
     each time. That's not a bug — it's the nature of the tool. So what would
     make it acceptable?

     Think about what you'd actually be unhappy to see. A caption that never
     mentions the price? Two different items producing the same opening
     sentence? A card longer than a caption anyone would post? Any of those can
     be turned into a number. -->
     
For 5 different items, generate one fit card each. If a card mentions a price, 
it must equal the listing's price. If it mentions no price but mentions a size, 
the size must equal the listing's size. A card that mentions neither is not 
counted. Every counted card passes, 5 of 5.


**Why this target:**
The price and size are passed straight from the listing into create_fit_card, 
so the model only has to repeat them. Any wrong price or size is not acceptable. 

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. Speed, the empty
     wardrobe path, what happens when the model can't be reached, whether the
     search respects a price ceiling — anything, as long as it names a number
     or an observable outcome. -->
     
Given a query that matches at least one listing and an empty wardrobe, 
suggest_outfit returns a string that is not empty and mentions the selected 
item's title or a recognizable part of it (such as "graphic tee"), in at least 
4 of 5 tries.


**Why this target:**

This path calls the model, so the wording changes each run, and the model may 
sometimes describe the item in its own words instead of using its title.
Requiring the item's name shows the advice is about this item.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
