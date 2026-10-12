# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

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

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr helps a user search for a thrifted clothing item using a description, optional size, and maximum price. The agent searches the available listings, selects the best match, and uses the user's wardrobe to suggest one or two outfits around that item. It then creates a short social-style fit card caption describing the thrift find and how it can be styled. If no listing matches the request, the agent stops early and tells the user what they could change in their search instead of continuing with the remaining tools.

---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the available clothing listings using the user's description, requested size, and maximum price. Results are ranked by keyword overlap with `description`, highest score first.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None). `max_price` is inclusive. If `size` or `max_price` is `None`, that filter is skipped. Size matching is case-insensitive and uses complete size tokens, so `M` can match `M`, `S/M`, or `M/L`, but not `XL` or `US 9`. I will treat `One Size` as matching any requested size.
- **Returns:** Up to `config.SEARCH_RESULT_LIMIT` matching listing dictionaries, best match first. Listings scoring 0 for keyword overlap are excluded. Each dictionary contains `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price` (float), `colors`, `brand` (str or None), and `platform`.
- **When it has nothing:** Returns an empty list `[]`.

### `suggest_outfit`

- **What it does:** Takes the selected thrift listing and the user's wardrobe and suggests one or two outfits using the new item with pieces the user already owns.
- **Inputs:** `new_item` (dict), `wardrobe` (dict containing an `items` list).
- **Returns:** A non-empty string containing one or two outfit suggestions. When the wardrobe is not empty, each suggestion names specific wardrobe pieces by their `name` and explains why they work with the new item.
- **When it has nothing:** If `wardrobe["items"]` is empty, returns general styling advice for the new item instead of raising an error or returning an empty string.

### `create_fit_card`

- **What it does:** Creates a short social-style caption about the selected thrift item and suggested outfit. It must not assume that the listing has a brand.
- **Inputs:** `outfit` (str), `new_item` (dict). `new_item["brand"]` may be `None`.
- **Returns:** A 2–4 sentence caption that mentions the item, its price, and its platform once each and describes the outfit's vibe.
- **When it has nothing:** If `outfit` is empty or contains only whitespace, returns `"Couldn't write a fit card — no outfit suggestion was provided."` without calling the model.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in
the session and stop. Otherwise, take the first result and go to
`suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** <!-- regex, string splitting, or asking the model — say which -->
`agent.py::parse_query` uses regular expressions to extract `size` and `max_price`. The remaining non-filler words are used as the description.

**What moves through the session:** <!-- which fields, in what order -->
The user's query and wardrobe are stored when the session is created. After parsing, `description`, `size`, and
`max_price` are stored in `session["parsed"]`. The results from
`search_listings` go into `session["search_results"]`, the first result becomes
`session["selected_item"]`, the result from `suggest_outfit` goes into
`session["outfit_suggestion"]`, and the result from `create_fit_card` goes into
`session["fit_card"]`. If the search returns no results, an explanation is
stored in `session["error"]` and the run stops.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Y2K Street
- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag
This balances the fitted crop of the tee with relaxed denim and chunky streetwear sneakers for a classic 2000s proportion.

Retro Contrast
- Y2K Baby Tee — Butterfly Print
- Wide-leg khaki trousers
- Vintage black denim jacket
- Black combat boots
The edgy black outerwear and boots ground the sweet pastel butterfly print for an easy high-low mix.

  Fit card: Scored this adorable Y2K butterfly baby tee on depop for just $18 and I am obsessed. I am styling it with wide-leg khaki trousers, a vintage black denim jacket, and black combat boots for such a cool retro contrast look. The edgy black outerwear and boots really ground the sweet pastel print.

2 model calls this session, 790 prompt + 180 output tokens

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}]

```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

Outfit 1: Classic Streetwear
- Vintage Levi's 501 Jeans — Medium Wash
- White ribbed tank top
- Oversized grey crewneck sweatshirt
- Chunky white sneakers
- Black crossbody bag
Layering the oversized grey crewneck sweatshirt over the white ribbed tank top creates a balanced, comfortable silhouette when paired with the medium-wash vintage denim and chunky white sneakers.

Outfit 2: Double Denim Edge
- Vintage Levi's 501 Jeans — Medium Wash
- White ribbed tank top
- Vintage black denim jacket
- Black combat boots
- Brown leather belt
Tucking the white ribbed tank top into the vintage Levi's 501 jeans with the brown leather belt anchors the look, while the cropped vintage black denim jacket and black combat boots add sharp contrast.

