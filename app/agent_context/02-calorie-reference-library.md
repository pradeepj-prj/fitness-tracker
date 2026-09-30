# 02 — Calorie Reference Library

**This is the most valuable non-data artifact in the bundle.** It is the accumulated estimation
knowledge built up between 2026-05-14 and 2026-09-30, consolidated from the source agent's
`MEMORY.md` and ~20 daily memory files. It existed nowhere else — not in the code, not in the
database.

Without it, a replacement agent's estimates will drift from the 603 historical entries and the
dataset stops being internally comparable. **Load it into the new agent's persistent memory**,
not just a context window.

**How to use it:** a user-provided label or weighed gram amount always wins. Then a matching
reference below. Then an API lookup. Then a conservative guess. Where two versions of a
reference exist, both are kept deliberately — the older one explains older entries; use the
newer one for new logging unless the user names the old pack.

---

## Drinks

| Item | Estimate | Provenance |
|---|---|---|
| Tea / chai (default) | **90 cal** per serving | measured recipe, revised 2026-07-14 |
| Chai batch | 254g water + 197g milk + 2 tbsp sugar + ginger, cardamom, tea leaves → ~181 cal, split into 2 servings = ~90 cal each | milk costed at 43 kcal/100g (2026-07-14 revision; the earlier figure was ~225 cal/batch, ~112 cal/serving — superseded) |
| Teh ping | **~120 cal** | 2026-09-15 |
| Filter coffee | ~84 cal | entry average |
| Cold coffee | ~180 cal | entry average |
| Buttermilk | **60 cal** | 2026-09-20 |
| Tiger pint | ~220 cal each (1.5 pints logged as 330) | 2026-09-23 |

## Bread, biscuits, snacks

| Item | Estimate | Provenance |
|---|---|---|
| Bread / toast | **2 slices = 137 cal; 1 slice = ~69 cal** | current, 2026-07-17 |
| ⤷ superseded | 2 slices = 163 cal (72g, 13.1g protein), 1 slice ~81.5 cal | 2026-06-04, replaced |
| Butter toast | ~240 cal; half ~120 cal | 2026-09-13 |
| Butter | 5g = ~36 cal; 14g = ~100 cal | 2026-09-13 |
| **Digestive biscuit** | **1 = 16g = 76 cal; 2 = 152 cal** (474 cal/100g) | confirmed repeatedly Sept 2026 |
| **Plain biscuit** | **139–140 cal per 9 biscuits** → ~15-16 cal each, 2 = ~31 cal, 3 = ~47 cal | separate pack, still valid when she names it |
| ⚠️ | These two differ **5×**. Clarify which biscuit if ambiguous. | |
| Cheese biscuits | ~137 cal (entry average) | data |
| Muruku | **~105 cal each** when no weight given | default |
| Butter muruku (by label) | 3756 kJ/100g ≈ **898 cal/100g** → 10g ≈ 90 cal, 5g ≈ 33 cal | label, 2026-09-22 |
| Banana chips | **28g = 140 cal** (5 cal/g) → 15g = 75, 13g = 65, 8g = ~40 | 2026-09-22 |
| Bhujia | **~603 cal/100g** | MEMORY.md |
| Chips | 37g = 200 cal | 2026-09-24 |

## Fruit

| Item | Estimate |
|---|---|
| Banana | ~105 cal |
| Apple | ~95 cal (small apple ~55) |
| Kiwi | ~42 cal · **gold kiwi ~55 cal** |
| Grapefruit | ~99 cal |
| Blackberries | ~43 cal / 100g |
| Mangosteen | ~73 cal / 100g flesh |
| Baby Thai pineapple | 3 small = 45 cal |

## Packaged / branded

| Item | Estimate | Provenance |
|---|---|---|
| **Baked beans** (current label) | full 220g can/serving = 825 kJ = **~197 cal**; half ~99; 100g ~90 | 2026-09-15 |
| ⤷ superseded | 207g = 136 cal | older, kept for old entries |
| Four Leaves little garlic roll | **~85 cal each**; 2 = ~170 | 2026-09-13 |
| Nature Veg Hong Kong style noodles | **189g portion = ~300 cal**; half extra = +150; half *medium* portion ~270 | 2026-09-13/14 |
| Mushroom soup (small) | **~97 cal**; Campbell's ref also used ~95 | 2026-09-16 |
| Coconut chutney (small) | ~45 cal | 2026-09-14 |
| Sundal / chickpea + coconut | 65g = ~115 cal | 2026-09-20 |
| Birthday cake | **~320 cal/100g** → 150g = 480 | 2026-09-22 |
| Claypot rice | **~200 cal/100g** unless portion/leftovers correct it → 220g = 440 | 2026-09-29 |

