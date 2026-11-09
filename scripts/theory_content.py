"""General concepts taught before the shared worked application.

Each item is one slide and its paragraph notes, shared with the reading view.
Notation is introduced here; case-specific values enter only in the application.
"""
from curriculum_content import teach,bullets
from retail_ui import formula,section,table

TITLES = {
1:'Measurement and data preparation',
2:'Distributions and association',
3:'Sampling, estimation, and hypothesis testing',
4:'Simple regression and functional form',
5:'Multiple regression, interactions, and inference',
6:'Prediction, validation, and regularization',
7:'Causal inference and randomized experiments',
8:'Causal diagrams and adjustment',
9:'Regression adjustment and matching',
10:'Difference-in-differences and panel data',
}

def B(title,points,*notes):
    assert len(points)<=4 and all(len(x.split())<=22 for x in points)
    return title,teach(title,bullets(*points),list(notes))

def F(title,equation,*notes):
    return title,teach(title,formula(equation),list(notes))

# Sections form a continuous explanation: definitions, method, interpretation.
THEORY = {
1:[('theory-foundations','Define what the data represent',[
B('A dataset represents a population through defined observations',[
 'Population: the units and periods the question concerns','Observation: what one row represents','Variable: a characteristic measured for each observation','Frame and sample: the available list and the selected observations'],
 'Begin with the question and define its target population. Then choose the observation unit: a person, organization, transaction, or unit-period. The frame is the list from which observations can be collected, and the sample is the subset actually selected. These definitions tell us whose experience a statistic summarizes.',
 'The same entity may appear on several rows when time or events are part of the observation. Repetition of an entity identifier is therefore compatible with a valid dataset; uniqueness must be assessed at the chosen observation level.'),
B('A sampling design connects the observed sample to its population',[
 'Define the population, then check the sampling frame','Simple random sampling gives every fixed-size subset the same chance','Follow up selected units that do not respond','Benchmark sample composition against trustworthy population information'],
 'The population is the group about which we want to learn; the frame is the available list from which we select. In a simple random sample without replacement, every subset of the chosen size is equally likely, so every listed unit has the same inclusion probability. Other probability designs can use unequal, known chances. Random selection does not make every realized sample identical to the population.',
 'Trace the sequence: population, frame, selected sample, responding sample. Coverage concerns units missing from the frame; nonresponse concerns selected units whose measurements are not obtained. Compare important characteristics with a registry or another trusted source and investigate the collection process. Repeating collection from the same incomplete frame increases volume while leaving the coverage gap in place.'),
B('Measurement quality begins with a common definition',[
 'Validity: the measure captures the intended concept','Reliability: the rule yields consistent measurements','Comparability: definitions align across units and periods','Coverage: the records represent the intended population'],
 'A variable needs an operational definition: what is counted, when it is measured, and which values are allowed. A data dictionary records the units, categories, missing-value codes, and collection process. This agreement turns a business concept into a measure that different analysts can use consistently.',
 'Use six questions to review a proposed measure. Meaning: what does it capture? Validity: does that match the intended concept? Reliability: would repeated measurement be consistent? Comparability: is the same rule used across units and periods? Coverage: who is absent? Selection: are the observed and absent units systematically different? The first four guide measurement; the last two guide the population claim.'),
B('Measurement scales determine which arithmetic is meaningful',[
 'Nominal: categories; count and compare shares','Ordinal: ordered categories; compare ranks','Interval: meaningful differences; zero is a reference','Ratio: meaningful differences and ratios; zero denotes absence'],
 'A number can be a label rather than a quantity. Nominal codes support counts, ordinal codes additionally support ordering, and interval scales support meaningful differences. Ratio scales add a meaningful zero. Choose summaries that respect these properties: a mean of identifier codes has no substantive interpretation.'),
B('Cross-sections, time series, and panels organize different comparisons',[
 'Cross-section: different units at one time','Time series: one unit across time','Panel: the same units across time','Choose the structure from the comparison of interest'],
 'A cross-section describes differences between units, a time series describes change over time, and a panel supports both perspectives. Aggregating or selecting observations can change the structure. State the resulting observation unit after each transformation so that later analysis uses the correct rows and dependence structure.'),
]),('theory-collection','Design collection before preparing the file',[
B('A common collection protocol makes measurements comparable',[
 'Choose a source that records the quantity of interest','Align the item, timing, and conditions of comparison','Turn broad concepts into questions and scoring rules','Train reviewers and specify who is blinded to which information'],
 'Sources capture different things. Systems and APIs record transactions, logs, or sensor events; web pages record what is displayed; administrative records reflect an organizational process. Surveys and interviews elicit responses, while experiments assign a change and measure its consequences. Choose the source and collection rule together. To compare online and offline prices, for example, match the same product and pack size at approximately the same time, with consistent treatment of taxes and promotions.',
 'Management quality is a concept that needs an operational measure. Define observable practices, ask consistent questions, and use a scorecard with clear anchors. Train interviewers on the same examples so that a score reflects the practice rather than the interviewer. A possible blinded design has respondents describe routines without seeing scoring thresholds and interviewers score those descriptions without seeing firm performance. These two information restrictions reduce different sources of bias; the study should still explain its purpose and obtain the appropriate participation agreement.'),
B('A collection plan assigns purpose, permissions, cost, and ownership',[
 'Specify the decision, required fields, and collection schedule','Confirm permitted use and protect identifiable information','Budget collection, follow-up, and quality review','Assign an owner and record the source history'],
 'Compare collecting new data with reusing an existing source. New collection gives control over definitions and timing but requires staff time, participant effort, and follow-up. An existing source may be faster while requiring work to establish its purpose, coverage, and permitted uses. Make those choices before collecting: identify the needed fields, obtain the applicable permissions or consent, set access and retention rules, and assign responsibility for exceptions.',
 'Attach a short source record: who collected the data; why; when and where; how observations were selected and measured; and what transformations have occurred. Keep variable definitions, units, category codes, valid ranges, and missing-value codes in the codebook. Together, the source record and codebook let a colleague assess both the history of the file and the meaning of its columns.'),
B('The four Vs translate data scale into processing requirements',[
 'Volume: how much data must be stored and processed','Velocity: how quickly data arrive and must be used','Variety: the different sources, structures, and formats','Veracity: the accuracy and credibility of the measurements'],
 'Translate each V into a design choice. Volume affects storage and computing capacity. Velocity determines whether processing must happen immediately or can run in batches. Variety determines how tables, text, and nested records are connected. Veracity determines source checks and reconciliation rules. Larger collections are useful when they improve the decision; representativeness still depends on the collection process.',
 'Choose a format to fit that task. CSV and TSV exchange plain tables; Excel supports spreadsheet review; JSON and XML represent nested records; Parquet stores typed columns efficiently for analytical work. Preserve delimiters, encoding, data types, and missing-value conventions when converting formats. The storage format does not define what an observation means.'),
]),('theory-method','Organize, combine, and summarize records',[
B('Tidy data and explicit keys make transformations traceable',[
 'One variable per column and one observation per row','A key uniquely identifies an observation','Long format stores repeated observations in rows','Wide format places repeated measurements in columns'],
 'A key can contain more than one variable. Tidy organization separates different observation types into related tables. Long and wide formats can encode the same information, but they make different operations convenient. A reshape should preserve keys, values, and totals; it should not silently aggregate conflicting observations.',
 'An entity identifier should be present and stable as names or operating arrangements change. Prefer an identifier that does not encode changeable information such as a manager or region. A primary key uniquely identifies rows in its own table; a foreign key refers to that key from another table. For example, an organization ID can be unique in a registry and repeated in a transaction table whose own key is a transaction ID.'),
('Resolve names to stable entities before checking duplicate observations',
 teach('Resolve names to stable entities before checking duplicate observations',
 table(['Original name','Standard name','Entity ID'],[
  ['North Quay','North Quay','E001'],
  ['N. Quay','North Quay','E001'],
  ['North Quay branch','North Quay','E001'],
  ['North Quay Outlet','North Quay Outlet','E002'],
 ],'Illustrative identity map: reviewed aliases share a stable ID'),[
 'Entity resolution establishes which records refer to the same real-world entity. This illustrative map treats three reviewed aliases as one branch and the outlet as a different branch. Confirm identity with an authoritative registry, address, or other stable attributes; spelling similarity suggests a candidate match rather than establishing identity. Keep the original name alongside the reviewed mapping.',
 'After assigning the entity ID, define the observation key, such as entity plus week, and check duplicate observations. Two aliases can refer to one entity while still describing two valid weeks. Conversely, two records for the same entity-week may repeat the same observation or contain conflicting values. Resolving identity makes that subsequent check meaningful.'
 ])),
B('Join cardinality determines how many rows a merge can produce',[
 'One-to-one: unique keys on both sides','Many-to-one: repeated left keys, unique right keys','Many-to-many: multiple candidate pairs','Validate uniqueness, unmatched keys, and row counts'],
 'A relational join combines rows using shared keys. The intended relationship determines whether the operation preserves or expands the observation count. Viewed from the opposite side, a many-to-one relationship is one-to-many. Choose left or inner joins according to the population the analysis should retain. When relationships change over time, dates or validity intervals belong in the matching rule.'),
F('A pooled rate weights each observation by its exposure',
 'Pooled rate = Σ countᵢ / Σ exposureᵢ = Σ weightᵢ × rateᵢ',
 'A rate divides an event count by the opportunities for that event. Here weightᵢ is exposureᵢ divided by total exposure. Equal exposure makes the simple mean of rates equal to the pooled rate. With unequal exposure, an average unit rate and a pooled opportunity rate summarize different targets.',
 'Grouping changes the observation unit. After aggregation, report the contributing counts and exposure alongside the rate. Eligibility rules, such as a minimum number of reporting periods, define which groups enter the summary.'),
]),('theory-practice','Make preparation reproducible',[
B('Cleaning is a documented sequence of decisions',[
 'Preserve and profile the original records','Define scope, keys, ranges, and coding rules','Resolve missing values, duplicates, and inconsistent relationships','Validate the output and retain a repair log'],
 'Inspect before changing data. Distinguish a genuine zero from missing information, and an identical duplicate from conflicting records with the same key. Check that headers and subtotals have not entered the observation rows, dates fall within the intended period, and quantities use consistent units. Record which rule was used and what it changed so that another analyst can reproduce the dataset.'),
B('Recover, exclude, or impute according to the missing-data problem',[
 'Recover the recorded value from a trusted source when possible','Exclusion changes which observations enter the analysis','Imputation supplies an estimate, not an observed value','Record the reason, affected observations, and resulting coverage'],
 'Begin by investigating why the value is missing. A failed export can sometimes be repaired from an original ledger. If recovery is impossible, excluding incomplete observations makes the calculation describe those retained. If busy units are less likely to report, for example, the retained sample can overrepresent quieter operations. Compare missingness across relevant groups before choosing the analytical sample.',
 'Imputation fills a missing value using a stated rule or model. It can retain rows, but the filled value is inferred and its uncertainty matters in later analysis. Mark imputed values and record the information used. A blank count is not automatically zero, and retaining a denominator while omitting an unresolved numerator changes the rate. In the retail application the ledger permits recovery; this is one solution, not a general assumption that every missing value is recoverable.'),
B('Automation is useful when its output can be checked',[
 'Specify the transformation and expected result','Check changed rows, totals, and eligibility','Keep executable steps beside the data dictionary','Assign responsibility for definitions and exceptions'],
 'Code and AI assistance can speed up a clearly specified preparation task. The analyst still needs a checkable contract: the intended input, output, and invariants. Preserve the original data, separate inputs from outputs, and organize the project so that someone else can trace each published number back to its source. Fluent explanations and polished charts do not verify a transformation; check the affected records and let the responsible person approve the business rules.'),
])],
2:[('explore','Describe a distribution before comparing groups',[
B('Exploratory analysis asks about centre, spread, shape, and relationships',[
 'Inspect units, missingness, and unusual values','Describe the typical value and variation','Look for clusters, asymmetry, and tails','Compare groups and relationships using consistent definitions'],
 'Exploratory data analysis builds an understanding of the observed distribution before selecting a model. Start with the observation unit and variable scale. A table supplies exact values; a graph exposes patterns. Together they help determine which summary answers the question and which features need further explanation.'),
B('Empirical and theoretical distributions describe different objects',[
 'Empirical distribution: frequencies in the observed data','Random variable: a numerical outcome of an uncertain event','Probability distribution: possible values and their probabilities','Expected value: a probability-weighted average'],
 'An empirical distribution assigns weight to the values actually observed. A theoretical distribution is a model for possible outcomes under repetition. Discrete probabilities add across values; continuous probabilities correspond to areas under a density. This distinction connects descriptive statistics with the later theory of sampling.'),
F('The mean and variance summarize location and squared spread',
 'x̄ = Σxᵢ / n; s² = Σ(xᵢ − x̄)² / (n − 1)',
 'The mean uses every observation and is sensitive to extreme values. Sample variance measures squared deviations from that mean, using n−1 when estimating a population variance from a sample. Its square root, the standard deviation, returns to the original measurement units.'),
B('Quantiles describe the distribution through ordered positions',[
 'Median: the 50th percentile','Q₁ and Q₃: the 25th and 75th percentiles','IQR = Q₃ − Q₁: spread of the middle half','Range: the observed minimum to maximum'],
 'Quantiles answer questions about positions in an ordered distribution. They complement mean and standard deviation when extreme values have strong influence. The median describes the middle observation, while the interquartile range describes how far the middle half extends. Always distinguish observed spread from uncertainty about an estimated mean.'),
]),('theory-method','Choose displays and comparisons deliberately',[
B('Histograms, densities, and boxplots expose different distribution features',[
 'Histogram: counts or shares within intervals','Density: a smoothed shape with total area one','Boxplot: median, quartiles, and a stated whisker rule','Skewness and tail weight describe different aspects of shape'],
 'A histogram depends on bin boundaries and widths; a density depends on smoothing. A conventional boxplot marks the median and quartiles, with whiskers extending to observations within 1.5 IQR of the box. Values beyond these fences are flagged for inspection. A violin adds a density shape to the same distributional view.'),
B('Comparable group displays use consistent scales and denominators',[
 'Keep measurement definitions and periods aligned','Use common bins and axis ranges','Use shares or density when group sizes differ','Show the number of observations in each group'],
 'Raw counts and within-group shares answer different questions. A group can contain more events simply because it has more observations. State the group denominator, preserve category order, and show sample sizes. The aim is to distinguish composition, prevalence, and severity using a comparison that readers can reconstruct.'),
F('A conditional mean summarizes the observations sharing a characteristic',
 'E[Y | X = x] = the expected outcome at a specified value of X',
 'Conditioning narrows the population being summarized. For a categorical X, estimate the conditional mean within each category. For a continuous X, bins or a fitted curve can summarize the relationship. A scatterplot preserves individual variation that group averages can hide.'),
F('Correlation standardizes the linear co-movement of two variables',
 'Correlation(X,Y) = Cov(X,Y) / [SD(X) × SD(Y)]',
 'Covariance is positive when above-average values of one variable tend to coincide with above-average values of the other. Correlation divides by their standard deviations, removing the measurement units and producing a value from −1 to 1. Inspect the scatterplot as well: a nonlinear relationship can have little linear correlation.'),
B('Description, prediction, and causal explanation answer different questions',[
 'Description: what patterns appear in the observed population?','Prediction: what outcome should we expect for another observation?','Causation: what would change under an intervention?'],
 'The same association may be useful for describing groups or anticipating outcomes. To interpret it as the consequence of changing a variable, we also need an account of how that variable is assigned and what else changes with it. The course develops those comparison designs after introducing prediction.'),
])],
3:[('theory-foundations','Distinguish the population from its estimate',[
B('A statistic varies across samples while its target parameter stays fixed',[
 'Parameter: the population quantity of interest','Estimator: a rule applied to a sample','Estimate: the value obtained from the observed sample','Sampling distribution: the estimator across repeated samples'],
 'Inference asks how a sample informs a population quantity. The estimate is a realized number; the sampling distribution describes how that number would change if sampling were repeated. Begin by specifying the target population, the sampling unit, and the selection design. Those choices determine what repetition means.'),
F('The standard error measures sampling variation in the estimated mean',
 'SE(x̄) = s / √n, for independent observations',
 'The standard deviation s describes variation among observations. The standard error describes variation among sample means. Under independent sampling with finite variance, increasing n reduces the standard error at the square-root rate: roughly four times as many observations are needed to halve it.',
 'The law of large numbers explains convergence of the sample mean. The central limit theorem explains its approximate normal sampling distribution for sufficiently large independent samples. When observations occur in dependent groups, use the independent group as the basis for the uncertainty calculation.'),
F('A confidence interval combines an estimate with a margin of error',
 '95% mean interval = x̄ ± t₀.₉₇₅,ₙ₋₁ × SE(x̄)',
 'The critical value sets the confidence level, and the standard error sets the width in outcome units. Under independent normal observations, the t interval has its stated coverage; it also provides an approximation in many larger samples. A 95% procedure covers the fixed target in 95% of repeated samples under its model.',
 'Interpret the resulting range against the decision threshold and the size of change that matters. Precision concerns how much the estimate varies, not whether the underlying outcome is large or small.'),
F('A sample proportion has uncertainty determined by successes and sample size',
 'p̂ = successes / n; estimated SE(p̂) = √[p̂(1 − p̂) / n]',
 'For independent binary observations, the sample proportion is their mean. The displayed standard error explains how uncertainty depends on n and the estimated share. Wilson intervals improve coverage relative to the simple symmetric normal interval near zero or one and in smaller samples; the worked exercise reports that interval.'),
]),('theory-method','Test a claim using a specified sampling model',[
B('State the null, alternative, and error costs before testing',[
 'Null hypothesis: the benchmark claim','Alternative: the direction or departure being tested','Type I error: reject a true null','Type II error: fail to reject a false null'],
 'Choose a one-sided alternative when only one pre-specified direction answers the question; choose a two-sided alternative when either direction matters. The significance level controls the probability of rejecting a true null under the testing model. Power is the chance of detecting a specified alternative and depends on effect size, variability, and sample size.'),
F('A test statistic expresses distance from the null in standard-error units',
 't = (estimate − null value) / estimated standard error',
 'Compare this statistic with its reference distribution under the null. The p-value is the probability, under that null model, of a statistic at least as extreme in the direction or directions specified by the alternative. It measures compatibility with the null rather than the probability that the null itself is true.'),
B('The relationship between observations determines the comparison test',[
 'One sample: compare its mean with a benchmark','Paired observations: analyze within-pair differences','Independent groups: compare group means with their own uncertainty','Keep the sampling unit consistent throughout'],
 'Pairing uses the fact that two measurements belong to the same unit. A paired t-test becomes a one-sample test of the differences. Independent-group comparisons use uncertainty from both groups; Welch’s approach allows unequal variances. Select the design from how the data were collected, then choose the corresponding formula.'),
]),('theory-practice','Use repetition and decision thresholds to interpret evidence',[
B('Bootstrap resampling approximates the estimator’s sampling distribution',[
 'Resample the independent units with replacement','Use the original sample size for each bootstrap draw','Recalculate the statistic for every draw','Use the simulated spread or quantiles to summarize uncertainty'],
 'The bootstrap treats the empirical distribution as an approximation to the population distribution. Resampling entire independent units preserves the design information needed for uncertainty. Subsampling without replacement and with fewer observations answers a different repetition question; its raw spread is not automatically the original estimator’s standard error.'),
B('Statistical evidence becomes useful when compared with a meaningful effect',[
 'Report the estimate, interval, and units together','Compare the interval with the decision threshold','Pre-specify key tests and distinguish exploratory findings','Choose additional measurement for the decision it could change'],
 'A small p-value can accompany an effect too small to matter, while an imprecise estimate can leave an important decision unresolved. Read statistical uncertainty together with effect size and the consequences of error. When many comparisons are explored, report that search and seek confirmation for the conclusions that will drive action.'),
])],
4:[('theory-foundations','Define a regression and its fitted values',[
F('Simple regression represents the conditional mean with a line',
 'Yᵢ = α + βXᵢ + uᵢ; fitted value Ŷᵢ = a + bXᵢ',
 'Y is the outcome, X the predictor, α the population intercept, and β the population slope. The error u represents variation around the specified relationship. A linear conditional-mean interpretation uses E[u | X] = 0. The fitted coefficients a and b are estimates obtained from observed data.',
 'An overall mean gives the same prediction to every observation. Group means give different predictions to categories; a fitted line summarizes a continuous relationship using an intercept and slope.'),
F('Ordinary least squares minimizes squared prediction misses',
 'Choose a and b to minimize Σ[Yᵢ − (a + bXᵢ)]²',
 'Each residual is the vertical difference between an observation and its fitted value. Squaring gives larger misses greater influence and makes the loss nonnegative. The fitted line is the one minimizing the sum over the estimation sample. This optimization defines OLS before any uncertainty or causal interpretation is added.'),
F('The slope measures outcome units per additional predictor unit',
 'b = Cov(X,Y) / Var(X); a = Ȳ − bX̄',
 'The slope is positive when X and Y move together and negative when they move in opposite directions. Its magnitude is expressed in units of Y per unit of X. The intercept supplies the fitted value at X=0. Read both coefficients against the units and range of the data.'),
]),('theory-method','Evaluate fit and choose a functional form',[
F('Residuals connect individual prediction misses with model fit',
 'eᵢ = Yᵢ − Ŷᵢ; RMSE = √[Σeᵢ² / n]',
 'A positive residual means the outcome exceeds its fitted value. Residual patterns can reveal systematic features missing from the chosen line. RMSE summarizes the squared misses in the original outcome units. On the estimation sample it describes training fit; performance on new observations requires separate evaluation.'),
F('R-squared describes the share of sample variation explained by OLS',
 'SST = SSR + SSE; R² = 1 − SSE / SST',
 'With an intercept, OLS partitions total squared variation around the sample mean into explained and residual components. SST is total variation, SSR explained variation, and SSE residual variation. R-squared is a relative measure of fit; RMSE reports an absolute error scale. Use both with the residual pattern.'),
B('Log transformations change the meaning of a slope',[
 'Level–level: one X unit corresponds to b Y units','Log–level: one X unit corresponds to approximately 100b% in Y','Level–log: 1% more X corresponds to approximately b/100 Y units','Log–log: 1% more X corresponds to approximately b% more Y'],
 'Choose a functional form from the relationship the model should express. Logs describe proportional changes and require positive values. The percentage interpretations are local approximations for small changes; exact finite changes use the log or exponential transformation. Compare predictions on a common outcome scale when assessing alternative forms.'),
F('Polynomial terms let the marginal association change with X',
 'Ŷ = a + b₁X + b₂X²; slope at X = b₁ + 2b₂X',
 'Read polynomial terms together through the predicted curve. The coefficient of X alone is not a constant slope once X² is included. Higher-order terms provide additional curvature. Plot the resulting predictions over the observed range and ask whether that flexibility captures a useful pattern.'),
F('Splines and local smoothing describe shape with different forms of flexibility',
 'Linear spline: Ŷ = a + bX + c × max(X − knot, 0)',
 'A linear spline changes the slope at a specified knot while keeping the curve continuous. Local smoothing instead fits relationships using nearby observations, often with distance-based weights. Both approaches help examine shape. Their tuning choices control how much detail the curve follows, so compare their implications on the same scale.'),
])],
5:[('theory-foundations','Define the comparison in a multiple regression',[
F('Multiple regression specifies which other variables are held fixed',
 'Yᵢ = β₀ + β₁X₁ᵢ + … + βₖXₖᵢ + uᵢ',
 'A coefficient describes a change in the fitted outcome when its predictor changes and the other included predictors are held fixed. State that comparison explicitly. Variables in the equation determine what is adjusted for; observations determine the population represented. Use complete input profiles when communicating predictions.'),
F('An omitted factor changes a slope through its outcome effect and sorting',
 'β short − β long = γ omitted × δ sorting',
 'Compare a short regression containing X with a longer regression also containing Z, on the same observations. γ is Z’s coefficient in the longer regression. δ is the slope from regressing Z on X. Their product accounts for the change in the X coefficient. A causal interpretation additionally uses the assignment and adjustment argument.'),
B('Indicator variables compare categories with a named reference',[
 'Choose one reference category','With K categories and an intercept, include K−1 indicators','Interpret each coefficient relative to the reference','Use the same coding rules when making predictions'],
 'An indicator takes value one for a category and zero otherwise. Including all categories and an intercept makes one column redundant. The reference category sets the interpretation of the remaining coefficients; it does not remove that category’s observations from the analysis.'),
F('An interaction lets the slope of one predictor depend on another',
 'Ŷ = b₀ + b₁X + b₂Z + b₃XZ; slope in X = b₁ + b₃Z',
 'With a binary Z, the X slope is b₁ in the reference group and b₁+b₃ in the other group. The group difference at a chosen X is b₂+b₃X. For continuous Z, the X slope changes continuously with Z. Interpret the main and interaction terms together at explicitly chosen values.'),
]),('theory-method','Quantify uncertainty and assess the fitted model',[
F('Coefficient uncertainty measures precision of a specified conditional comparison',
 'Large-sample 95% interval = bⱼ ± 1.96 × SE(bⱼ)',
 'A zero-coefficient test compares bⱼ with zero in standard-error units. Robust standard errors allow the residual variance to differ across independent observations. The interval’s target remains the coefficient in the specified model. Changing predictors or reference values can change its interpretation as well as its estimate.'),
B('An individual prediction includes variation beyond uncertainty in the mean',[
 'Mean-response interval: uncertainty about E[Y | X=x]','Prediction interval: uncertainty about a new outcome at x','A new outcome includes residual variation around the mean','Specify the same input profile for both comparisons'],
 'Estimating an average response and predicting one realization are different tasks. A prediction interval includes both coefficient uncertainty and variation of the new outcome around the conditional mean, so it is wider under the same model. The standard simple-regression formula assumes constant residual variance; the worked table makes that specification explicit.'),
B('Fit statistics and residuals reveal complementary aspects of a model',[
 'R-squared summarizes explained sample variation','Adjusted R-squared accounts for the number of fitted parameters','Actual-versus-fitted plots reveal individual misses','Residual patterns suggest what to investigate next'],
 'Adding predictors cannot reduce ordinary training R-squared in nested OLS models. Adjusted R-squared accounts for the degrees of freedom used in fitting. Inspect residuals and plausible input combinations alongside these summaries, then assess future prediction with data not used to select the model.'),
])],
6:[('prediction-task','Define the prediction task and its loss',[
B('Prediction begins with the output needed at the time of action',[
 'Regression predicts a numerical outcome','Classification predicts a category','Probability estimation quantifies outcome risk','Features must be available when the prediction is made'],
 'Define the prediction unit, target, horizon, and information available at the decision time. These determine the learning problem before an algorithm is selected. The target may be a value, category, or probability; each supports a different type of action and requires an appropriate evaluation measure.'),
F('The loss function determines which prediction errors matter most',
 'MAE = mean |Y − Ŷ|; MSE = mean (Y − Ŷ)²; RMSE = √MSE',
 'Absolute loss treats each additional unit of error equally; squared loss gives large errors extra weight. RMSE returns squared loss to the outcome’s units. Under squared loss the population-optimal prediction is the conditional mean; under absolute loss it is a conditional median. Choose the loss to reflect the prediction task.'),
B('Model complexity trades systematic error against estimation variability',[
 'Underfitting misses useful structure','Overfitting follows development-sample noise','More flexible models can have higher sampling variability','Irreducible variation remains after available predictors are used'],
 'Training error generally improves as flexibility increases, but future error need not improve. A simple model can have systematic bias; a flexible fitted model can vary greatly across samples. The bias–variance perspective explains why model selection requires an estimate of performance outside the fitting sample.'),
]),('theory-method','Validate the whole forecasting procedure',[
B('Training, validation, and test data have distinct roles',[
 'Training fits coefficients and transformations','Validation selects features, model type, and tuning parameters','The final test evaluates the selected procedure','Match the split to how new observations will arrive'],
 'Model development includes every choice informed by performance. Reserve final test data until those choices are complete. For predictions about later periods, train on earlier observations and validate on later ones. For repeated units or groups, design splits around the generalization task and its dependence structure.'),
B('Cross-validation repeats the comparison using multiple development splits',[
 'Fit a complete procedure in each training fold','Evaluate it on that fold’s held-out observations','Aggregate errors using the same loss','Use forward-moving windows for time-ordered prediction'],
 'Cross-validation reduces dependence on one arbitrary development split. Random folds suit some independent sampling tasks, while temporal tasks use expanding or rolling windows. Every fold must recreate what was available at its forecast date. Compare candidate procedures on the same eligible observations.'),
B('Preprocessing must be learned inside each training fold',[
 'Fit imputation, scaling, and feature selection on training rows','Apply those fitted rules to validation rows','Keep target definitions and category coding consistent','Refit the chosen pipeline before final evaluation'],
 'A model is the entire pipeline, not only its final regression or tree. Estimating transformations using held-out outcomes or future data makes validation too optimistic. Learn data-dependent preprocessing within the training fold and carry the fitted rules into validation and deployment unchanged.'),
F('LASSO adds a penalty that can set some slopes to zero',
 'Minimize mean squared loss / 2 + α × Σ|slope coefficients|',
 'The tuning parameter α controls the strength of shrinkage. Larger penalties generally produce smaller coefficients and can eliminate some predictors. Standardize features within training so that their measurement scales do not determine the penalty. Select α using development-data prediction error, not final test performance.'),
F('Information criteria trade likelihood fit against model complexity',
 'AIC = −2 log likelihood + 2k; BIC = −2 log likelihood + k log n',
 'Here k is the number of fitted parameters and n the sample size. Both criteria reward fit and penalize complexity, with different penalties. Compare them under consistent likelihood definitions on the same outcome and observations. Validation directly scores predictions on held-out data and therefore answers a related but distinct question.'),
]),('theory-practice','Return predictions to the operating scale',[
F('Exponentiating a fitted log mean does not generally recover the outcome mean',
 'Estimated mean on the Y scale = exp(fitted log Y) × mean[exp(residual)]',
 'The displayed smearing correction uses the distribution of log-model residuals to return predictions to the outcome scale. A common correction factor assumes the relevant residual distribution is stable across predictor profiles. State whether the target is a mean, median, or another quantity before comparing errors in the original units.'),
B('Deployment continues the evaluation with new outcomes',[
 'Record inputs, forecasts, model version, and actions','Monitor prediction errors and decision outcomes','Review changes in data definitions and population','Set a schedule and criteria for updating the model'],
 'Validation supports a decision to use a forecasting procedure under specified conditions. Deployment produces new evidence about those conditions and the procedure’s usefulness. Monitor the same loss and relevant operational outcomes, and distinguish deterioration in prediction from changes in how the forecast is acted upon.'),
])],
7:[('theory-foundations','Define the causal quantity before estimating it',[
F('A causal effect compares two potential outcomes for the same unit',
 'τᵢ = Yᵢ(1) − Yᵢ(0); observed Yᵢ = DᵢYᵢ(1) + (1−Dᵢ)Yᵢ(0)',
 'D indicates treatment assignment. Y(1) is the outcome under treatment and Y(0) under the comparison condition. Their difference defines an individual causal effect. Only the assigned outcome is normally observed, leaving the other as a counterfactual. Identification requires a design that supplies a credible comparison.',
 'This theory uses treatment minus control as the effect convention. When a smaller outcome is desirable, an improvement is a negative effect; the retail application reports its negative as a positive reduction.'),
F('ATE, ATT, and ATU average effects over different populations',
 'ATE = E[τ]; ATT = E[τ | D=1]; ATU = E[τ | D=0]',
 'ATE is the average treatment effect for the named population. ATT averages effects among treated units and ATU among untreated units. When effects differ across units, these targets need not coincide. Specify the population before choosing which average answers the decision.'),
F('The population effect combines treated and untreated group effects',
 'ATE = P(D=1) × ATT + P(D=0) × ATU',
 'The law of total expectation expresses the overall average using the two groups’ shares. The identity is about potential outcomes and population weights; it does not by itself identify those outcomes from observed data. It explains why a change in the target population can change the average effect.'),
F('An observed mean difference combines a causal effect with selection',
 'E[Y | D=1] − E[Y | D=0] = ATT + E[Y(0) | D=1] − E[Y(0) | D=0]',
 'The final two terms compare the groups under the same untreated condition. They capture selection into treatment: groups could have differed even without treatment. This decomposition shows exactly what randomization or an observational adjustment strategy must address before the observed difference can be interpreted causally.'),
]),('theory-method','Use random assignment to construct the comparison',[
B('Random assignment makes treatment independent of potential outcomes',[
 'Define eligibility before assignment','Assign treatment using a recorded random procedure','Measure the same outcome over the same follow-up period','Analyze uncertainty at the assignment unit'],
 'Under random assignment, treatment and control groups represent the same potential-outcome distributions in expectation. Their mean difference estimates the average effect for the experimental population. A particular draw may contain chance imbalance, which is handled through sampling uncertainty. Assignment records establish the procedure.'),
B('A well-defined intervention connects assignment with the outcome contrast',[
 'Specify the treatment and comparison versions','Track delivery and participation','Design assignment to handle spillovers between units','Pre-specify primary outcomes and operating guardrails'],
 'Consistency links the observed treatment to its defined potential outcome. No interference means one unit’s treatment does not alter another unit’s outcome. Together with a well-defined treatment, these conditions are often grouped under SUTVA. If interactions occur within groups, consider assigning and analyzing at that group level.'),
F('A treatment-indicator regression reproduces the difference in means',
 'Yᵢ = a + bDᵢ + eᵢ; b = treated mean − control mean',
 'With an intercept and a binary treatment indicator alone, the fitted values are the two group means. The treatment coefficient is their difference. The regression and difference-in-means calculations therefore express the same comparison; use uncertainty appropriate to the assignment unit and design.'),
B('Controlled and natural experiments differ in the source of assignment',[
 'Controlled experiment: the study team assigns treatment','Natural experiment: an external rule or event supplies variation','Both require a credible counterfactual comparison','Document eligibility, timing, and implementation'],
 'The defining issue is how the comparison is created. In a controlled randomized experiment, the assignment procedure is designed directly. A natural experiment uses external variation whose operation must support comparability. Understanding that mechanism determines what causal contrast can be learned.'),
]),('theory-practice','Translate an effect into a decision',[
F('The intervention pays when its expected benefit exceeds its cost',
 'Net benefit = value per unit improvement × improvement − intervention cost',
 'Translate the estimated effect and its interval using the stated business valuation. Dividing intervention cost by value per unit improvement gives a break-even threshold. A zero-effect hypothesis and a break-even decision answer different questions. Keep implementation outcomes and the review horizon alongside the financial calculation.'),
])],
8:[('identification','State the observational identification argument',[
B('Conditional exchangeability compares units with the same relevant starting conditions',[
 '(Y(0), Y(1)) independent of D given X','X contains the common causes needed for adjustment','Both treatment options occur at relevant X values','The intervention and outcome are defined consistently'],
 'Conditional exchangeability says that, after conditioning on X, treated and untreated units have comparable potential-outcome distributions. Positivity supplies observations under both options at the profiles relevant to the target. These are the conditions that give an adjusted comparison its causal interpretation; knowledge of the assignment process guides the choice of X.'),
B('A causal diagram records an argument about how variables are connected',[
 'Nodes represent variables; arrows represent proposed direct causal links','A directed acyclic graph has no directed feedback cycle','Time ordering helps distinguish causes from consequences','Evaluate paths relative to the chosen intervention and outcome'],
 'A DAG makes substantive assumptions visible before selecting controls. It describes proposed causal links rather than merely observed correlations. A path is a sequence of connected nodes; whether it transmits association depends on arrow directions and what is conditioned on. The three basic structures establish the rules.'),
]),('theory-method','Read paths before choosing controls',[
F('Conditioning on a mediator blocks part of a causal pathway',
 'Chain: D → M → Y',
 'M is a mediator on this path: treatment changes M and M changes the outcome. Conditioning on M blocks the pathway through it. For a total-effect question, retain that pathway. A direct-effect question requires a different target and additional identification conditions.'),
F('Conditioning on a common cause blocks a backdoor path',
 'Fork: D ← X → Y',
 'X is a common cause of treatment and outcome. The open path through X creates an association beyond the causal effect of D. Conditioning on X blocks this path and compares units with the same relevant starting condition. This is the basic logic of confounding adjustment.'),
F('Conditioning on a collider can open a previously blocked path',
 'Collider: D → C ← Y',
 'The two arrows meet at C, making C a collider on this path. Without conditioning, the path is blocked. Selecting or adjusting for C, or a descendant of C, can open it. Variable roles are path-specific, so evaluate the complete set of relevant paths rather than labeling a variable universally safe or unsafe.'),
B('Backdoor adjustment blocks noncausal paths and preserves the total-effect pathway',[
 'Find paths entering treatment through an incoming arrow','Block those paths with an appropriate adjustment set','Avoid treatment descendants in the standard backdoor set','Check the implied open and blocked paths'],
 'The backdoor criterion gives a sufficient graphical rule for identifying a total effect. Choose a set that blocks the noncausal treatment–outcome paths while preserving causal pathways. Proxies can carry information about unmeasured causes; their usefulness depends on what the diagram and measurement process justify, rather than on correlation alone.'),
]),('theory-practice','Turn conditional comparisons into a population effect',[
B('Subclassification estimates effects within comparable groups',[
 'Define strata using pre-treatment characteristics','Compare treated and untreated outcomes inside each stratum','Check representation of both options','Combine stratum effects using target-population weights'],
 'Subclassification makes adjustment visible as a sequence of within-group comparisons. Under the identification conditions, each comparison estimates an effect for its stratum. Broad strata may leave relevant differences within groups, motivating more detailed regression or matching in the next lecture.'),
F('Different target populations require different weights on the same conditional effects',
 'ATE = Σₓ τ(x)P(X=x); ATT uses P(X=x | D=1); ATU uses P(X=x | D=0)',
 'The conditional effect τ(x) is held fixed while the weighting distribution changes. All-unit, treated-unit, and untreated-unit averages can differ because their populations have different characteristics. Name the population and confirm that the weights sum to one before calculating the overall effect.'),
B('A graph is useful when people can inspect and defend its assumptions',[
 'Explain the timing and mechanism behind each arrow','Distinguish measured variables, proxies, and latent causes','Name the effect and adjustment set','Use software to check the graph’s implications'],
 'Domain knowledge supplies the causal structure. Software or AI can help draw a graph and check path rules once that structure is specified. Discuss why each link belongs, what has been measured, and which alternative explanations matter to the comparison. This makes the statistical adjustment a transparent argument.'),
])],
9:[('theory-foundations','Define the observational comparison and its target',[
B('A target trial specifies the causal question before choosing an estimator',[
 'Define eligibility and the decision time','Specify treatment and comparison strategies','Fix follow-up, outcome, and target population','Explain how the observed assignment differs from that trial'],
 'An observational analysis can be organized around the experiment we would ideally run. This specification aligns treatment, measurement, and follow-up, and clarifies which records belong in the analysis. It also identifies the assignment differences that the adjustment method must address.'),
B('Endogeneity arises when assignment is related to outcome determinants',[
 'Common causes influence both treatment and outcome','Reverse direction makes treatment respond to outcome pressure','Measurement error can leave relevant differences unresolved','Use the causal model to choose pre-treatment adjustment variables'],
 'Adding predictors is useful only in relation to the stated comparison. Confounding, reverse direction, and measurement error can each connect treatment with the outcome error term. The preceding lecture’s graph provides the adjustment argument; this lecture develops ways to implement it under exchangeability, overlap, and consistency.'),
B('Internal and external validity concern different populations and claims',[
 'Internal validity: identify the effect for the study population','External validity: apply the result to a new target population','State eligibility, exclusions, and missing-data rules','Retain the target when comparing estimation methods'],
 'A well-identified study effect may require adaptation to a different population. Trimming observations or excluding unmatched units can also change the target within the study. Keep the population visible when comparing estimates so that a difference between methods is not confused with a difference between the people or organizations represented.'),
]),('theory-method','Estimate adjusted outcomes or construct comparable matches',[
F('Regression standardization averages paired policy predictions for the target population',
 'Estimated ATE = mean over target units of [m̂(1,Xᵢ) − m̂(0,Xᵢ)]',
 'Fit an outcome model m(D,X), then predict each target observation twice: once under treatment and once under control, keeping X fixed. Average the paired differences. For an ATT target, average over treated units. Interactions allow the predicted treatment effect to vary with the covariates.'),
B('Matching specifies which untreated observations represent each treated unit',[
 'Exact matching requires the same covariate values','Coarsened matching compares units within declared bands','Nearest-neighbor matching uses a specified distance','State replacement, calipers, exclusions, and target population'],
 'A matching rule turns the idea of comparability into a reproducible procedure. A caliper limits the maximum acceptable distance; matching with replacement allows one control to serve several treated units. Report retained units and the resulting target. The distance rule and reuse also matter for uncertainty.'),
F('A propensity score summarizes treatment probability given starting characteristics',
 'e(X) = P(D=1 | X)',
 'Under conditional exchangeability, the true propensity score is a balancing score for the observed covariates. Estimate it from pre-treatment information and use it to construct comparisons. A fitted score must still be evaluated for overlap and balance on the actual covariates; a good treatment-prediction score alone does not establish a good causal comparison.'),
F('Standardized mean differences measure balance on a common scale',
 'SMD = (treated mean − comparison mean) / pooled pre-match SD',
 'Using a fixed pre-match denominator makes before-and-after balance comparable. When controls are reused, weight them according to their contribution to the matched sample. Inspect relevant covariates and local overlap, not only the range of propensity scores. Balance diagnoses the observed comparison that the estimator uses.'),
]),('theory-practice','Interpret estimates for the population actually represented',[
B('Regression and matching should be compared for the same target',[
 'Keep eligibility, outcome, and follow-up aligned','Name the target of each estimate','Report unmatched units and model specifications','Compare sensitivity to reasonable adjustment choices'],
 'Regression can predict for a specified population, while matching often estimates an effect among retained treated units. Before comparing their numbers, align those targets and inspect where each obtains its counterfactual information. Agreement is useful evidence about the specification choices; the identification argument continues to come from the study design.'),
])],
10:[('theory-foundations','Define the two-group, two-period comparison',[
B('Difference-in-differences compares changes across treated and comparison groups',[
 'Two groups: treated and comparison','Two periods: before and after treatment','The same outcome definition in all four cells','Stable identifiers preserve the unit-level history'],
 'A before-and-after change combines the intervention with background changes over time. Difference-in-differences uses a comparison group to estimate that background movement. A panel follows the same units across periods, allowing their changes to be calculated directly; define the eligible units and period averages before fitting the model.'),
F('Subtracting the comparison trend removes the shared background change',
 'DiD = (treated after − treated before) − (comparison after − comparison before)',
 'The formula is a treatment-minus-control contrast in changes. The implied untreated outcome for the treated group is its pre-period mean plus the comparison group’s change. Under the identification conditions, the difference from the observed treated outcome estimates the average effect on the treated group.',
 'This lecture uses the conventional signed outcome effect in theory. The retail application reports its negative as a positive reduction in stockouts.'),
F('Parallel trends identifies the missing untreated change for the treated group',
 'E[ΔY(0) | D=1] = E[ΔY(0) | D=0]',
 'The groups may begin at different levels. Parallel trends requires their average untreated changes over the policy period to be the same. With no anticipation of treatment and a stable comparison, the observed control change then supplies the treated group’s missing no-treatment change. Examine the operating history and contemporaneous events to defend that comparison.'),
]),('theory-method','Express the same contrast through regression and first differences',[
F('The group-by-period interaction equals the two-by-two DiD',
 'Yᵢₜ = a + bDᵢ + cAfterₜ + d(Dᵢ × Afterₜ) + eᵢₜ',
 'The intercept is the comparison mean before treatment. b is the initial group difference, c is the comparison group’s change, and d is the additional treated-group change. With the same observations and weights, d reproduces the four-cell calculation. This connects the interaction model to an identifiable comparison rather than a coefficient label alone.'),
F('First differences remove each unit’s time-invariant level',
 'ΔYᵢ = a + bDᵢ + uᵢ',
 'With two periods, differencing reduces the analysis to one change per unit. The treated-minus-comparison difference in those changes recovers the DiD. Preserve the independent unit in the uncertainty calculation; additional repeated rows do not create additional independent assignments.'),
B('Pre-trends, controls, and subgroups address specific parts of the comparison',[
 'Inspect pre-treatment paths and placebo changes','Use baseline covariates to model differences in trends','Report subgroup counts and uncertainty','State weights according to the target population'],
 'Pre-period evidence helps diagnose whether the proposed comparison is plausible, together with knowledge of the business history. Baseline covariates can allow different changes for units with different starting conditions. Subgroup and weighted analyses answer more specific target questions, so retain their sample sizes and definitions beside the estimate.'),
F('A continuous-treatment interaction measures change per unit of a defined exposure',
 'Yᵢₜ = unit terms + time terms + β × exposureᵢ × Afterₜ + eᵢₜ',
 'Replacing a binary treatment indicator with a pre-defined continuous exposure changes the target to an effect gradient. Specify the exposure unit and the corresponding trend assumption. The shared worked case uses a binary intervention; this generalization shows how the same interaction logic extends when an appropriate dose is observed.'),
]),('theory-practice','Complete the causal and business interpretation',[
B('A DiD result belongs to a named population, period, and trend argument',[
 'State the groups, dates, and outcome','Explain the untreated trend comparison','Report the effect and uncertainty in outcome units','Translate the result using the decision’s cost rule'],
 'The final interpretation should connect the design, estimate, and decision. Identify who was treated, which comparison supplies the missing path, and when the effect applies. Translate the outcome effect into a business consequence only after that statistical target is clear, and state how the next implementation will be reviewed.'),
])],
}

def theory_sections(n):
    sections=[]
    titles={}
    for key,heading,blocks in THEORY[n]:
        sections.append(dict(**section(key,heading,''.join(html for _,html in blocks)),phase='General theory'))
        titles[key]=[title for title,_ in blocks]
    return sections,titles