```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Scored these vintage Levi's 501 jeans on depop for only $38 and they fit like an absolute dream. The medium wash and subtle knee fading give them such an effortless street style edge. Paired them with crisp white sneakers for the ultimate casual weekend uniform.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- _What I asked for:_ I asked Claude to implement `create_fit_card` from my Tool Inventory contract: a 2–4 sentence caption mentioning the item, price, and platform once each.
- _What came back:_ A working prompt, but testing with the cache off showed one caption wrote the price as "thirty-eight dollars" instead of `$38`, which would fail Criterion 4.
- _What I changed:_ I changed the prompt to require the price as digits in the exact `$38` format. The next five test runs all contained the price in that format.

**Moment 2**

- _What I asked for:_ After the price fix, I tested more items to check that the captions read like a real post.
- _What came back:_ One caption for the Y2K Baby Tee said "I just listed it on depop" as if the poster were selling the item.
- _What I changed:_ I added a rule to the prompt stating that the poster bought the item and is not selling it. Three more runs on the same item all described it as a purchase.

**Moment 3**

- _What I asked for:_ I asked AI to help me review the Unit 4 test results and compare the before and after runs.
- _What came back:_ It pointed out that all five acceptance criteria stayed at 5 of 5, so there was no numerical score improvement, but the exact-title behavior in `create_fit_card` became more consistent.
- _What I changed:_ I kept the acceptance criteria and scores unchanged, documented the prompt change as a qualitative improvement, and wrote that the existing criteria were already at the ceiling instead of claiming a score increase.

---

## Stretch Feature — Fourth Tool

### `compare_prices`

- **What it does:** Compares the selected listing's price with the prices of the _other_ listings `search_listings` returned. It does not call the model.
- **Inputs:** `selected_item` (dict), `search_results` (list[dict]). The selected item is left out of the average by its `id`.
- **Returns:** A dict with `selected_price` (float), `average_price` (float), `difference` (float, selected minus average), `position` (`"below"`, `"equal"`, or `"above"`), `compared_with` (int, how many listings were averaged), and `summary` (a one-sentence str).
- **When it has nothing:** If the search returned only the selected item, `position` is `"no comparison"`, `average_price` and `difference` are `None`, and `compared_with` is `0`. It does not raise.

**Where it runs:** `agent.py::run_agent` calls it after choosing `session["selected_item"]` and before `suggest_outfit`. The result is stored in `session["price_comparison"]`. On the empty-search path it never runs, because the loop stops first.

**A run where the agent called it**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop
  Price:    $18.00 — $3.33 below the $21.33 average of 9 other matches.

  Outfit:   Y2K Street
- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag
...
```

**The empty case**

```
$ python app.py ask 'jeans size W30'

  Found:    Vintage Levi's 501 Jeans — Medium Wash — $38.0 on depop
  Price:    $38.00 — no other matching listings to compare against.
```

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion                                      | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict       |
| ---------------------------------------------- | -----: | ----- | ----- | ----- | ----- | ----- | ------------- |
| 1. Matching query completes all three tools    | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 2. Impossible query stops before second tool   | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 3. Selected item carries through session state | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 4. Fit card contains required item details     | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 5. Search respects maximum price               | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
Produced by: `run_eval.py::main`
Agent loop: `agent.py::run_agent`

- Query: `vintage graphic tee under $30`
- Wardrobe: example

**Try 1**

- stopped early: no
- selected_item: Y2K Baby Tee — Butterfly Print ($18.0, depop)
- search_results: 10

Outfit suggestion:

```

Y2K Street

- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag
  It balances the fitted, feminine tee with relaxed denim and streetwear accessories.

Grunge Contrast

- Y2K Baby Tee — Butterfly Print
- Vintage black denim jacket
- Wide-leg khaki trousers
- Black combat boots
  It anchors the sweet butterfly print with edgy outerwear and chunky footwear.

```

Fit card:

```

I finally scored this adorable Y2K baby tee on Depop for just $18 and I am obsessed with the butterfly print. For a grunge contrast look, I paired it with a vintage black denim jacket, wide-leg khaki trousers, and chunky black combat boots to anchor the sweet graphic. It is the ultimate mix of feminine and edgy for everyday wear.

```

Trace:

```

[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ results found, continuing
[2] compare_prices
in: dict with keys: selected_item, search_result_count
out: $18.00 — $3.33 below the $21.33 average of 9 other matches.
[3] suggest_outfit
in: dict with keys: new_item, wardrobe_items
out: Y2K Street - Y2K Baby Tee — Butterfly Print - Baggy straight-leg jeans, dark wash - Chunky white sneakers - Bl…
[4] create_fit_card
in: dict with keys: new_item, outfit
out: I finally scored this adorable Y2K baby tee on Depop for just $18 and I am obsessed with the butterfly print. …

```

---

