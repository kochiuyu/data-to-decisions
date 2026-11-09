# Data to decisions

A public, reproducible business statistics course built around one retail decision: how to reduce stockouts profitably. Ten connected lessons follow the same stores from data reconciliation through prediction, evaluation, and a staged expansion recommendation.

## This edition

One documented synthetic world contains 150 stores, 32 weeks, and a fixed monitoring basket of 140 product-days per store-week. Three disjoint cohorts supply a randomized pilot, voluntary adoption, and a later selected rollout. All lesson results share a data fingerprint. The earlier private course remains a separate edition.

The homepage begins with four questions: what is happening, what can be predicted, what would change with action, and which action is worth its cost. Each main lesson contains a decision brief, the relevant rows, a worked calculation, interpretation, an action, and an entry in the cumulative management memo. Technical continuations use the same variables and calculation. Former `lesson-N-guide.html` URLs serve the same complete lesson with a canonical main URL.

The current build uses `scripts/retail_case.py` for the data and analyses, `retail_content.py` for the ten lessons, `retail_pages.py` for orientation and synthesis, and `build_retail_course.py` for rendering and labs. The previous edition's builders are no longer invoked by `build_all.py`.

## Reproduce

Python 3.11 or later is required for the labs. Install the tested dependency versions from requirements.txt in a virtual environment, then run:

```
python scripts/build_all.py
python scripts/check_public_release.py --execute
```

The first command builds all pages, shared CSV releases, standalone Python labs, executed notebook output, and JSON results. The second verifies cohort and timeline boundaries, numerical identities, data consistency, links, notebook/script agreement, and independent reruns of all ten labs. Small floating-point differences are compared at a stated tolerance.

The notebooks include the shared setup and a visible worked calculation. Each standalone lab includes the same generator, requires no network access, and verifies its worked result against the shared analysis. An early storyboard prototype can be built with `python scripts/build_retail_course.py --pilot` for Lessons 1, 6, and 9.

The deployed site is the prebuilt dist/ directory and needs no application server. All navigation and worked solutions remain usable without JavaScript. Every quantitative chart includes a text alternative or a corresponding table.

## Publication

The GitHub Actions workflow rebuilds from source, independently reruns all ten labs, and deploys `dist/` to GitHub Pages. See PUBLISHING.md for verification steps.

## Provenance and reuse

The generated case data are original synthetic teaching examples; no third-party dataset license is needed to obtain their source observations because no third-party observations are included. This does not establish realism or empirical validity. See DATA-NOTICE.md.

Public repository visibility is not itself an open-source license. No separate reuse license for the course prose or code has been selected here. External reading links and installed software retain their own terms; their source and data are not bundled.
