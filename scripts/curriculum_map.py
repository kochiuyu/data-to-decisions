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
2:[(1,15,'EDA questions and visual/table design','explore','main'),(16,38,'Histograms, bins, filtering, and comparison scope','distributions','main'),(39,49,'Summary formulas, spread, shape, boxplots, and violin plots','distributions','main'),(50,82,'Comparable groups, common scales, density, and grouped summaries','calculate','main'),(83,92,'Random variables and theoretical distributions','probability','appendix'),(93,148,'Conditional means, composition, scatterplots, and binning','association','main'),(149,169,'Covariance, correlation, subgroup interpretation, and causal questions','association','main'),(170,172,'Latent variables, proxies, and probability rules','probability','appendix')],
3:[(1,18,'Population risk, point estimates, and a threshold proportion','sampling-variation','main'),(19,27,'Standard errors, confidence intervals, and sampling distributions','calculate','main'),(28,43,'Subsampling and bootstrap procedures','resampling','main'),(44,50,'External validity, estimator properties, LLN, and CLT','inference-details','appendix'),(51,68,'Hypotheses, errors, significance, p-values, power, and one-sample tests','testing','main'),(69,79,'Paired differences and paired testing','testing','main'),(80,84,'Independent groups, composite hypotheses, and multiple testing','testing','main')],
4:[(1,38,'Mean prediction, bins, and conditional relationships','from-bins','main'),(39,43,'Local linear smoothing and nonlinear shape','functional-form','main'),(44,53,'OLS, coefficients, and residuals','calculate','main'),(54,64,'ANOVA decomposition, R-squared, MSE, and RMSE','fit','main'),(65,104,'Four log/level specifications and model comparison','functional-form','main'),(105,130,'Nonlinear patterns, polynomial models, and interpretation','functional-form','main'),(131,137,'Piecewise linear splines and deliberate model choice','functional-form','main')],
5:[(1,27,'Regression inference, robust standard errors, and slope tests','regression-uncertainty','main'),(28,48,'Mean confidence intervals, individual prediction intervals, and scope','regression-uncertainty','main'),(49,60,'Multiple-regression models, matrix notation, and controls','multiple-regression-details','appendix'),(61,68,'Omitted-variable identity and its direction','controls','main'),(69,80,'Nonlinear terms, indicators, and interactions','controls','main'),(81,93,'Fit, actual-versus-fitted plots, and residual-based review','residual-review','main')],
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
