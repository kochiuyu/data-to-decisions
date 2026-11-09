"""Audience cues paired with the existing lesson prose, never a second deck.

The build embeds these cues in the relevant reading block. Presentation mode
uses the cues on screen and that block's original paragraphs as teaching notes.
"""
from html import escape
import re


def outline(points,kind='outline'):
    assert 1 <= len(points) <= 5
    assert all(len(point.split()) <= 25 for point in points),points
    return '<template data-slide-'+kind+'><ul>'+''.join('<li>'+escape(point)+'</li>' for point in points)+'</ul></template>'


def annotate_sections(html,points):
    def add(match):
        key=match.group(1)
        return match.group(0)+(outline(points[key]) if key in points else '')
    return re.sub(r'<section[^>]*\bid="([^"]+)"[^>]*><h2>.*?</h2>',add,html)


def lesson_points(n,r):
    f=lambda x:f'{x:.2f}'
    if n==1:
        main=dict(
            brief=['Proposed action: replenishment alerts','First decision: establish the scale of stockouts','Deliverable: a reconciled baseline and repair log'],
            **{'read-data':['20 products × 7 days = 140 product-days','One row: one store in one week','Unique key: store_id + week'],
            'calculate':[f"{r['raw']:,} exported rows → {r['clean']:,} store-weeks",f"Remove {r['duplicates']} duplicates; recover {r['flagged']} flagged counts",'Keep genuine zeros and record every repair'],
            'interpret':[f"Baseline stockout rate: {f(r['rate'])}%",'Rate = unavailable product-days ÷ scheduled product-days','Compare with the 10% service target'],
            'act':['Hand over the cleaned data, definitions, and repair log','Join store attributes without multiplying weekly rows','Next: locate the largest service burdens'],
            'memo':[f"Baseline: {r['clean']:,} store-weeks; {f(r['rate'])}% stockouts",'Fixed denominator: 140 product-days per store-week','Use this same baseline throughout the course'],
            'big-picture':['A useful metric starts with a measurement agreement','Define the count, opportunities, and decision','A shared baseline lets teams compare evidence'],
            'question':['A weekly count is blank. What enters the rate?'],
            'answer':['Recover the count from its source','Keep the 140-product-day denominator','Record the repair before calculating'],
            'truth':['Added errors: 12 duplicates, eight blanks, four negative counts','Reconciliation recovers all 1,200 original store-weeks']})
        technical=[['Key: store_id + week','Allowed counts: zero to exposure','Exposure: 20 products × 7 days'],['Deduplicate → join repair ledger → replace flagged counts','Validate recovered counts and keys'],['Pooled rate: total stockouts ÷ total exposure','Equal exposure makes the two averaging rules agree'],['Double one record’s exposure; hold its count fixed','Compare simple and exposure-weighted means']]
    elif n==2:
        main=dict(brief=['Decision: where should operations investigate first?','Use all 150 baseline store profiles','Deliverable: a review shortlist with operating context'],
            **{'read-data':['Average eight weekly rates within each store',f"Mean: {f(r['mean'])}%; median: {f(r['median'])}%",f"Middle half: {f(r['q1'])}%–{f(r['q3'])}%"],
            'calculate':['Compare stores within their delivery group','Mean rate: severity of the problem','Share above 10%: breadth of the problem'],
            'interpret':['Weekly chart: movement across time','Group table: differences across stores','Use both views to organize the investigation'],
            'act':['Retain store IDs in the shortlist','Assign reviewers and investigate the replenishment process','Next: assess confidence in a sample audit'],
            'memo':[f"Baseline mean: {f(r['mean'])}%",'Report the spread, group coverage, and store IDs','Direct attention to the observed service burden'],
            'big-picture':['Averages summarize; distributions guide resource allocation','Count how many stores miss the target','Consider both frequency and severity'],
            'question':['Share of long-lead stores above target: which denominator?'],
            'answer':['Denominator: all long-lead stores','Keep numerator and denominator in the same group'],
            'truth':['Same 150 stores; same eight baseline weeks','Grouping changes the view, not the underlying records']})
        technical=[['One baseline average per store','Eight equal-exposure weeks per average'],['Group means use the group’s store count','Threshold shares use the same group denominator','Quantiles describe store averages'],['Describe the complete baseline release','Introduce sampling uncertainty for the later audit'],['Recalculate coverage at 12% and 15% targets','Compare the resulting review workload']]
    elif n==3:
        main=dict(brief=['Decision: is a 30-store audit informative enough?','Fresh shelf checks in week 16','Compare the estimated rate with the 10% target'],
            **{'read-data':['Sampling unit: the store','Calculate one audit rate per sampled store','Keep the audit period separate from the baseline'],
            'calculate':[f"Estimated mean: {f(r['mean'])}%",f"Store SD: {f(r['sd'])} points; mean SE: {f(r['se'])} points",'95% interval: estimate ± t multiplier × SE'],
            'interpret':[f"95% interval: {f(r['low'])}%–{f(r['high'])}%",'The whole range exceeds the 10% service target','Use the range to judge the next action'],
            'act':['Report the unit, period, estimate, and interval together','Fund more measurement when it could change the decision','Next: explain differences across baseline stores'],
            'memo':[f"Week-16 audit: {f(r['mean'])}% stockouts",f"95% interval: {f(r['low'])}%–{f(r['high'])}%",'Proceed with investigating replenishment'],
            'big-picture':['Information has value when it changes an action','Compare uncertainty with the decision threshold','Choose sample size for the decision at hand'],
            'question':['For the standard error, count stores or product-days?'],
            'answer':['Use the 30 independently sampled stores','Product-days share conditions within a store'],
            'truth':[f"Known expected week-16 rate: {f(r['truth'])}%",'Compare the sample estimate with this target']})
        technical=[['30 randomly selected stores','140 independently audited product-days per store','Target: the week-16 expected store-average rate'],['Mean → sample SD → SE → t multiplier','Degrees of freedom: 29'],['Store is the independent sampling unit','Observed spread includes store and measurement variation'],['Repeat sampling with the same sample size','Then vary sample size to study precision']]
    elif n==4:
        main=dict(brief=['Decision: how does delivery time relate to stockout pressure?','Return to the same 150 baseline stores','Fit a line; inspect predictions and residuals'],
            **{'read-data':['Predictor: usual delivery time in days','Outcome: eight-week baseline stockout rate','Inspect group means across the two-to-five-day range'],
            'calculate':['Prediction = intercept + slope × delivery days','OLS minimizes squared prediction misses',f"Slope: {f(r['slope'])} percentage points per day"],
            'interpret':['Residual = actual rate − predicted rate',f"Training RMSE: {f(r['rmse'])} percentage points",'Use residuals to find stores needing closer review'],
            'act':['Use the line as a baseline planning benchmark','Investigate unusually high residuals','Next: add the operating conditions that distinguish stores'],
            'memo':[f"Fitted slope: {f(r['slope'])} points per delivery day",'Use the relationship to describe operating pressure','Add store context to the next comparison'],
            'big-picture':['Explain the model in business units','Trace a prediction for a recognizable store','Add complexity to answer a concrete question'],
            'question':['Positive residual and positive slope: what does each mean?'],
            'answer':['Residual: this store’s actual rate exceeds its prediction','Slope: fitted rates rise with delivery time'],
            'truth':['Generated risk includes delivery, location, demand, promotions, and store differences','The simple line summarizes their observed combination']})
        technical=[['One baseline average per store','X: intercept and delivery days','y: baseline stockout percentage'],['Minimize squared residuals','Fitted values: Xβ; residuals: y − Xβ'],['RMSE uses average squared fitting error','Later-week forecast accuracy is evaluated in Lesson 6'],['Overlay delivery-group means and the fitted line','Inspect residual patterns before adding terms']]
    elif n==5:
        main=dict(brief=['Decision: compare stores with different operating conditions','Add location, demand, and promotion exposure','Allow delivery slopes to differ by location'],
            **{'read-data':['Same baseline outcome and 150 stores','Inputs: lead time, location, demand, promotion share','Define indicator codes and reference values'],
            'calculate':['Interaction: lead × urban','Nonurban slope: b₁; urban slope: b₁ + b₅','Specify every input before calculating a profile'],
            'interpret':['Hold demand and promotion share fixed','Change delivery time and location','Compare the resulting predicted rates'],
            'act':['Use profiles to make the comparison concrete','Investigate stores above their fitted benchmark','Next: test predictions on later observations'],
            'memo':[f"Nonurban slope: {f(r['rural_slope'])} points/day",f"Urban slope: {f(r['urban_slope'])} points/day",'Compare fully specified operating profiles'],
            'big-picture':['“Holding other factors fixed” needs an explicit comparison','Show the inputs and predicted outcomes','Use operating context to explain the model'],
            'question':['Why does the urban delivery slope include two coefficients?'],
            'answer':['For urban stores, both lead and lead × urban change','Add the main delivery slope and the interaction coefficient','For nonurban stores, the interaction is zero'],
            'truth':['The generator allows delivery effects to vary with location','The richer model reflects that operating structure']})
        technical=[['Same 150 baseline profiles','Include demand, promotion share, location, and delivery'],['Construct the interaction term explicitly','Substitute complete profiles into the equation'],['Separate coefficient uncertainty from prediction uncertainty','Interpret each estimate at its reference values'],['Compare specified profiles and residual patterns','Explain which operating comparison changes']]
    elif n==6:
        main=dict(brief=['Decision: which stores need attention next week?','Use information available before the week begins','Choose a procedure through validation'],
            **{'read-data':['One store-week is one forecast case','Inputs must be known at the forecast date','Target: next week’s stockout rate'],
            'calculate':['Train: weeks 3–10','Validate: weeks 11–13','Test once: weeks 14–16'],
            'interpret':[f"Final test RMSE: {f(r['rmse'])} points",'Read error in the same units as the operating target','Judge forecast usefulness on later weeks'],
            'act':['Build a review queue from predicted stockout risk','Track forecast errors as new weeks arrive','Next: test whether alerts improve outcomes'],
            'memo':['Keep training, validation, and test periods separate',f"Final RMSE: {f(r['rmse'])} points",'Use forecasts to prioritize attention'],
            'big-picture':['Prediction turns available information into a planning rule','Validate the rule where it will be used','A useful forecast still needs an effective action'],
            'question':['Can next week’s realized demand be used in today’s forecast?'],
            'answer':['Use only information available at prediction time','Use the planned demand forecast, not future realized demand'],
            'truth':['Forecasts face random outcome variation','The generator also contains persistent store differences','Known mechanisms help diagnose prediction errors']})
        technical=[['Store-week observations with lagged outcomes','Use planned inputs available before the target week'],['Fit candidates on training weeks','Choose on validation weeks','Evaluate the chosen procedure on held-out weeks'],['RMSE penalizes large misses; MAE reports average absolute misses','Keep the final test out of model tuning'],['Vary one feature or model choice','Repeat the same time-ordered validation procedure']]
    elif n==7:
        main=dict(brief=['Decision: do alerts improve service enough to cover their cost?','Randomly offer alerts to 25 of 50 pilot stores','Compare eight-week store averages'],
            **{'read-data':['Unit of assignment: store','Follow-up: weeks 17–24','Weekly cost: 6 CU per stockout product-day + 20 CU for alerts'],
            'calculate':[f"Estimated reduction: {f(r['effect']['value'])} percentage points",f"95% interval: {f(r['effect']['low'])}–{f(r['effect']['high'])} points",'Compare groups created by random assignment'],
            'interpret':['One percentage point saves 8.40 CU per store-week','Break-even reduction: 20 ÷ 8.40 = 2.38 points',f"Estimated weekly saving: {f(r['savings']['value'])} CU per store"],
            'act':['Fund a measured next phase','Track implementation, staff effort, and inventory','Keep the same service and cost definitions'],
            'memo':[f"Pilot reduction: {f(r['effect']['value'])} points",f"Estimated saving: {f(r['savings']['value'])} CU per store-week",'Expand in stages and keep measuring'],
            'big-picture':['Evaluation asks what changes because the business acts','Random assignment supplies the policy comparison','A cost threshold turns the effect into a spending decision'],
            'question':['Why must the break-even reduction exceed zero?'],
            'answer':['Alerts cost 20 CU per store-week','Service savings must cover that cost','Break-even improvement: 2.38 percentage points'],
            'truth':[f"Known expected pilot reduction: {f(r['truth'])} points",'Compare the assignment-based estimate with its population target']})
        technical=[['50 pilot stores; 25 offers and 25 controls','One post-period average per store'],['Reduction: usual-operation mean − offered mean','Use a Welch interval across store means'],['Saving = 8.4 × rate reduction − 20','Translate the effect interval into the same cost units'],['Change the fee or holding-cost assumption','Recalculate the break-even decision']]
    elif n==8:
        main=dict(brief=['Decision: what can voluntary adopters teach us?','Reconstruct selection before estimating an effect','Deliverable: a comparison design and target population'],
            **{'read-data':['Cohort: S051–S100; adoption starts in week 17','Starting conditions affect adoption and later stockouts','Build comparisons from pre-policy characteristics'],
            'calculate':['Compare adopters and nonadopters within delivery groups','Keep both options represented in each group','Calculate usual rate − adopter rate'],
            'interpret':['Target: all 50 stores in this cohort','Weight each group by its share of those stores',f"Delivery-standardized reduction: {f(r['standardized'])} points"],
            'act':['Record eligibility, timing, outcome, and target population','Name the starting conditions behind selection','Carry the design into the fuller adjustment'],
            'memo':['Voluntary adoption requires a selection model',f"Initial standardized reduction: {f(r['standardized'])} points",'Next: use delivery time, location, and baseline performance together'],
            'big-picture':['Choose controls from the order of business events','Connect operating knowledge with the statistical comparison','Define the target before calculating the final estimate'],
            'question':['Should an alert-triggered emergency order be a baseline control?'],
            'answer':['For the total effect, retain the policy’s operating pathway','Adjust for conditions measured before adoption'],
            'truth':['Adoption uses delivery time, location, and baseline rate','Delivery strata adjust for only part of that starting mix']})
        technical=[['50 voluntary-cohort stores','Outcome: average rate in weeks 17–24'],['Calculate a usual-minus-adopter contrast within each stratum','Weight by the target population’s stratum shares'],['Use pre-policy common causes for adjustment','Broad delivery groups leave other differences for Lesson 9'],['Reweight using adopter shares','Explain the change from all-store to adopter target']]
    elif n==9:
        main=dict(brief=['Decision: estimate the gain for all 50 voluntary-cohort stores','Predict both policy options for the same stores','Average the paired reductions over the spending population'],
            **{'read-data':['One analysis row per voluntary-cohort store','Outcome: average rate in weeks 17–24','Starting fields: delivery, location, baseline rate'],
            'calculate':['Fit adoption, starting characteristics, and interactions','Copy each store: set adoption to zero, then one','Subtract the predictions; average across target stores'],
            'interpret':[f"All-store adjusted reduction: {f(r['estimate'])} points",f"Adopter-target reduction: {f(r['att'])} points",'Match the reported average to the proposed rollout'],
            'act':['Match adopters to similar nonadopters','Compare estimates for the same adopter population','Inspect actual matches and model specifications'],
            'memo':[f"All-store estimate: {f(r['estimate'])} points",f"Adopter estimate: {f(r['att'])} points",'Carry the target and calculation into the budget decision'],
            'big-picture':['An average effect belongs to a named population','Two predictions per store make the comparison visible','Changing the rollout mix can change the average gain'],
            'question':['Which model average belongs beside the matching estimate?'],
            'answer':['Use the model’s adopter average','Each match starts from an adopter','An all-store offer concerns a different population mix'],
            'truth':[f"Known all-store reduction: {f(r['truth'])} points",f"Known adopter reduction: {f(r['truth_att'])} points",'Compare estimates with the corresponding target']})
        technical=[['One post-period mean per store','Include adoption interactions with delivery and location'],['Construct X₀ and X₁ for each target row','Average the paired model contrasts'],['Use HC1 covariance for the selected model','Calculate uncertainty for the target’s average contrast'],['Match on standardized pre-policy characteristics','Track reused controls, distances, and retained adopters']]
    else:
        main=dict(brief=['Decision: what improved beyond the network’s existing trend?','25 selected adopters; 25 comparison stores','Compare before-and-after changes'],
            **{'read-data':['Cohort: S101–S150; rollout starts in week 25','Before: weeks 17–24; after: weeks 25–32','Keep one before value, after value, and change per store'],
            'calculate':['Calculate each group’s change','Reduction = comparison change − adopter change',f"Estimated reduction: {f(r['effect']['value'])} percentage points"],
            'interpret':['Use the comparison trend to construct the missing path','Judge parallel trends using history and operating knowledge','Read the effect together with its uncertainty'],
            'act':['Combine pilot, voluntary-adoption, and rollout evidence','Retain each study’s target population and comparison','Use the common cost rule to plan the next phase'],
            'memo':[f"Rollout reduction: {f(r['effect']['value'])} points",f"Estimated weekly saving: {f(r['savings']['value'])} CU per store",'Recommend a measured expansion with clear review criteria'],
            'big-picture':['A useful recommendation connects measurement, prediction, and evaluation','Combine evidence around the same business decision','State the next action and how it will be reviewed'],
            'question':['Why does before-and-after improvement differ from the policy reduction?'],
            'answer':['Comparison stores changed over the same period','Subtract their movement from the adopter movement','Use that trend to construct the no-rollout benchmark'],
            'truth':[f"Known adopter reduction: {f(r['truth'])} points",'Use the same stores and follow-up period when comparing']})
        technical=[['Two periods for each of 50 stores','Preserve the before/after pairing'],['Calculate four group-period means','Recover the same contrast from store-level changes'],['Uncertainty follows independent stores','Model baseline-related trend differences explicitly'],['Inspect pre-trends and subgroup comparisons','Explain any change in weights or target population']]
    appendix=dict(zip(['data','calculation','uncertainty','extension'],technical))
    appendix.update({'generation':['150 stores; 32 weeks; 140 product-days per store-week','Risk reflects operating conditions and store differences','Separate assignment rules for pilot, adoption, and rollout'],
        'known-answer':main['truth']})
    return main,appendix


