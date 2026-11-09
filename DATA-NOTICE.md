# Data notice

## Origin

All quantitative case observations in the current release come from one shared generator in `scripts/retail_case.py`, using seed 20261109. It defines 150 stores, 32 weeks, pre-policy records, an independent audit, and three disjoint intervention cohorts. Distribution assumptions, assignment rules, accounting inputs, and analysis steps are disclosed in the source. No historical records are downloaded, resampled, or used for calibration.

Case names are fictional. Numeric constants used to specify a mathematical model are teaching assumptions, not estimates taken from an external dataset. Displayed case estimates, tables, plots and notebook outputs are calculated from these new generators.

## Included and excluded

Included: generator source, analysis source, synthetic CSV releases, repair ledger, original teaching explanations, calculated results, charts, notebooks, and study pages. The shared public store-week CSV excludes the alternate policy outcomes and latent probabilities; these remain available through the generator for known-answer exercises.

Excluded: original stock/retail/hotel/survey/advertising/transport data, historical fitted outputs and arrays, private source archives, authentication or hosting configuration, and internal review materials.

## Meaning

A simulation permits checking a method against a known data-generating process. It does not prove that the process matches a real firm, person or market. Inference and causal interpretations remain conditional on the assumptions stated in each lesson.

## Third-party references

Further-reading links identify optional conceptual resources. No readings or data are copied into the release. NumPy, pandas, SciPy and scikit-learn are installed dependencies, not bundled source; each keeps its own license.

This notice describes provenance. It does not grant an additional license over the course or any third-party material.
