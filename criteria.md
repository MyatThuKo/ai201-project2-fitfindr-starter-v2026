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

4 of 5 because `search_listings` uses keyword matching rather than a semantic model. A valid request could be phrased differently from the words in the listing data and miss the search even though a relevant item exists. If a match is found, I still expect the rest of the tool chain to complete normally.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**

5 of 5 because this branch is deterministic. `run_agent` should always stop before calling `suggest_outfit` and store a useful message in `session["error"]` when `search_listings` returns an empty list. Unlike the successful path, this decision does not depend on model-generated output, so I expect it to work every time.

---

## 3. The selected item carries through session state

Given a query that returns at least one listing, the `id` in the `session["selected item"]` should match the `id` of the item passed into `suggest_outfit` - in at least 4 of 5 tries.

**Why this target:**
The agent is supposed to move the item found by `search_listings` through session state instead of asking the user for it again. I chose 4 out of 5 because the tool chain includes the model-generated output later, but the selected item iteself should normally remain consistent.

---

## 4. The fit card contains the required item details

Given a successful run, the fit card should be 2-4 sentences and mention the selected item's price and platform - in at least 4 of 5 tries.

**Why this target:**

`create_fit_card` calls the model, and I do not expect the wording to be the same every run. I chose observable requirements that can still be checked even when the model phrases the different caption.

---

## 5. Search respects the maximum price

Given a query with a maxmium price, every listing returned by `search_listings` should have a price less than or equal to that maximum - in 5 of 5 tries.

**Why this target:**

`max_price` filters the listing's `price` field directly and is inclusive. The project data does not include taxes, shipping, or checkout fees, so the criterion measures the listed price only and before adding those additional costs.

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