## Verdicts and Diagnoses

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

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | Matching query completes all three tools | 4 of 5 | MET (5/5) | All five tries completed the successful path and produced a fit card. |
| 2 | Impossible query stops before the second tool | 5 of 5 | MET (5/5) | All five tries returned no search results, stopped before `suggest_outfit`, and returned a useful message. |
| 3 | Selected item carries through session state | 4 of 5 | MET (5/5) | All five tries kept the selected item consistent through the session and into `suggest_outfit`. |
| 4 | Fit card contains the required item details | 4 of 5 | MET (5/5) | All five fit cards were 2–4 sentences and included the selected item's price and platform. |
| 5 | Search respects the maximum price | 5 of 5 | MET (5/5) | All five tries returned only listings at or below the requested maximum price. |

**Diagnoses**

No criteria were missed in the before run, so there are no failed steps or failure mechanisms to diagnose.

The target I would tighten is Criterion 3. I originally set it to 4 of 5 because the tool chain contains model-generated output later in the run.
However, the criterion itself only checks whether the selected item's `id` moves correctly through session state into `suggest_outfit`.
That state transfer is deterministic and does not depend on the model, so a stricter target of 5 of 5 would better match the behavior being measured.
---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

$ python app.py ask 'vintage graphic tee under $30' --trace