## Eating out

| Item | Estimate | Provenance |
|---|---|---|
| VeganBurg | burger ~550 + fries ~300 = **~850 cal** | 2026-09-20 |
| Food-court half rice + greens + fried tofu + Thai green curry | **~410 cal** | 2026-09-20 |
| South Indian thali (100g rice, sambhar, rasam, alu sabzi, beans/dal sabzi, 2 medu vada, 2 applam, small kheer) | **~940 cal** | 2026-09-22 |
| Tom yum soup | ~140 cal (half ~70); + 50g rice (~65) = 205 | 2026-09-22 |
| Half tom yum + half medium HK noodles | **360 cal total** (revised up from an earlier lower figure) | 2026-09-13 |
| Shroomami bowl w/ soba (Knead) | 560 cal | 2026-09-30 |
| Paris Baguette petite cake | half = 220 cal | 2026-09-30 |

## Batch recipes — the core of the method

Compute the batch once from weighed raw ingredients, then log fractions.

| Batch | Ingredients | Full batch | Portion |
|---|---|---|---|
| **Poha** | 22g oil + 139g dry poha + 1 large onion + 125g boiled potato + 15g groundnut + 1 medium tomato + 1/5 capsicum | **~941 cal** | just under ½ + tea logged as 513 |
| **Upma** | 125g sooji + 9g ghee + 1 medium tomato + ½ carrot + ¼ capsicum | **~573 cal** | ½ = ~287; ½ + tea = **377**; + chutney = 422 |
| **Paneer bhurji** | 9g olive oil + 1 large onion + 1 medium tomato + ¼ capsicum + 200g paneer | **~688 cal** | ¼ = **~172 cal** |
| **Paneer sabzi** | 21g olive oil + 1 medium onion + 2.5 tomatoes + 10g tomato paste + 15g cashews + 400g paneer | **~1441 cal** | ⅙ = **~240 cal** |
| **Dal + rice (khichdi)** | 1 small cup each toor/moong/chana dal + 2 tsp ghee + 1 cup raw rice | **~1125 cal** | ⅓ = **~375 cal** ("dal khichdi same as last time") |
| **Bhindi** | 350g bhindi + 15g olive oil + 1 medium onion + ½ boiled medium potato | **~349 cal** | ⅓ = **~116 cal** |
| **Rajma** | 1 large onion + 3 large tomatoes + 20g olive oil + 209g rajma + 1 tbsp tomato puree | **~565 cal** (rice separate) | 2026-07-28 |
| **Burger patties** | 240g rajma (89 cal/100g) + 10g cornflour + 108g paneer | **~535 cal / 4 patties** | ~134 each before oil |
| **Air-fried potatoes** | 279g potato | **~215 cal** before oil | 10g olive oil across patties+potatoes → half consumed adds ~45 |
| **Tahini sauce** | 20g tahini + 40g yoghurt + mustard | **~150 cal** | half = ~75 |

## Tare container weights (for gross-weight portions)

Recorded 2026-06-21 — subtract these when she gives a bowl/pot weight including the container.

| Container | Tare |
|---|---|
| black pot | 1292 g |
| pressure cooker | 939 g |
| big steel bowl | 212 g |
| medium steel bowl | 160 g |
| small steel bowl | 117 g |
| blue cup | 404 g |
| IKEA glass | 254 g |

## Most-logged foods (frequency, from the data — useful for autocomplete)

`tea` ×11 · `1 grapefruit` ×7 · `1 teh ping` ×5 · `1 kiwi` ×5 · `1 filter coffee` ×5 ·
`cold coffee` ×4 · `chai` ×4 · `apple` ×4 · `1 tea` ×4 · `1 small apple` ×4 ·
`cheese biscuits` ×3 · `1 muruku` ×3 · `1 biscuit` ×3 · `1 banana` ×3

> Note the near-duplicate names (`tea` / `1 tea` / `chai`). `food_name` is free text with no
> normalisation. Worth adding a canonical-name layer in the new home — but **do not rewrite
> historical rows**; map at read time instead.
