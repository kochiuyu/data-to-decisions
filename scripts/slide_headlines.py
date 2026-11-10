"""Read each lesson's titles in order to follow its argument.

Each line names one source section; | separates its visual frames. Questions
preserve discussion and reveal moments; statements express supported takeaways.
"""

def sequence(text):
    return {key.strip(): [s.strip() for s in titles.split('|')]
            for line in text.strip().splitlines()
            for key,titles in [line.split(':',1)]}


MAIN = {
1: sequence('''
main: Should we test alerts to reduce empty shelves?
decision-brief: Establish a trustworthy stockout baseline before testing alerts
evidence: The spending decision starts with comparable shelf-availability data | Build a baseline another analyst can reproduce | Choose data sources that capture the operating question | Agree what stockouts mean and how stores report them
read-data: Each store-week contains 140 opportunities to keep products available | Store and week together identify each stockout count
coverage: Define the target stores before selecting the observed sample | More rows cannot replace missing stores | Scale data collection around volume, speed, variety, and reliability
structure: Different table structures reveal differences across stores or time | Measurement scales determine which calculations make sense | Choose a file format that preserves the documented variables | Inspect rows, types, and missing values before filtering | Select rows and columns using explicit business rules | Give every observation a unique, stable key | Check missing and repeated keys before removing records
calculate: Reconcile duplicates and flagged counts before calculating stockout rates | Recover missing counts from the source ledger | Divide stockout counts by scheduled product-days
reshape: Long format keeps each store-week on its own row | Wide format puts weekly values side by side | Reshape around the store-week key to preserve observations
relationships: Define the relationship before joining two tables | A store-profile join should preserve the number of weekly rows | Manager responsibility depends on the assignment dates | Match each week to the manager responsible then | Date filtering removes invalid store-manager pairings | One transfer produces both an incoming and an outgoing record
aggregation: Aggregating weekly records creates a store-level measure | Show reporting coverage beside each store's rate | Apply minimum reporting coverage before ranking stores
interpret: Stockouts exceed the service target on the reconciled baseline
workflow: Preserve inputs and document each step from source to result | Organize raw data, repaired data, and analysis separately | Use AI for work with explicit rules and checkable results | Which repeated records are errors, and which are valid observations?
act: Hand over the baseline with definitions and a repair log
memo: Use the same reconciled baseline for the rest of the decision | How should a missing weekly count enter the stockout rate?
big-picture: A shared measurement agreement makes business evidence comparable | Did reconciliation recover the original store-week records?
'''),
2: sequence('''
main: Where should the chain investigate stockouts first?
decision-brief: Build a store shortlist from the severity and breadth of stockouts
explore: Inspect the distribution before choosing a summary | Match the chart to the business question
read-data: Average each store's eight weeks before comparing stores
distributions: Most stores cluster between 8% and 16% stockouts | The 12%–16% band contains the largest number of stores | Report both the typical rate and the spread across stores | Variance measures squared distance from the average | Standard deviation and IQR summarize spread in the original units | A boxplot shows the median, middle half, and extremes | Quartiles and density reveal the shape behind the average | The baseline distribution is nearly symmetric | Use common scales and group shares for comparable charts
calculate: Compare each delivery group against its own store count | Long-lead stores have higher average rates and broader target misses | Almost all long-lead stores exceed the service target
interpret: Separate differences across stores from movement over time | The chain stays above target throughout the baseline | Weeks one through six show a persistent service gap | The final baseline weeks remain above target
association: High stockout rates are more common among long-lead stores | A conditional mean describes the group named in the question | Higher-demand groups generally have higher stockout rates | Equal-sized demand bins make group averages easy to compare | Correlation expresses co-movement on a standardized scale | Demand and stockout rates are positively associated
act: Turn the observed burden into an identifiable review shortlist | Start reviews with the stores showing the highest baseline rates
memo: Allocate review effort using severity, coverage, and store identity | Which stores belong in the denominator for long-lead target misses?
big-picture: Distributions turn an average problem into a resource-allocation decision | Do these different summaries describe the same underlying stores?
'''),
3: sequence('''
main: Is the audit precise enough to justify further action?
decision-brief: Compare a fresh 30-store audit with the service target
read-data: Treat each sampled store as one audit observation | Each audited store contributes a count and a stockout rate
sampling-variation: Different samples produce different estimates of the same target | More independent stores reduce the standard error of the mean | A share above target needs its own uncertainty interval
calculate: Combine the sample mean with its standard error | Divide store-level spread by the square root of sample size | Add and subtract the margin of error to form an interval
interpret: The entire audit interval lies above the service target
resampling: Bootstrap whole stores to reproduce the sampling unit | Analytical and bootstrap intervals tell a similar story | Smaller subsamples answer a different precision question
testing: State the service-gap hypothesis before examining the result | Measure the target gap in standard-error units | The p-value depends on whether the test is one-sided or two-sided | Weigh false alarms and missed problems against their business costs | Choose the test from how observations are related | The paired audit-system interval includes zero difference | What should follow a selectively reported small p-value?
act: Buy more information when it could change the action
memo: The audit supports investigating the replenishment problem | Should precision count independent stores or product-days?
big-picture: Sample size should serve the decision the evidence must support | How close did the audit come to the known population rate?
'''),
4: sequence('''
main: How does stockout pressure vary with delivery time?
decision-brief: Use a fitted line to summarize delivery-related operating pressure
read-data: Pair each store's delivery time with its baseline stockout rate | Average stockout rates rise across longer delivery cycles | Five-day delivery stores have the highest group average
from-bins: Move from one chain average to store-specific predictions | Least squares chooses the line with the smallest squared misses | The slope divides co-movement by variation in delivery time
calculate: Read the delivery slope in percentage points per day | Combine an intercept and delivery slope to predict the rate | Substitute four delivery days to predict a store's baseline rate
interpret: Residuals identify stores above or below their fitted benchmark | Compare each observed rate with its prediction
fit: Split total variation into explained and residual components | R-squared reports the share of variation explained by the line | RMSE expresses fitting error in stockout percentage points
functional-form: Transformations change what a regression coefficient means | Compare functional forms on the same stockout-rate scale | Additional curve terms produce little improvement in training error | A spline lets the delivery slope change at a chosen point | Local smoothing shows how rates vary across nearby demand values | At the highest displayed demand, the smoothed rate remains elevated
act: Use residuals to guide the next investigation of store conditions
memo: Longer delivery cycles are associated with higher baseline stockout rates | How does a positive residual differ from a positive slope?
big-picture: A useful model explains a recognizable store in business units | Which operating factors lie behind the simple fitted line?
'''),
5: sequence('''
main: How can we compare stores with different operating conditions?
decision-brief: Add store context to make the comparison explicit
regression-uncertainty: Read each coefficient alongside its uncertainty interval | Predicting one new store requires a wider interval than predicting a mean
read-data: Specify delivery, location, demand, and promotion exposure together
calculate: Allow the delivery slope to depend on location | The interaction adds a separate urban delivery component | Each coefficient belongs to a defined input and reference | Add the interaction coefficient to obtain the urban delivery slope
controls: Omitted-variable bias combines an outcome effect with sorting | Adding location changes the fitted delivery coefficient | The omitted-variable identity accounts for the coefficient change | Category coefficients compare with a named reference group | An interaction makes one variable's slope depend on another | Review residuals as well as overall goodness of fit
interpret: Hold demand and promotions fixed when comparing operating profiles | Urban and nonurban profiles imply different delivery-related increases
residual-review: Review stores whose stockouts exceed their profile-based prediction | How would you explain the interaction using two store profiles?
act: Carry the profile comparison forward into forecast design
memo: Report delivery slopes separately for urban and nonurban stores | Why does the urban delivery slope combine two coefficients?
big-picture: Holding factors fixed means specifying the comparison in full | Does the richer model reflect the case's operating mechanism?
'''),
6: sequence('''
main: Which stores will need attention next week?
decision-brief: Select a forecasting rule using information available before action
prediction-task: Define whether the decision needs a rate, category, or probability | Choose an error measure that reflects the cost of misses | Balance missed structure against fitting development-sample noise
read-data: Put every forecast input on the decision clock | Only previously observed or planned information enters the forecast
calculate: Train first, validate later, and reserve the final weeks | Linear regression beats the small tree on validation error
validation-design: Move validation forward to imitate repeated forecasting | Information criteria and validation score different aspects of a model | Fit preprocessing within the training procedure
interpret: Evaluate the chosen rule on later, untouched weeks | Individual forecast misses reveal where the final error comes from | RMSE summarizes squared misses across all final test store-weeks
lasso: LASSO penalizes large coefficients as well as prediction error | Choose the penalty using development-period forecasts | The tuned LASSO and original model have similar final errors | Retained features show how the LASSO forecast combines available information | Return log predictions to the intended business scale | Monitor forecasts, actions, and costs after deployment
act: Turn predicted risk into a queue for operational review | Review the highest predicted risks for the next planning week
memo: Use the validated forecast to prioritize attention | Can today's forecast use next week's realized demand?
big-picture: Prediction helps allocate attention; evaluation tests whether the action works | What sources of variation remain behind forecast errors?
'''),
7: sequence('''
main: Do replenishment alerts improve service enough to pay for themselves?
decision-brief: Randomly offer alerts before comparing outcomes and costs
counterfactuals: Define the alert offer, eligible store, and follow-up outcome | A store's policy effect compares its two potential outcomes | Average effects refer to different groups of stores | The all-store effect combines treated and untreated group effects | Assignment determines which potential outcome becomes observed
read-data: Assign alerts by store and measure eight-week outcomes consistently | Store-level records connect assignment, service, and operating cost
experiment-design: Check starting conditions after random assignment | Deliver a consistent intervention and measure both groups alike | Experimental designs differ in who assigns the policy
calculate: The randomized comparison estimates a reduction in stockouts | Offered stores have lower average stockouts and operating costs | Subtract the offered mean from the usual-operation mean
interpret: Translate the service improvement into a net saving | The alert fee sets a positive break-even improvement | Avoided stockout charges exceed the alert fee at the point estimate
experiment-value: A treatment-indicator regression reproduces the group comparison | Track service gains, implementation, and operating guardrails together | How does the randomized estimate compare with both potential paths?
act: Fund a measured next phase and track its implementation
memo: The pilot supports staged expansion with continued measurement | Why must the break-even stockout reduction exceed zero?
big-picture: Combine a credible policy comparison with a business cost threshold | How close is the pilot estimate to its known expected effect?
'''),
8: sequence('''
main: What can voluntary adoption tell us about alert effectiveness?
decision-brief: Reconstruct why stores adopted before comparing their outcomes
identification: Compare policy options conditional on relevant starting conditions | Build within-group comparisons before averaging across stores
read-data: Starting conditions precede both adoption and later stockouts | Delivery, location, and baseline performance shape the comparison
calculate: Use delivery groups containing adopters and nonadopters | Adopters begin with longer deliveries and higher stockout rates | Within both delivery groups, adopters have lower follow-up rates
graph-structures: Earlier review is a pathway through which alerts can work | Delivery conditions can influence both adoption and stockouts | Selecting on escalation can create a misleading association | A variable's position on the path determines adjustment's effect | Block common-cause paths while retaining the total policy pathway | Baseline performance can provide information about store capability | Should total-effect estimation adjust for post-alert review effort?
interpret: Weight group effects to represent the proposed rollout population | Larger groups contribute more to the all-store average | Sum weighted contributions to obtain the standardized reduction
target-weights: All stores, adopters, and nonadopters require different weights | Changing the target population changes the weighted estimate | Make the causal diagram an inspectable business argument
act: Document the comparison design before fitting the fuller model
memo: Carry starting conditions into the next adjustment step | Is an alert-triggered emergency order a baseline control?
big-picture: Business timing and the target population guide the comparison | Which starting conditions actually drive adoption in this case?
'''),
9: sequence('''
main: How much would alerts help the intended rollout population?
decision-brief: Predict both policy options for the same target stores
ideal-experiment: Reconstruct the trial the business would like to run | Explain how adoption becomes related to potential outcomes | Distinguish identifying the study effect from applying it elsewhere
read-data: Keep the outcome period and target stores fixed
calculate: Average paired policy predictions over the spending population | Each store receives a usual-operation and an alert prediction | The average prediction difference estimates the all-store reduction
interpret: The adopter-target estimate differs from the all-store estimate
matching-options: Richer adjustment changes the estimated reduction | Matching rules change which adopters receive a comparison | A propensity score predicts adoption from starting conditions | Check whether adopters and nonadopters have comparable adoption probabilities | Matching improves delivery balance but leaves other imbalances | Whose effect remains when stricter matching excludes adopters?
act: Compare matching and regression for the same adopter target | Inspect the actual comparison stores behind the matched differences
memo: Attach every reported effect to its target population | Which regression average belongs beside the matching estimate?
big-picture: The expected gain depends on which stores the business plans to serve | Do estimates approach the known effect for the corresponding target?
'''),
10: sequence('''
main: Did expansion improve service beyond the existing network trend?
decision-brief: Compare changes for rollout stores and comparison stores
read-data: Follow the same stores before and after rollout | The rollout groups' stockout paths converge after alerts begin | Weeks one through six show higher stockouts among future adopters | Future adopters remain higher through weeks seven to twelve | The level gap persists as the pre-rollout period approaches | Weeks nineteen through twenty-four establish the immediate comparison baseline | After rollout, adopters' rates fall below the comparison group's | The final two weeks retain the reversed ordering
panel-design: Two groups and two periods define the basic comparison | Preserve store identities and state the business weighting rule | Parallel trends supplies the missing no-rollout change
calculate: Subtract the adopter change from the comparison change | Adopter rates fall while comparison-store rates rise | The difference in changes estimates the rollout reduction
interpret: Connect the comparison trend to the stores' operating history
did-regression: The group-by-period interaction represents difference-in-differences | A negative outcome interaction becomes a positive stockout reduction | The pre-period placebo interval includes zero trend difference | Adjusting baseline-related changes produces a smaller estimated reduction | Report subgroup effects with their store counts | Planning weights express which stores matter to the decision | A continuous-treatment model needs a clearly defined dose | What evidence belongs beside the expansion recommendation?
act: Combine the three studies into a staged expansion decision
memo: The rollout estimate supports expansion under the stated cost rule | Why does before-and-after improvement differ from the policy reduction?
big-picture: Connect measurement, prediction, and evaluation to the next business action | How close is the rollout estimate to the known adopter effect?
''')}

