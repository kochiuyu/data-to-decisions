# Data to decisions

A public, reproducible course in applied business statistics: ten business cases, ten guided worked lessons, optional technical appendices with 246 detailed teaching stops, accessible charts, and executable Python labs.

## This edition

Every case dataset is newly generated for teaching from a documented model and fixed seed. The public release contains no historical source records, resampled historical records, fitted historical results, or private site files. Its numbers are not claims about real people, firms or markets. The earlier private course remains a separate edition.

Topics progress from measurement, distributions and inference to regression, prediction, experiments, causal graphs, matching and difference-in-differences. Each business case presents a decision, an observed result, a question, and a reveal of the synthetic model's known truth. A guided lesson follows one business problem through the practical obstacle, evidence, a worked method step, and next action. Its appendix contains the data-generating process and the original detailed methods. Five supporting pages provide navigation, study guidance, Python help, provenance and a final synthesis.

## Reproduce

Python 3.11 or later is required for the labs. Install the tested dependency versions from requirements.txt in a virtual environment, then run:

```
python scripts/build_all.py
python scripts/check_public_release.py --execute
```

The first command recalculates the lesson results and builds HTML, Python scripts, notebooks and JSON results. The second checks the site and reruns every lab. The notebooks contain actual output from the same source, not copied historical output. Mathematical functions and random sequences can differ in their last digits across dependency/platform versions.

The deployed site is the prebuilt dist/ directory and needs no application server. All navigation and worked solutions remain usable without JavaScript. Every quantitative chart includes a text alternative or a corresponding table.

## Publication

The GitHub Actions workflow checks the prebuilt files and deploys dist/ to GitHub Pages. Select **Settings → Pages → Build and deployment → Source: GitHub Actions** before the deployment. See PUBLISHING.md for verification steps.

## Provenance and reuse

The generated case data are original synthetic teaching examples; no third-party dataset license is needed to obtain their source observations because no third-party observations are included. This does not establish realism or empirical validity. See DATA-NOTICE.md.

Public repository visibility is not itself an open-source license. No separate reuse license for the course prose or code has been selected here. External reading links and installed software retain their own terms; their source and data are not bundled.
