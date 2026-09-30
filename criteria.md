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

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. The selected item reaches suggest_outfit unchanged

On a matching query, `session["selected_item"]["id"]` is the same `id` passed
into `suggest_outfit` as `new_item` — in 5 of 5 tries.

**Why this target:** This path is straight-through (search → pick first result →
suggest), so there is no reason for the id to drift. I picked 5 of 5 because
if the wrong listing reaches the model, everything downstream looks broken even
when the tools themselves work.

---

## 4. The fit card mentions price and platform

On a matching query, the fit card string contains both the item's price (as
shown in the listing, e.g. `$24`) and its platform name (depop, thredUp, or
poshmark) — in at least 4 of 5 tries.

**Why this target:** The model can word things differently each run, but price
and platform are in every listing dict and the prompt asks for them. Missing
both on more than one try would mean the card isn't grounded in the data. I
didn't require 5 of 5 because wording can vary (e.g. "$24" vs "24 dollars").

---

## 5. Search respects the price ceiling

When the query includes a max price, every listing in `session["search_results"]`
has `price <= max_price` — in 5 of 5 tries.

**Why this target:** Price filtering is plain numeric comparison with no model
involved, so it should never slip. Criterion 1 already tests the happy path
end-to-end; this checks that the search layer actually honors what the user
asked for.



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