APPENDIX = {
1: sequence('''
main: Reproduce the baseline from source records to a validated handover
data: Store-week keys and exposure define valid analysis rows
calculation: Repair flagged counts before checking keys and totals | Deduplicate records and reconcile counts against the repair ledger | Reshape the cleaned data and validate the store-profile join | Use assignment dates to recover valid weekly responsibilities | Retain stores meeting the minimum reporting-coverage rule
uncertainty: Equal exposure makes simple and exposure-weighted means agree
extension: Changing exposure changes the appropriate weight in the pooled rate
known-answer: Reconciliation recovers the original store-week records
'''),
2: sequence('''
main: Reproduce how distributions direct the store-review effort
data: Each baseline store contributes one eight-week average
calculation: Use each group's store count in its summaries | Calculate group rates, threshold shares, and histogram counts | Verify store-level spread and demand correlation
uncertainty: Baseline descriptions cover the full released store population
extension: Changing the service threshold changes the review workload
probability: Probabilities describe distributions of possible outcomes | A random variable assigns a number to an uncertain outcome | Choose a probability model suited to the observation | Subtract the overlap when combining event probabilities | Conditional probability restricts the comparison to the conditioning event | Bernoulli and binomial moments connect probabilities to expected counts
known-answer: Grouping changes the view of the same baseline stores
'''),
3: sequence('''
main: Reproduce the audit's estimate and decision-relevant uncertainty
data: Thirty sampled stores represent the week-sixteen audit target
calculation: Build the interval from the mean and its standard error | Calculate the store-level t interval | Resample whole stores to estimate bootstrap uncertainty | Pair audit and system readings by store identity
uncertainty: Store-level spread includes differences across stores and measurement variation
extension: Repeat sampling to study how sample size affects precision
inference-details: Evaluate an estimator through its repeated-sampling behavior | Tests and intervals both scale the estimate by its standard error | Bootstrap percentiles give the endpoints of a resampling interval
known-answer: Compare the sample mean with the known expected audit rate
'''),
4: sequence('''
main: Reproduce the delivery relationship and compare model forms
data: One baseline row per store supplies delivery time and stockout rate
calculation: Least squares produces fitted values and residuals | Fit the delivery line and calculate its prediction misses | Partition variation and fit the log-outcome model | Apply residual smearing when returning predictions to the rate scale
uncertainty: Training RMSE measures error on the fitted observations
extension: Compare residual patterns before adding model terms
regression-details: Derive coefficients and compare predictions in business units | Covariance and predictor variance determine the fitted slope | Polynomial slopes change with the predictor's value | Recover the variance decomposition from fitted values and residuals
known-answer: The simple line summarizes several underlying operating factors
'''),
5: sequence('''
main: Reproduce store comparisons with controls and interactions
data: Keep baseline stores fixed while adding operating context
calculation: Construct the interaction before calculating profile predictions | Fit the model and recover both location-specific delivery slopes | Verify how location changes the delivery coefficient
uncertainty: Coefficient, mean-response, and individual-prediction uncertainty have different targets
extension: Compare complete operating profiles and their residual patterns
multiple-regression-details: The design matrix specifies the comparison the model makes | Full column rank allows a unique least-squares coefficient solution | Omitted-variable bias combines the omitted effect with sorting
known-answer: The case mechanism lets delivery effects vary by location
'''),
6: sequence('''
main: Reproduce a forecasting procedure that respects the decision clock
data: Use lagged outcomes and planned inputs for each store-week
calculation: Separate model fitting, model selection, and final evaluation | Split the timeline and fit candidate forecasting models | Select on validation error before evaluating the final period | Build expanding-window folds for LASSO tuning | Compare fold errors to choose the penalty
uncertainty: Evaluate final errors without using them to tune the model
extension: Hold the validation design fixed when comparing a model change
prediction-details: Tune model complexity within the training pipeline | AIC and BIC penalize likelihood fit for model complexity | Fit transformations, scaling, and LASSO together within each fold
known-answer: Outcome randomness and persistent store differences shape prediction errors
'''),
7: sequence('''
main: Reproduce the randomized pilot's service and cost comparison
data: Average follow-up weeks within each of the fifty pilot stores
calculation: Compare randomized store means with a Welch interval | Calculate the randomized reduction from store-level averages | Recover potential-outcome averages for treated and untreated stores
uncertainty: Translate the effect interval into the same cost units
extension: Changing the fee changes the break-even improvement
potential-outcomes: Two potential paths define each store's policy effect | The known-outcome table reveals each store's realized reduction | The observed contrast combines the adopter effect and baseline selection
known-answer: Compare the randomized estimate with the pilot population's expected effect
'''),
8: sequence('''
main: Reproduce the selection argument and target-population weighting
data: Use follow-up averages for the fifty voluntary-cohort stores
calculation: Weight within-stratum contrasts for the target population | Calculate delivery-group reductions and their population-weighted sum | Reweight the same effects for adopters and nonadopters
uncertainty: Broader adjustment incorporates starting differences beyond delivery groups
extension: Adopter weights shift the target from all stores to adopters
graph-details: Adjustment depends on a variable's role in the causal paths | Common causes and selected common consequences create different paths | Target-specific weights connect conditional effects to population averages | Adjustment changes the estimate differently in chains, forks, and colliders | Simulate the review pathway to trace its total policy effect
known-answer: Adoption depends on delivery time, location, and baseline performance
'''),
9: sequence('''
main: Reproduce adjusted policy effects for a named store population
data: Include adoption interactions to allow different store-level gains
calculation: Average paired model contrasts for the target rows | Fit the outcome model and predict both policy options | Prepare starting conditions for the adoption-propensity model | Calculate logit distances and identify candidate matches | Apply the caliper and average retained matched differences
uncertainty: Estimate uncertainty for the target population's average contrast
extension: Track distances, reused controls, and retained adopters
matching-details: Specify similarity, exclusions, and deterministic tie-breaking | Standardized mean differences measure balance on starting variables
known-answer: All-store and adopter effects have different known targets
'''),
10: sequence('''
main: Reproduce the rollout effect from paired store-level changes
data: Preserve each store's before-and-after pairing
calculation: Four group-period means recover the difference in changes | Calculate paired changes for adopters and comparison stores | Fit the group-by-period interaction to recover the same contrast
uncertainty: Independent stores determine uncertainty in the change comparison
extension: Review pre-trends and subgroups against the stated target
did-details: First differences preserve the two-period policy comparison | Regress store-level changes on adoption to recover the signed effect
known-answer: Compare the rollout estimate with the same adopters' known effect
''')}