[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ results found, continuing
[2] compare_prices
in: dict with keys: selected_item, search_result_count
out: $18.00 — $3.33 below the $21.33 average of 9 other matches.
[3] suggest_outfit
in: dict with keys: new_item, wardrobe_items
out: Y2K Street - Y2K Baby Tee — Butterfly Print - Baggy straight-leg jeans, dark wash - Chunky white sneakers - Bl…
[4] create_fit_card
in: dict with keys: new_item, outfit
out: Scored this adorable Y2K butterfly baby tee on depop for just $18 and I am obsessed. I am styling it with wide…

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
Price: $18.00 — $3.33 below the $21.33 average of 9 other matches.

Outfit: Y2K Street

- Y2K Baby Tee — Butterfly Print
- Baggy straight-leg jeans, dark wash
- Chunky white sneakers
- Black crossbody bag
  This balances the fitted crop of the tee with relaxed denim and chunky streetwear sneakers for a classic 2000s proportion.

Retro Contrast

- Y2K Baby Tee — Butterfly Print
- Wide-leg khaki trousers
- Vintage black denim jacket
- Black combat boots
  The edgy black outerwear and boots ground the sweet pastel butterfly print for an easy high-low mix.

  Fit card: Scored this adorable Y2K butterfly baby tee on depop for just $18 and I am obsessed. I am styling it with wide-leg khaki trousers, a vintage black denim jacket, and black combat boots for such a cool retro contrast look. The edgy black outerwear and boots really ground the sweet pastel print.

0 model calls this session, 2 served from cache

```

**Empty search**

```

$ python app.py ask 'designer ballgown size XXS under $5' --trace

[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: [] (empty)
→ branch: empty search, stopping

No listings matched. Try: raise your price limit above $5; or drop the size filter (XXS); or use broader words than "designer ballgown".

0 model calls this session

```

## Failure Mode Checks

**Empty search**

```

$ python app.py ask 'designer ballgown size XXS under $5'
[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: [] (empty)
→ branch: empty search, stopping

No listings matched. Try: raise your price limit above $5; or drop the size filter (XXS); or use broader words than "designer ballgown".

0 model calls this session

```

**Empty Wardrobe**

```

$ python app.py ask 'vintage graphic tee under $30' --empty-wardrobe
[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ results found, continuing
[2] compare_prices
in: dict with keys: selected_item, search_result_count
out: $18.00 — $3.33 below the $21.33 average of 9 other matches.
[3] suggest_outfit
in: dict with keys: new_item, wardrobe_items
out: 1. Retro Street - Straight-leg light wash jeans - White platform sneakers - Small black shoulder bag Why it wo…
[4] create_fit_card
in: dict with keys: new_item, outfit
out: Scored this adorable Y2K butterfly baby tee on Depop for just $18 and I am obsessed. I am leaning into the ret…

Found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
Price: $18.00 — $3.33 below the $21.33 average of 9 other matches.

Outfit: 1. Retro Street

- Straight-leg light wash jeans
- White platform sneakers
- Small black shoulder bag
  Why it works: Balances the fitted, girly top with relaxed denim for an effortless everyday look.

2. Y2K Grunge

- Black pleated mini skirt
- Knee-high black boots
- Silver chain necklace
  Why it works: The edgy skirt and boots tone down the sweetness of the butterfly print.

  Fit card: Scored this adorable Y2K butterfly baby tee on Depop for just $18 and I am obsessed. I am leaning into the retro street vibe today by pairing itwith relaxed straight-leg jeans and white platform sneakers. It balances the fitted, girly print with casual denim for the ultimate everyday look.

0 model calls this session, 2 served from cache

```

**Model Unavailable (API Failed)**

```

python app.py ask 'vintage graphic tee under $30' --trace
[1] search_listings (via MCP)
in: dict with keys: description, size, max_price
out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
→ results found, continuing
[2] compare_prices
in: dict with keys: selected_item, search_result_count
out: $18.00 — $3.33 below the $21.33 average of 9 other matches.
[3] suggest_outfit
in: dict with keys: new_item
out: ModelUnavailable
→ model unavailable, stopping

The styling model couldn't be reached. Check your API key and network connection. If the problem persists, try again later.

1 model calls this session

```

**On the MCP move:**
I moved `search_listings` from a direct Python function call in `agent.py` to an MCP tool registered in `mcp_server.py`.
`run_agent` now calls it through `mcp_client.call_tool`, while the inputs and returned list of listing dictionaries stayed the same. After the rewire, the happy path and empty-search path behaved the same as before; the trace now shows `search_listings (via MCP)` as the first tool call.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**
I tightened the `create_fit_card` prompt so that it now requires the selected listing's exact title to appear once in the caption. Previously, the prompt only required the caption to mention the item, which allowed the model to refer to it more generally.

**Which failure it was meant to fix:**
None of my five acceptance criteria missed in the before run.
This change was meant to make the fit card more clearly grounded in the exact listing selected by the agent.
Criterion 4 already passed 5 of 5, so its score may remain the same even if the captions become more specific.

### Before vs. After

| Criterion | Before | After | Change |
|---|---:|---:|---|
| 1. Matching query completes all three tools | 5/5 | 5/5 | No score change |
| 2. Impossible query stops before second tool | 5/5 | 5/5 | No score change |
| 3. Selected item carries through session state | 5/5 | 5/5 | No score change |
| 4. Fit card contains required item details | 5/5 | 5/5 | No score change |
| 5. Search respects maximum price | 5/5 | 5/5 | No score change |

### Run Log — After

| Criterion                                      | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict       |
| ---------------------------------------------- | -----: | ----- | ----- | ----- | ----- | ----- | ------------- |
| 1. Matching query completes all three tools    | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 2. Impossible query stops before second tool   | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 3. Selected item carries through session state | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 4. Fit card contains required item details     | 4 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |
| 5. Search respects maximum price               | 5 of 5 | PASS  | PASS  | PASS  | PASS  | PASS  | **MET — 5/5** |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->
The acceptance criterion scores stayed the same.
All five criteria were 5 of 5 before and 5 of 5 after.
The before run was already at the maximum score, so the existing criteria could not show a numerical improvement.

However, the specific behavior I changed did improve.
Before the prompt change, `create_fit_card` often referred to the selected item with a shortened or generic name, such as `Vintage Levi's 501 jeans`
After requiring the exact listing title, all five Criterion 4 runs included `Vintage Levi's 501 Jeans — Medium Wash` in the fit card.

So the change improved how clearly the generated caption is grounded in the selected listing, even though Criterion 4 remained MET at 5/5 before and after.

---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->
None of the five acceptance criteria are still missed after the improvement run.
All five criteria remained MET at 5 of 5.

The main limitation I would continue working on is outside the current acceptance criteria: the fit-card prompt can still produce stylistic variation even when it follows the required structure.
I stopped here because the assignment asks for one measured improvement, and the current criteria are already satisfied.

## Unit 4 Stretch Features

I plan to add the following stretch features before implementing them:

1. **Second MCP tool:** Move `compare_prices` behind MCP so both `search_listings` and `compare_prices` are called through the MCP client.

2. **Retry with looser constraints:** If a search with a size filter returns no results, retry once without the size filter and tell the user which constraint was removed.

3. **Second measured improvement:** I will make one additional change based on the evaluation results and measure it with a third full evaluation run.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [x] criteria.md has five numbered criteria, each with a target
       [x] Each criterion has a reason underneath it
       [x] All five unit 3 sections above have real content
       [x] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [x] Planning Loop names the branch rule and agent.py::run_agent
       [x] Sample Run: one full query plus the three per-tool tests, as text
       [x] At least four new commits
       [x] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [x] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [x] Run Log — Before, five criteria, five tries each
       [x] Real output pasted underneath, naming file and function
       [x] A verdict on every criterion
       [x] A diagnosis for every miss, naming a place AND a mechanism
       [x] Loop Trace, with the MCP call visible in it
       [x] All three failure modes triggered and handled
       [x] One improvement, with Run Log — After in the same format
       [x] What's Still Broken
       [x] At least four new commits
       [x] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
```
