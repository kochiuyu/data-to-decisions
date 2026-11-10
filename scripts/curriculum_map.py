"""Explicit topic crosswalk for the ten user-supplied 2026 slide decks.

Ranges partition each original deck. Screenshot-by-screenshot repetitions are
consolidated; the concepts and worked operations are retained in the retail case.
"""
from retail_ui import table,p

SLIDE_COUNTS={1:104,2:172,3:84,4:137,5:93,6:138,7:63,8:137,9:93,10:75}
COVERAGE={
1:[
 (1,7,'Purpose, readiness, and managerial question','evidence','main'),
 (8,9,'Observations, variables, and the data table','theory-foundations','main'),
 (10,10,'Storage formats and their uses','theory-collection','main'),
 (11,11,'Cross-sections, time series, and panels','theory-foundations','main'),
 (12,17,'Source inspection, loading, and variable selection; retail application replaces hotels','structure','main'),
 (18,19,'Measurement quality and the six review questions','theory-foundations','main'),
 (20,21,'Source documentation and collection routes','theory-collection','main'),
 (22,26,'Sampling, coverage, nonresponse, and benchmarking; the historical poll is omitted','theory-foundations','main'),
 (27,30,'Aligned collection, scoring protocols, and interview blinding','theory-collection','main'),
 (31,32,'Four Vs, collection costs, permissions, and responsibilities','theory-collection','main'),
 (33,34,'Input quality, AI verification, and the preparation task','theory-practice','main'),
 (35,35,'Nominal, ordinal, interval, and ratio scales','theory-foundations','main'),
 (36,36,'Documented preparation workflow','theory-practice','main'),
 (37,37,'Tidy data, stable identifiers, and keys','theory-method','main'),
 (38,48,'Inspecting identifiers, composition, and selection','structure','main'),
 (49,59,'Long/wide data, multi-level columns, and naming','reshape','main'),
 (60,60,'Primary and foreign keys in relational tables','theory-method','main'),
 (61,72,'Event versus observation and time-specific assignments','relationships','main'),
 (73,73,'One-to-one, many-to-one, and many-to-many relationships','theory-method','main'),
 (74,76,'Joining records using assignment periods','relationships','main'),
 (77,93,'Grouping, aggregation, rates, eligibility, and ranking','aggregation','main'),
 (94,94,'Cleaning decisions, systematic missingness, exclusion, and imputation','theory-practice','main'),
 (95,95,'Entity resolution through a reviewed alias-to-ID table','theory-method','main'),
 (96,96,'Preservation, profiling, validation, and documentation','theory-practice','main'),
 (97,102,'Project folders, readable filenames, and handover','workflow','main'),
 (103,104,'AI accountability; the numerical time-allocation slogan is omitted','theory-practice','main'),
],
2:[
 (1,9,'EDA purpose, empirical distributions, and questions','explore','main'),
 (10,15,'Frequency, density, and visual/table design','theory-visual','main'),
 (16,18,'Dataset scope; retail store profiles replace hotel observations','read-data','main'),
 (19,28,'Histogram widths, normalization, and reproducible counts','bin-widths','main'),
 (29,38,'Distribution shape and filtering; delivery groups replace city/star filters','distributions','main'),
 (39,40,'Summary formulas, quantiles, mode, percentile range, and coefficient of variation','theory-visual','main'),
 (41,49,'Spread, shape, boxplot and violin interpretation','distributions','main'),
 (50,82,'Common-scale group distributions and summary statistics; repeated histograms use grouped boxes','group-distributions','main'),
 (83,92,'Sample spaces, random variables, distribution parameters, support, and moments','probability','appendix'),
 (93,96,'Conditional means, descriptive questions, prediction, and causation','theory-method','main'),
 (97,108,'Composite management scores and marginal distributions; proxy construction generalized','probability','appendix'),
 (109,117,'Individual-observation scatter before grouped means','raw-association','main'),
 (118,132,'Counts, within-group denominators, ordered shares, and stacked bars','association','main'),
 (133,137,'Group boxes, spread, and overlap; violin construction remains optional','group-distributions','main'),
 (138,148,'Quantile bins, group means, and variation hidden by aggregation','association','main'),
 (149,156,'Covariance products, sign intuition, and correlation pattern gallery','theory-covariance','main'),
 (157,161,'Worked covariance and correlation from the same rows; redundant library calls consolidated','worked-covariance','main'),
 (162,166,'Pooled and subgroup correlations with observation counts','worked-covariance','main'),
 (167,169,'Causal interpretation; decorative quotations omitted','theory-covariance','main'),
 (170,170,'Latent variables, proxies, standardized composites, and optional PCA','probability','appendix'),
 (171,172,'Event rules, independence, Bayes, weighted and conditional moments','probability','appendix'),
],
3:[
 (1,8,'Population inference, estimation, and the managerial question','theory-foundations','main'),
 (9,18,'Threshold proportions; the audit replaces market-risk data','sampling-variation','main'),
 (19,20,'Sampling distributions and the SD/SE distinction','sampling-visuals','main'),
 (21,27,'Interval estimation and normal/t reference distributions; corrected SD conventions','sampling-visuals','main'),
 (28,35,'Subsampling mechanics and interpretation; unscaled subsample intervals corrected','resampling-visuals','main'),
 (36,43,'Bootstrap draws, estimate histogram, and percentile endpoints','resampling-visuals','main'),
 (44,44,'External validity as a transfer question','scope-and-search','main'),
 (45,50,'Estimator properties, LLN, CLT, and binary uncertainty','inference-details','appendix'),
 (51,54,'Population claims, null/alternative, and testing logic','theory-method','main'),
 (55,58,'Two errors and decision trade-offs; arbitrary coin rule omitted','test-visuals','main'),
 (59,63,'Critical regions, p-values, and a reproducible decision; audit replaces coin approximation','test-visuals','main'),
 (64,65,'t reference distribution and the standardized test statistic','sampling-visuals','main'),
 (66,67,'Rejection regions and power under a specified alternative','test-visuals','main'),
 (68,68,'Worked one-sample test using the audit benchmark','testing','main'),
 (69,72,'Paired observations and explicit selection; audit/system readings replace prices','paired-analysis','main'),
 (73,76,'Distribution of paired differences and inspection before testing','paired-analysis','main'),
 (77,79,'Paired SD, SE, t statistic, interval, and decision','paired-analysis','main'),
 (80,80,'Parameter restrictions, composite nulls, and test direction; original claims corrected','inference-details','appendix'),
 (81,83,'Independent groups and Welch inference; reference-distribution errors corrected','independent-analysis','main'),
 (84,84,'Multiple testing, selective reporting, and family-wise adjustment','scope-and-search','main'),
],
4:[
 (1,8,'Regression goals, conditional means, and parametric versus flexible forms','theory-model-choice','main'),
 (9,11,'Overall mean versus group-specific predictions','from-bins','main'),
 (12,25,'Sample definition and two-group predictions; retail stores replace hotels','from-bins','main'),
 (26,38,'Four group means, raw observations, counts, and fitted group values','from-bins','main'),
 (39,43,'Local weighted lines, neighborhood fractions, and visible smooth curves','functional-form','main'),
 (44,48,'OLS, covariance arithmetic, centroid, and vertical residuals','line-geometry','main'),
 (49,53,'Coefficients, fitted values, and the regression line','calculate','main'),
 (54,54,'Sample residual balance and equality of observed and fitted means','theory-model-choice','main'),
 (55,56,'Deviation geometry and the summed-squares identity','theory-fit-geometry','main'),
 (57,57,'R-squared and its equality to squared simple-regression correlation','regression-details','appendix'),
 (58,62,'MSE, RMSE, variation accounting, and denominator conventions','fit','main'),
 (63,64,'Reproducible OLS and fitting-error calculations; duplicate library examples consolidated','calculation','appendix'),
 (65,67,'Linear-in-coefficients models, logs, and proportional changes','theory-fit-geometry','main'),
 (68,76,'Four specifications and level-level predictions','functional-form','main'),
 (77,84,'Log-level changes, curve plots, and retransformation','functional-form','main'),
 (85,92,'Level-log units, intercept meaning, and positive input values','functional-form','main'),
 (93,100,'Log-log elasticity and exact finite changes; original scaling error corrected','functional-form','main'),
 (101,104,'Common-sample model comparison in consistent outcome units','functional-form','main'),
 (105,116,'Continuous shape and log transformations; same-store demand replaces GDP','functional-form','main'),
 (117,123,'Quadratic curves, rescaling, and slopes at specified values','functional-form','main'),
 (124,129,'Cubic curves, support, and comparison of nonlinear models','functional-form','main'),
 (130,130,'Residual patterns, record checks, and sensitivity of the fitted slope','residual-patterns','main'),
 (131,136,'Continuous spline, hinge values, knot units, and segment slopes','functional-form','main'),
 (137,137,'Deliberate model simplification and transferable interpretation','big-picture','main'),
],
5:[
 (1,6,'Purpose and managerial motivation','decision-brief','main'),
 (7,11,'Coefficient uncertainty, robust SEs, and hypothesis tests','theory-inference','main'),
 (12,12,'Classical intercept uncertainty and reference values','multiple-regression-details','appendix'),
 (13,20,'Comparable measurement and fixed analysis sample; retail replaces wages','read-data','main'),
 (21,27,'Precise versus imprecise estimates and matching confidence/test levels','regression-uncertainty','main'),
 (28,47,'Mean confidence bands, individual prediction bands, and worked SEs','interval-bands','main'),
 (48,48,'External validity and scope of operating use','theory-prediction','main'),
 (49,51,'Multiple regression, design matrix, and least squares','multiple-regression-details','appendix'),
 (52,52,'Multicollinearity, variance inflation, and individual versus joint tests','theory-foundations','main'),
 (53,68,'Same-sample adjustment, auxiliary regression, and omitted-variable identity','controls','main'),
 (69,72,'Centered quadratic controls and nested fit comparison','model-comparison','main'),
 (73,76,'Reference categories, group lines, and continuous interactions','theory-specification','main'),
 (77,80,'Group slopes, centering, profile contrasts, and joint inference','interpret','main'),
 (81,81,'Ordinary and adjusted R-squared','model-comparison','main'),
 (82,92,'Actual-versus-fitted graphs, residual direction, and operational shortlist','residual-review','main'),
 (93,93,'Transferable interpretation and judgment','big-picture','main'),
],
6:[(1,12,'Prediction tasks, losses, bias, variance, and irreducible error','prediction-task','main'),(13,34,'Features, candidate complexity, aligned samples, and overfitting','validation-design','main'),(35,44,'Likelihood, deviance, AIC, and BIC','prediction-details','appendix'),(45,58,'Holdout and cross-validation; deployment stability','validation-design','main'),(59,67,'Prediction workflow and log retransformation','lasso','main'),(68,75,'LASSO penalty, scaling, and tuning','lasso','main'),(76,101,'Missing-data rules, feature groups, nonlinear terms, and interactions','validation-design','main'),(102,114,'Repeated validation and complexity comparison','validation-design','main'),(115,138,'Regularization, retained coefficients, final evaluation, and deployment','lasso','main')],
7:[(1,12,'Prediction versus interventions and causal questions','counterfactuals','main'),(13,35,'Potential outcomes, ITE, ATE/ATT/ATU, selection, and SUTVA','counterfactuals','main'),(36,41,'Controlled/natural experiments and random assignment','experiment-design','main'),(42,57,'A/B arithmetic, regression equivalence, outcomes, and cost','experiment-value','main'),(58,63,'Balance, implementation, replication, and guardrails','experiment-design','main')],
8:[(1,19,'Conditional independence, subclassification, and target effects','identification','main'),(20,57,'DAGs, chain, fork, collider, and adjustment','graph-structures','main'),(58,69,'Combined paths, collider descendants, and d-separation','graph-details','appendix'),(70,90,'Confounding and selection-bias mechanisms','graph-details','appendix'),(91,105,'Backdoor adjustment, precision controls, and proxies','graph-structures','main'),(106,129,'Assignment story, balance, strata, and within-stratum effects','calculate','main'),(130,137,'ATE/ATT/ATU weighting and human ownership of DAG assumptions','target-weights','main')],
9:[(1,24,'Assignment mechanisms, endogeneity, controls, and validity','ideal-experiment','main'),(25,33,'Build an adjustment strategy from the substantive causal model','ideal-experiment','main'),(34,41,'Target-trial workflow and observational methods','ideal-experiment','main'),(42,79,'Treatment coding, analytical sample, and baseline comparison','read-data','main'),(80,88,'Progressively richer regression specifications','matching-options','main'),(89,93,'Exact, coarsened exact, and propensity-score matching','matching-options','main')],
10:[(1,14,'Two-by-two DiD, counterfactual trend, and ATT','panel-design','main'),(15,21,'Natural-experiment reasoning and regression representation','did-regression','main'),(22,44,'Panel construction, IDs, aggregation, exposure, and balance','panel-design','main'),(45,57,'Group changes, weighting, regression, and subgroup comparisons','did-regression','main'),(58,70,'Pre-trend diagnostics and pre-treatment controls','did-regression','main'),(71,75,'Interaction regression, continuous exposure, and decision checklist','did-details','appendix')]
}