from lesson2_depth import PROBABILITY_TITLES
APPENDIX[2]['probability'] = ['Probability connects event definitions with weighted numerical summaries'] + PROBABILITY_TITLES
APPENDIX[2]['calculation'] = [
    "Use each group's store count in its summaries",
    'Calculate group rates, threshold shares, and histogram counts',
    'Centered products reproduce covariance and standardized correlation',
    'Recalculate quartiles, correlations, and category shares within delivery groups',
    'Check density normalization and the equal-count bin averages',
]

from lesson3_depth import DETAIL_TITLES
APPENDIX[3]['inference-details'] = ['Sampling design links the estimator to its uncertainty calculation'] + DETAIL_TITLES
APPENDIX[3]['calculation'] = [
 'Build the interval from the mean and its standard error',
 'Calculate the store-level t interval from the observed audit',
 'Resample whole stores and test the service benchmark',
 'Match readings by store before calculating the paired standard error',
 'Complete the paired test and form independent-group variance contributions',
 'Use Welch degrees of freedom for the independent comparison',
 'Reconstruct Wilson endpoints and retain every plotted difference',
]


for titles in APPENDIX.values():
    titles['generation'] = [
        'One shared retail world generates all three policy studies',
        'Operating conditions determine risk and heterogeneous alert effects',
    ]