EXTRA_POINTS={
    'probability':['Discrete probabilities add; continuous probabilities are areas','Expected values use probability weights','Distinguish empirical distributions from theoretical models'],
    'inference-details':['Match the test to the observation structure','Unbiasedness, consistency, and efficiency describe different properties','Use repetition to study the estimator'],
    'regression-details':['Derive coefficients from the same store profiles','Read curvature through the predicted curve or marginal association','Return log predictions to the intended business scale'],
    'multiple-regression-details':['Solve least squares using the specified design matrix','Distinguish a fitted mean from an individual prediction','Read coefficient changes against their held-fixed variables'],
    'prediction-details':['Penalties balance fit and model complexity','Scale and tune inside the training process','Keep validation and final evaluation separate'],
    'potential-outcomes':['Each store has two potential policy outcomes','Only the assigned path is normally observed','Use known outcomes to check the stated target'],
    'graph-details':['Block common-cause paths','Keep mediating paths when estimating the total effect','Conditioning on a collider can create a misleading comparison'],
    'matching-details':['Choose the similarity rule and target population','Track exclusions and reused comparison stores','Resolve numerical ties by the lowest store ID'],
    'did-details':['First differences recover the two-period contrast','Preserve the store as the independent unit','State the weighting rule and trend model']}


GENERATION_REVEAL=['Baseline risk combines recorded conditions and store differences','Alert effects vary with delivery time and location','Shared draws generate both potential outcome counts']