def coverage_html(n):
    rows=[]
    for start,end,topic,target,route in COVERAGE[n]:
        page=f'lesson-{n}.html' if route=='main' else f'lesson-{n}-appendix.html'
        rows.append([f'{start}–{end}',topic,f'{route.title()}: {target}'])
    links=''.join(f'<li><a href="lesson-{n}{"" if route=="main" else "-appendix"}.html#{target}">{topic}</a> <span>({start}–{end})</span></li>' for start,end,topic,target,route in COVERAGE[n])
    specifics=(p('For Lesson 1, source design, sampling, measurement, and preparation are taught before the retail application. The price-comparison and interview examples illustrate collection protocols; the alias table illustrates entity resolution. They do not add new datasets to the running case. The ranking procedure is retained, while its original plotting code and chart are condensed into plotting guidance.')+'<p><a href="python-bridge.html">Python readiness and syntax bridge</a> · <a href="resources.html#labs">Runnable lesson notebooks</a></p>') if n==1 else ''
    return '<section id="original-coverage"><h2>Teaching coverage from the original slides</h2>'+p(f'The supplied Lesson {n} deck has {SLIDE_COUNTS[n]} slides. This map records where its substantive topics are taught in the website. Reading and presentation views use the same lesson blocks.')+table(['Original slides','Topic retained','Location'],rows,'Original-deck topic map')+'<details><summary>Open a mapped topic</summary><ul>'+links+'</ul></details>'+specifics+p('Original hotel, wage, country, advertising, and other datasets are replaced by the continuing retail case. Repeated code/output screenshots are consolidated into worked steps, tables, and executable labs. Decorative quotations and unsupported time-allocation slogans are not carried forward. The aim is to retain the teaching substance, not to reproduce each original slide as a separate screen.')+'</section>'

def validate_coverage():
    for n,expected in SLIDE_COUNTS.items():
        numbers=[i for start,end,*_ in COVERAGE[n] for i in range(start,end+1)]
        assert numbers==list(range(1,expected+1)),(n,'Coverage gaps or duplicate ranges')
