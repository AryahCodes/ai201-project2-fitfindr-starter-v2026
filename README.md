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

FitFindr is a secondhand shopping assistant. You type a plain-language query like
`vintage graphic tee under $30`, and the agent searches mock thrift listings,
picks the best match, suggests one or two outfits using your saved wardrobe,
and writes a short caption you could post about the find.

If the search finds nothing, the agent stops early and tells you what to try
changing (size, price limit, or keywords). It does not call the outfit or fit
card tools on an empty search.

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

- **What it does:** Loads the listings dataset with `load_listings()` and returns items whose title, description, and style tags overlap with the user's keywords. Optionally filters by size (case-insensitive match on size tokens, so `"M"` matches `"S/M"` but `"s"` does not match `"US 9"`) and by max price (inclusive). Scores what's left, drops zero-score matches, sorts best-first, and caps at 10 results.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A `list[dict]`. Each dict is one listing with keys: `id`, `title`, `description`, `category`, `style_tags` (list of str), `size`, `condition`, `price` (float), `colors` (list of str), `brand` (str or None), `platform` (str). Best match first, at most 10 items.
- **When it has nothing:** An empty list `[]`, not `None` and not an exception.

### `suggest_outfit`

- **What it does:** Takes the listing the user is considering and their wardrobe, then asks the model for one or two outfit ideas. If the wardrobe is empty, it asks for general styling advice for the item instead of naming pieces the user owns.
- **Inputs:** `new_item` (dict, a listing dict from search), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts)
- **Returns:** A non-empty `str` with outfit suggestions or general styling advice.
- **When it has nothing:** It should still return a non-empty string (general styling advice when `wardrobe["items"]` is empty). It does not return `""` or raise.

### `create_fit_card`

- **What it does:** Turns the outfit suggestion and listing into a short caption someone would actually post. Mentions the item, price, and platform, and reads like a real thrift find post rather than a product listing.
- **Inputs:** `outfit` (str, the string from `suggest_outfit`), `new_item` (dict, the same listing dict)
- **Returns:** A `str` caption, usually two to four sentences.
- **When it has nothing:** If `outfit` is empty or only whitespace, returns a descriptive fallback message string instead of raising or returning `""`.

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

**Branch rule:** In `agent.py::run_agent`, if `search_listings` returns an empty list, save a useful message in `session["error"]` (naming size, price, or keywords the user could change), leave `session["fit_card"]` as `None`, and return without calling `suggest_outfit` or `create_fit_card`. Otherwise save the first result in `session["selected_item"]`, read it back from session for `suggest_outfit`, save the outfit in `session["outfit_suggestion"]`, read that back for `create_fit_card`, and save the caption in `session["fit_card"]`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex in `_parse_query()`. It pulls out `max_price` from phrases like "under $30", `size` from "size M" or "size S/M", and uses whatever text is left as the search description. The parsed values go in `session["parsed"]`.

**What moves through the session:** `parsed` → `search_results` → (branch) → `selected_item` → `outfit_suggestion` → `fit_card`. On the empty-search path, only `parsed`, `search_results`, and `error` are set; `selected_item`, `outfit_suggestion`, and `fit_card` stay `None`.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   **Outfit 1: Y2K Streetwear Contrast**
Pair the butterfly baby tee with your **baggy straight-leg dark wash jeans** to balance the cropped, fitted silhouette. Throw on the **vintage black denim jacket** over top and finish with your **chunky white sneakers** and the **black crossbody bag**. 

**Outfit 2: Casual Earth-Tone Mix**
Tuck the baby tee into your **wide-leg khaki trousers**, secured with the **brown leather belt** to pull the pink and purple graphic tones together with the tan. Slip on your **black combat boots** to add a little edge to the softer cottagecore-Y2K vibe, and wear the **black cropped zip hoodie** unzipped over your shoulders if you need an extra layer.

  Fit card: Obsessed with the pink and purple butterfly print on this Y2K baby tee. It's giving total early 2000s daydream, especially styled with baggy dark wash denim or tucked into khaki trousers for that sweet-meets-edgy vibe. Grab it on my Depop for just $18 before I change my mind and keep it.

0 model calls this session, 2 served from cache
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

