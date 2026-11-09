# Data to decisions

A public, reproducible business statistics course built around one retail decision: how to reduce stockouts profitably. Ten connected lessons follow the same stores from data reconciliation through prediction, evaluation, and a staged expansion recommendation.

## This edition

One documented synthetic world contains 150 stores, 32 weeks, and a fixed monitoring basket of 140 product-days per store-week. Three disjoint cohorts supply a randomized pilot, voluntary adoption, and a later selected rollout. All lesson results share a data fingerprint. The earlier private course remains a separate edition.

The homepage begins with four questions: what is happening, what can be predicted, what would change with action, and which action is worth its cost. Each main lesson contains a decision brief, the relevant rows, a worked calculation, interpretation, an action, and an entry in the cumulative management memo. Technical continuations use the same variables and calculation. Former `lesson-N-guide.html` URLs serve the same complete lesson with a canonical main URL.

The current build uses `scripts/retail_case.py` for the data and analyses, `retail_content.py` for the running narrative, `curriculum_content.py` for the restored teaching blocks, `curriculum_worked.py` for their executable continuations, `retail_pages.py` for orientation and synthesis, and `build_retail_course.py` for rendering and labs. `curriculum_map.py` maps the substantive topics across all 1,096 slides in the ten supplied original decks. Each appendix publishes its coverage map. The previous edition's builders are no longer invoked by `build_all.py`.

## One website for reading and teaching

Choose **Present lesson** on a main lesson or technical continuation. Slides use short teaching points, charts, tables, equations, and worked code. **Notes** supplies full paragraph explanations drawn from the reading content. Notes are visible on the same screen, not a private presenter window.

Each teaching block pairs its audience cues with its explanation. `presentation_content.py` supplies concise cues for the narrative sections; the build embeds them beside the original prose in HTML templates. The browser reads both from the same lesson page, so there is no separate deck to maintain. Reading paragraphs remain available in full, including the detailed reasoning behind answer reveals. New narrative sections should have an explicit outline; prose is not automatically chopped into slide bullets.

Arrow keys, Page Up/Down, Home/End, the slide menu, and Previous/Next navigate the presentation. Escape exits. **Read this section** returns to the matching reading location. **Full screen** requests the browser's full-screen mode. **Print slides** opens a landscape print layout. A URL such as `lesson-1.html?present=1&slide=6` opens a specific slide. Presentation behavior and styling live in `static/presentation.js` and `static/presentation.css`; the build copies them into the public assets.

Original datasets and repeated code/output screenshots are replaced by worked retail examples. Core concepts, calculations, discussion exercises, and technical continuations are retained and expanded. Historical quotations and unsupported time-allocation slogans are omitted rather than presented as evidence.

Slide titles state the takeaway or the decision question, so the slide menu reads as the lesson's argument. `slide_headlines.py` authors the sequence for each lesson section; `slide_titles.py` embeds it in that same HTML and checks it against the actual visual frames. Give table and code continuations their own specific titles. Preserve discussion and known-answer questions until their reveals. The build rejects missing, duplicate, overlong, or misaligned titles.

## Reproduce

Python 3.11 or later is required for the labs. Install the tested dependency versions from requirements.txt in a virtual environment, then run:

```
python scripts/build_all.py
python scripts/check_public_release.py --execute
```

The first command builds all pages, shared CSV releases, standalone Python labs, executed notebook output, and JSON results. The second verifies cohort and timeline boundaries, numerical identities, data consistency, links, notebook/script agreement, and independent reruns of all ten labs. Small floating-point differences are compared at a stated tolerance.

The notebooks include the shared setup and a visible worked calculation. Each standalone lab includes the same generator, requires no network access, and verifies its worked result against the shared analysis. An early storyboard prototype can be built with `python scripts/build_retail_course.py --pilot` for Lessons 1, 6, and 9.

The deployed site is the prebuilt dist/ directory and needs no application server. Reading, navigation, and worked solutions remain usable without JavaScript; presentation mode is a progressive enhancement. Every quantitative chart includes a text alternative or a corresponding table.

## Publication

The GitHub Actions workflow rebuilds from source, independently reruns all ten labs, and deploys `dist/` to GitHub Pages. See PUBLISHING.md for verification steps.

## Provenance and reuse

The generated case data are original synthetic teaching examples; no third-party dataset license is needed to obtain their source observations because no third-party observations are included. This does not establish realism or empirical validity. See DATA-NOTICE.md.

Public repository visibility is not itself an open-source license. No separate reuse license for the course prose or code has been selected here. External reading links and installed software retain their own terms; their source and data are not bundled.