[{'id': 'lst_002', 'title': 'Y2K Baby Tee — Butterfly Print', 'description': 'Super cute early 2000s baby tee with butterfly graphic. Fitted crop length. Tag says medium but fits like a small.', 'category': 'tops', 'style_tags': ['y2k', 'vintage', 'graphic tee', 'cottagecore'], 'size': 'S/M', 'condition': 'excellent', 'price': 18.0, 'colors': ['white', 'pink', 'purple'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee with faded graphic. Slightly boxy fit. 100% cotton, soft and worn-in.', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_017', 'title': 'Mesh Long-Sleeve Top — Black', 'description': 'Sheer black mesh long-sleeve. Great for layering under a graphic tee or over a bralette. Stretchy material, fits true to size.', 'category': 'tops', 'style_tags': ['y2k', 'grunge', 'goth', 'layering'], 'size': 'S/M', 'condition': 'excellent', 'price': 15.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_033', 'title': 'Vintage Band Tee — Faded Grey', 'description': 'Faded grey band-style tee with distressed graphic. Crew neck. Fits boxy. Well-loved but no holes or major damage.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'band tee', 'graphic tee', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 19.0, 'colors': ['grey', 'charcoal'], 'brand': None, 'platform': 'depop'}, {'id': 'lst_011', 'title': 'Low-Rise Cargo Pants — Khaki', 'description': 'Y2K era low-rise cargo pants. Lots of pockets. Khaki color, slightly distressed at the hems. Great for layering with a long tee.', 'category': 'bottoms', 'style_tags': ['y2k', 'cargo', '2000s', 'streetwear'], 'size': 'W29', 'condition': 'fair', 'price': 27.0, 'colors': ['khaki', 'tan'], 'brand': None, 'platform': 'poshmark'}, {'id': 'lst_012', 'title': 'Oversized Crewneck Sweatshirt — Vintage Navy', 'description': 'Perfectly faded navy crewneck. Genuinely vintage — not manufactured distressed. Ribbed cuffs and hem. No graphics, clean.', 'category': 'tops', 'style_tags': ['vintage', 'basics', 'oversized', 'classic'], 'size': 'XL (fits oversized)', 'condition': 'good', 'price': 20.0, 'colors': ['navy'], 'brand': None, 'platform': 'thredUp'}, {'id': 'lst_015', 'title': 'Vintage Graphic Hoodie — Faded Black', 'description': 'Faded black pullover hoodie with barely-visible vintage graphic on the chest. Cozy interior. Some pilling but adds to the worn-in look.', 'category': 'tops', 'style_tags': ['vintage', 'grunge', 'graphic', 'streetwear'], 'size': 'L', 'condition': 'fair', 'price': 26.0, 'colors': ['black', 'charcoal'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"

**Buy them.** Vintage 501s in a medium wash are a lifetime staple that will anchor your existing wardrobe. 

Here are two outfits using pieces you already own:

**Outfit 1: Effortless Casual (Streetwear/Minimal)**
*   **Top:** White ribbed tank top
*   **Bottoms:** Vintage Levi's 501 Jeans (Medium Wash)
*   **Outerwear:** Vintage black denim jacket
*   **Shoes:** Chunky white sneakers
*   **Accessories:** Black crossbody bag + Brown leather belt 
*   *Why it works:* The fitted white tank balances the straight leg of the 501s, and the black denim jacket creates a cool, double-denim contrast against the medium wash.

**Outfit 2: Cozy Layered (Streetwear/Cozy)**
*   **Top:** Oversized grey crewneck sweatshirt (worn layered over the white ribbed tank)
*   **Bottoms:** Vintage Levi's 501 Jeans (Medium Wash)
*   **Shoes:** Black combat boots
*   **Accessories:** Brown leather belt (cinched at the waist with the jeans showing beneath the sweatshirt)
*   *Why it works:* The chunky combat boots ground the relaxed proportions of the oversized crewneck and classic straight-leg denim.

```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"

Nothing beats the fit of broken-in vintage Levi's 501s. These have that perfect medium wash and effortless streetwear vibe for just $38. Throw them on with crisp white sneakers and you're good to go. Grab them on my depop before I change my mind and keep them.

```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* Help drafting the Tool Inventory and three acceptance criteria in `criteria.md` from the starter docstrings and listing schema.
- *What came back:* Specs for each tool's inputs, return shape, and empty case, plus criteria about session state (`selected_item` id matching), fit card mentioning price/platform, and search respecting the price ceiling.
- *What I changed:* Kept the empty-search return as `[]` instead of `None` because that is what the loop branches on. Tightened the size-matching description after reading actual sizes in `listings.json` (like `US 9` and `S/M`).

**Moment 2**

- *What I asked for:* Help implementing `search_listings` and wiring `run_agent()` so values flow through session state.
- *What came back:* Keyword scoring over title/description/style_tags, a `_size_matches()` helper to avoid single-letter false positives, and reading `session["selected_item"]` and `session["outfit_suggestion"]` back out before each next tool call.
- *What I changed:* Ran the per-tool terminal tests myself to confirm size `S` does not match shoe listings, and ran `python agent.py` to check that the impossible query stops with `fit_card` still `None`.

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

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

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
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



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

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



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

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
