"""Causal reasoning through potential outcomes, assignment, and worked estimates."""
from functools import lru_cache
import re
import numpy as np
from lesson2_depth import figure,text

CALCULATIONS = '''# Four hypothetical units: outcomes under control and treatment.
from itertools import combinations
from scipy.stats import norm, t
y0 = np.array([5.,6.,7.,8.]); y1 = np.array([4.,6.,8.,7.])
D = np.array([0,0,1,1], dtype=bool)
observed = np.where(D,y1,y0); individual = y1-y0
ate = individual.mean(); att = individual[D].mean(); atu = individual[~D].mean()
gap = observed[D].mean()-observed[~D].mean()
selection = y0[D].mean()-y0[~D].mean()
assert np.allclose([ate,att,atu,gap,selection],[-.25,0,-.5,2,2])
assert np.isclose(gap,att+selection)
assignments = []
for pair in combinations(range(4),2):
    assigned = np.zeros(4,dtype=bool); assigned[list(pair)] = True
    factual = np.where(assigned,y1,y0)
    assignments.append((pair,float(factual[assigned].mean()-factual[~assigned].mean())))
assert np.isclose(np.mean([v for _,v in assignments]),ate)
# The retail experiment has 50 assigned units, not 400 independent assignments.
panel = world()['panel'].query("cohort=='Pilot' and 17<=week<=24")
stores = panel.groupby(['store_id','offer']).stockout_rate.mean().reset_index()
control = stores.loc[stores.offer==0,'stockout_rate'].to_numpy()
offered = stores.loc[stores.offer==1,'stockout_rate'].to_numpy()
v0 = control.var(ddof=1); v1 = offered.var(ddof=1)
se = np.sqrt(v0/25+v1/25)
df = (v0/25+v1/25)**2/((v0/25)**2/24+(v1/25)**2/24)
critical = t.ppf(.975,df); reduction = control.mean()-offered.mean()
pilot_interval = np.array([reduction-critical*se,reduction+critical*se])
result = lesson_result(7)
assert np.isclose(reduction,result['effect']['value'])
assert np.allclose(pilot_interval,[result['effect']['low'],result['effect']['high']])
# OLS reproduces the contrast; HC2 reproduces its Welch standard error.
X = np.column_stack([np.ones(50),stores.offer]); y = stores.stockout_rate.to_numpy()
beta = np.linalg.lstsq(X,y,rcond=None)[0]; residual = y-X@beta
bread = np.linalg.inv(X.T@X); leverage = np.sum((X@bread)*X,axis=1)
hc2 = bread@(X.T@((residual**2/(1-leverage))[:,None]*X))@bread
assert np.isclose(beta[1],-reduction) and np.isclose(np.sqrt(hc2[1,1]),se)
assert np.allclose(8.4*pilot_interval-20,[result['savings']['low'],result['savings']['high']])
# Optional transfer example: original advertising summary counts.
advertising = []
for name,a,b in [('Clicks',3323,3128),('Actions',32,21)]:
    n = 1_000_000; pa = a/n; pb = b/n; binary_gap = pa-pb
    binary_se = np.sqrt(pa*(1-pa)/n+pb*(1-pb)/n)
    advertising.append(dict(name=name,a=a,b=b,pa=pa,pb=pb,gap=binary_gap,
        se=binary_se,pvalue=2*norm.sf(abs(binary_gap/binary_se)),
        low=binary_gap-1.96*binary_se,high=binary_gap+1.96*binary_se))
assert np.allclose([r['pvalue'] for r in advertising],[.015025064693,.130791741],atol=1e-9)
assert 3323+3128 == 6451 and np.isclose(1000/32,31.25)
# Reveal the pilot's potential paths only after the observed-data decision.
potential = panel.groupby(['store_id','offer'])[['y0','y1']].mean().reset_index()
potential['reduction'] = 100*(potential.y0-potential.y1)/140
treated = potential.offer==1
pilot_att = potential.loc[treated,'reduction'].mean()
pilot_atu = potential.loc[~treated,'reduction'].mean()
pilot_selection = 100*(potential.loc[~treated,'y0'].mean()-potential.loc[treated,'y0'].mean())/140
assert np.isclose(reduction,pilot_att+pilot_selection)
assert np.isclose(potential.reduction.mean(),.5*pilot_att+.5*pilot_atu)
'''
DETAIL_TITLES = [
 'Adding and subtracting one counterfactual mean isolates selection',
 'Equal untreated means identify ATT without equating every average effect',
 'Random assignment makes the mean difference unbiased over assignments',
 'Welch uncertainty uses variation across independently assigned stores',
 'HC2 regression uncertainty reproduces the two-group standard error',
 'A binary outcome turns group means into conversion rates',
 'Click and action outcomes produce different precision from the same impressions',
 'Observed cost per action favors A while action evidence remains imprecise',
 'Potential paths explain the pilot contrast after the decision',
]
CODE_TITLES = [
 'Calculate effects and selection in the four-unit teaching example',
 'Enumerate assignments and construct the retail analysis rows',
 'Build the store-level interval and verify the reported estimate',
 'Fit the equivalent regression and start the binary-outcome comparison',
 'Calculate binary uncertainty and begin the potential-outcome reveal',
 'Verify the pilot decomposition and population-weighted average',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    ns=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson7-worked-calculations','exec'),ns)
    return ns

def picture(title,body,caption,height=300):
    visual=figure(title,body,caption,height)
    return re.sub(r'font-size="(\d+)"',lambda m:m.group(0)+' style="font-size:'+str(max(17,int(m.group(1))))+'px"',visual)

def assignment_picture(d):
    sx=lambda v:110+(v+3)*100
    body=''
    for j,(pair,value) in enumerate(d['assignments']):
        y=35+j*33
        body+=text(25,y+6,','.join(chr(65+i) for i in pair),17)+f'<line x1="{sx(-.25)}" x2="{sx(value)}" y1="{y}" y2="{y}" stroke="#aebbb6"/><circle cx="{sx(value)}" cy="{y}" r="6" fill="#276451"/>'+text(sx(value)+12,y+5,f'{value:g}',17)
    body+=f'<line x1="{sx(-.25)}" x2="{sx(-.25)}" y1="12" y2="220" stroke="#b05225" stroke-dasharray="5 4"/>'
    body+=text(110,252,'Treated − control difference (points)',18)+text(110,282,'Dashed line: ATE = −0.25; average of all six estimates',17)
    return picture('Random assignment varies the estimate around the population effect',body,'Left labels identify the two treated units. Each allocation has probability 1/6.',310)

def interval_picture(d):
    sx=lambda v:80+110*v
    lo,hi=d['pilot_interval'];estimate=d['reduction'];threshold=20/8.4
    body=''.join(f'<line x1="{sx(v)}" x2="{sx(v)}" y1="45" y2="200" stroke="#d5ded9"/>'+text(sx(v),230,v,17,'middle') for v in range(6))
    body+=f'<line x1="{sx(threshold)}" x2="{sx(threshold)}" y1="40" y2="200" stroke="#b05225" stroke-width="2" stroke-dasharray="6 4"/>'
    body+=f'<line x1="{sx(lo)}" x2="{sx(hi)}" y1="130" y2="130" stroke="#276451" stroke-width="5"/><circle cx="{sx(estimate)}" cy="130" r="8" fill="#276451"/>'
    body+=text(sx(lo),105,f'{lo:.2f}',17,'middle')+text(sx(hi),105,f'{hi:.2f}',17,'middle')+text(sx(estimate),165,f'Estimate {estimate:.2f}',17,'middle')
    body+=text(80,25,'Zero: no effect',18)+text(sx(threshold)+10,55,'Break-even 2.38',17)+text(360,275,'Reduction in stockout rate (percentage points)',18,'middle')
    return picture('The service interval clears zero and reaches just below break-even',body,'Line: 95% interval. Dashed line: the reduction needed to cover the policy cost.')

def restore(c):
    from retail_ui import section,table,formula,step_link
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();r=d['result'];fmt=lambda v:f'{v:.3f}'
    c['sections']=[];c['authored_sections']=True
    c['headlines']={k:v for k,v in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    c['brief']='The forecast identifies stores likely to struggle. Would offering replenishment alerts reduce their stockouts enough to cover the service cost? First define the effect and learn how random assignment identifies it. Then evaluate the 50-store pilot and make a staged-expansion decision.'
    c['presentation_points']={'memo':['Pilot reduction: 3.49 points; 95% interval 2.36–4.62','Estimated saving: 9.28 CU per store-week','Expand in stages and measure the same outcomes'],
      'question':['The interval excludes zero but crosses break-even. What does each comparison tell us?'],
      'answer':['The pilot supports a service improvement','The interval includes a small accounting loss','Use the estimated return and uncertainty to plan the next phase'],
      'truth':['Expected pilot reduction: 3.81 points','Realized potential-path average: 3.72 points','Observed randomized comparison: 3.49 points']}
    c['headlines']['memo']=['The pilot supports staged expansion with continued measurement','Service improvement and cost recovery answer different questions']
    def block(title,visual,*notes):
        if 'class="calculation"' in visual: visual=visual.replace('\n','<br>')
        return teach(title,visual,list(notes))
    def put(key,title,body,phase='General theory'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    put('causal-question','Distinguish a forecast from an intervention effect',
      block('Predicting an outcome does not identify what an action would change',table(['Question','Comparison'],[['Prediction','Which outcome is likely given available information?'],['Causation','How would the same unit fare under alternative actions?']], 'Different questions can use the same measured outcome'),
        'A good forecast can identify stores with high stockout risk. It does not establish whether an alert would help those stores. Existing alert users may have chosen the service because their problems were unusually severe. The association between use and outcomes therefore combines the response with the circumstances that led to use. Behavioral responses can also obscure a simple association: for example, teams might increase preventive effort when they anticipate a shortage. A small observed correlation need not imply that changing the intervention has no effect. This is a mechanism to investigate, not an empirical finding about the pilot.')+
      block('A causal question names the unit, intervention, outcome, and horizon',bullets('Unit: the entity whose outcome is compared','Intervention: a defined treatment versus a defined alternative','Outcome: the same measurement under either action','Horizon: the same follow-up period'),
        'Define the question before choosing a model. A treatment can be an offer, a delivered service, or a change in operating practice; those are different interventions. A binary indicator D takes value one for treatment and zero for control. The comparison fixes the unit and relevant setting while changing the specified intervention.'))
    put('counterfactuals','Understand what the factual data cannot show',
      block('Two potential outcomes define one individual treatment effect',formula('τᵢ = Yᵢ(1) − Yᵢ(0); Yᵢ = DᵢYᵢ(1) + (1−Dᵢ)Yᵢ(0)'),
        'Y(1) is the outcome under treatment; Y(0) is the outcome under control. The switching equation selects the observed outcome. If D=1 it reduces to Y=Y(1); if D=0 it reduces to Y=Y(0). The individual treatment effect compares both paths for the same unit. In an ordinary parallel-group study only one is observed, so the individual effect is not directly observed.')+
      block('Observed rows leave one potential outcome missing for every unit',table(['Hypothetical unit','D','Observed Y','Y(0)','Y(1)'],[['A',0,5,5,'?'],['B',0,6,6,'?'],['C',1,8,'?',8],['D',1,7,'?',7]], 'Teaching example: four hypothetical stores; stockout-rate units (%)'),
        'These four hypothetical units are a small numerical illustration, not records from the course pilot. Ask students which cells could be filled from factual data alone. Neither a large sample nor an accurate prediction algorithm directly reveals both individual outcomes. Identification uses a design and assumptions to learn an average comparison.')+
      block('A revealed teaching table shows effects with different signs',table(['Unit','Y(0)','Y(1)','Observed Y','Effect'],[['A',5,4,5,-1],['B',6,6,6,0],['C',7,8,8,1],['D',8,7,7,-1]], 'Reveal after discussing the missing cells; effect = Y(1) − Y(0)'),
        'The supplied potential outcomes complete the teaching example. A and D improve by one point, B does not change, and C worsens by one point. The outcome is a stockout rate, so negative signed effects indicate improvement. This reveal establishes the numerical truth for the exercise; real factual records do not supply the hidden cells.')+
      block('An average effect can hide different responses to the same intervention',bullets('Individual effects here: −1, 0, +1, −1','Some units improve while another worsens','An average describes the named population','Subgroup questions require their own evidence'),
        'Heterogeneity means the effect varies between units. It can reflect operating conditions, implementation, or other characteristics. An average near zero does not imply that nothing happened to anybody. Similarly, a useful average does not establish that every unit benefits. Decide whose outcomes the management question concerns before choosing an average.'))
    put('effect-targets','Calculate the average that answers the question',
      block('ATE averages individual effects across the full target population',formula('ATE = E[τ] = E[Y(1)] − E[Y(0)] = (−1 + 0 + 1 − 1)/4 = −0.25'),
        'The average treatment effect gives each unit in the target population its specified weight. Here the four stores are equally weighted. A policy applied to all four reduces the average stockout rate by 0.25 points in the teaching world. This is different from comparing outcomes of the two assigned groups.')+
      block('ATT and ATU average effects among treated and untreated units',table(['Target','Units in this assignment','Calculation','Effect'],[['ATT','C, D','(1 − 1)/2',0],['ATU','A, B','(−1 + 0)/2',-.5]], 'Both averages use individual effects, not observed group means'),
        'ATT asks about the effect for units that received treatment; ATU asks about those that did not. Their definitions are conditional averages of the same individual effect. They can differ when the groups contain different responses. The definitions alone do not supply the missing potential outcomes needed to estimate them.')+
      block('Population shares connect the three treatment-effect averages',formula('ATE = P(D=1) ATT + P(D=0) ATU = 0.5 × 0 + 0.5 × (−0.5) = −0.25'),
        'This identity follows by splitting the population into treated and untreated groups. It is a weighting identity, not an identification assumption. Changing the population or its weights can change the average. In later observational lessons, who adopts and which population management wants to reach will matter explicitly.'))
    put('selection','Separate an observed contrast from a causal effect',
      block('The observed difference is two points despite a negative population effect',formula('Observed difference = (8 + 7)/2 − (5 + 6)/2 = 7.5 − 5.5 = 2'),
        'Using only the observed table, treated units have a stockout rate two points higher. But their average individual treatment effect is zero and the whole population effect is −0.25. Their higher observed rate therefore cannot be read directly as harm caused by treatment. The comparison mixes the intervention with which units were assigned.')+
      block('Adding one counterfactual mean separates effect from selection',formula('E[Y|D=1] − E[Y|D=0]\n= {E[Y(1)|D=1] − E[Y(0)|D=1]}\n+ {E[Y(0)|D=1] − E[Y(0)|D=0]}'),
        'First use the switching equation to replace observed outcomes by the appropriate potential outcomes. Add and subtract the treated group’s mean Y(0). The first bracket is ATT. The second compares the groups under the same untreated condition and is the selection component. That treated counterfactual mean is exactly what ordinary data do not reveal.')+
      block('The teaching example attributes the entire observed gap to selection',formula('Selection = (7 + 8)/2 − (5 + 6)/2 = 2\nObserved difference = ATT + selection = 0 + 2'),
        'The treated units would have had higher stockouts even without treatment. A valid comparison must deal with that difference. Zero selection in untreated outcomes would make the observed contrast identify ATT. It would not, by itself, prove ATT equals ATU or ATE: treatment responses may still differ across groups.'))
    put('random-assignment','Use assignment to identify the comparison',
      block('Random assignment makes treatment independent of both potential outcomes',formula('(Y(0), Y(1)) ⟂ D\nE[Y(j)|D=1] = E[Y(j)|D=0] = E[Y(j)], j ∈ {0,1}'),
        'When each eligible unit has the same treatment probability independent of its potential outcomes, treatment and control represent the same potential-outcome distributions across repetitions. With a well-defined intervention and no interference, the mean difference identifies ATE. Both treatment states must have positive probability. These are population expectations; actual sample means can differ by chance.')+
      block('Six random allocations produce six different observed comparisons',assignment_picture(d),
        'Fix the four pairs of potential outcomes and assign exactly two units to treatment. There are six equally likely pairs. For each pair, observe the potential outcome selected by that assignment and recompute the group difference. The estimates range from −2.5 to 2 points even though the four individual effects remain fixed. The left labels name the two treated units.')+
      block('The average across random assignments equals the true population effect',formula('E_assignment[estimated effect] = (−2.5 − 1 − 1 + 0.5 + 0.5 + 2)/6 = −0.25'),
        'Randomization removes systematic selection over assignments, not every chance imbalance in one draw. This finite example makes unbiasedness concrete. It is not a permutation test that holds observed outcomes fixed: here both potential outcomes are supplied and the observed outcome changes with assignment. The general proof is in the appendix.'))
    put('experiment-design','Define an experiment that estimates the intended effect',
      block('A stable intervention gives the potential-outcome comparison a clear meaning',bullets('Specify what treatment and usual operation deliver','Measure outcomes over the same follow-up period','Handle spillovers through the assignment design','Record delivery and participation alongside assignment'),
        'Consistency connects observed outcomes with the specified treatment version. No interference means another unit’s assignment does not alter this unit’s outcome. These ideas underpin SUTVA. If stores share a replenishment team that reallocates capacity, assignment may need to be organized at that team level. Effects in a larger rollout are an additional question about population and implementation.')+
      block('Experiment types differ in setting and the source of assignment',table(['Design','Source of variation','Example setting'],[['Laboratory','Designed assignment','Controlled task'],['Field','Designed assignment','Operating stores'],['Online A/B','Designed assignment','Users or accounts'],['Natural experiment','External event or rule','Eligibility or policy change']], 'A credible causal comparison depends on the assignment mechanism'),
        'Laboratory settings offer close control; field and online experiments observe behavior in operating settings. A natural experiment obtains variation from an external source, but external does not automatically mean independent of potential outcomes. Its rules must justify the comparison. Lessons 8–10 develop other ways to construct a comparison when ordinary random assignment is unavailable.')+
      block('Assignment records establish randomization while balance describes the realized groups',bullets('Define eligibility and record the random procedure','Check assignment counts and actual exposure','Inspect important pre-treatment characteristics','Preserve analysis by assigned group'),
        'A balanced table can arise without random assignment, and a randomized draw can be imbalanced. Inspect the allocation record and implementation as well as baseline summaries. Comparing groups as assigned estimates the effect of the offer. If uptake differs from assignment, that offer effect remains distinct from the effect of actual receipt. The present pilot delivers the service as assigned.'))
    put('estimation-theory','Connect group comparisons to rates and regression',
      block('A mean difference estimates the effect and a standard error measures its precision',formula('Effect estimate = Ȳ₁ − Ȳ₀\nSE = √(s₁²/n₁ + s₀²/n₀)\nInterval = estimate ± critical value × SE'),
        'The two groups contribute uncertainty through their outcome variances and sample sizes. Use the independent assignment unit. With repeated outcomes for each assigned store, average them within store for this analysis. Welch’s t interval allows the group variances to differ. Its degrees of freedom and derivation follow in the appendix.')+
      block('For a binary outcome the group mean is the success rate',formula('Y ∈ {0,1}: p̂₁ = successes₁/n₁; p̂₀ = successes₀/n₀\nRate difference = p̂₁ − p̂₀'),
        'A conversion indicator, completion indicator, or service-success indicator is one for success and zero otherwise. Its mean is a proportion. Define the eligible denominator before comparing rates. For a funnel, clicks per impression and actions per impression measure different outcomes. Conditioning on people who clicked changes the population after treatment and does not preserve the original randomized comparison.')+
      block('Percentage-point change and relative lift use different denominators',table(['Measure','Illustration: 10% becomes 12%'],[['Percentage-point change','12 − 10 = 2 points'],['Relative lift','(12 − 10)/10 = 20%']], 'Illustrative arithmetic; these are not pilot results'),
        'The absolute change determines the expected extra number of successes at a given volume. Relative lift divides that change by the baseline rate and can look large when the baseline is small. Report the rate and denominator alongside either comparison. The appendix applies these calculations to the original advertising counts.')+
      block('A treatment-indicator regression fits the two group means exactly',formula('Yᵢ = a + bDᵢ + eᵢ\nâ = Ȳ₀; â + b̂ = Ȳ₁; b̂ = Ȳ₁ − Ȳ₀'),
        'With only an intercept and a binary treatment indicator, least squares sets each fitted group value to its sample mean. This gives exactly the mean difference, whether the outcome is continuous or binary. For binary outcomes the coefficient is a difference in probabilities. Use a variance calculation appropriate to the assignment and outcome; the equality of coefficients alone does not determine the standard-error convention.'))
    put('read-data','Construct the pilot comparison at the assignment unit',
      block('The pilot randomizes fifty stores to an alert offer or usual operation',table(['Design element','Pilot specification'],[['Eligible units','S001–S050'],['Offer group','25 stores; alerts and weekly review'],['Comparison group','25 stores; usual operation'],['Follow-up','Weeks 17–24'],['Outcome','Each store’s mean stockout rate']], 'One assigned store contributes one analysis row'),
        'The alert lists low-stock products before the replenishment review so staff can bring forward orders. Every offered store receives the defined service. The eight weekly observations improve measurement of that store’s follow-up outcome; they do not create eight independent assignments. The voluntary-adoption and later-rollout cohorts remain outside this experiment.')+
      block('Each pilot row averages eight weekly outcomes for one assigned store',table(['Store','Offer','Baseline (%)','Follow-up (%)'],[[x['store_id'],x['offer'],fmt(x['baseline_rate']),fmt(x['rate'])] for x in r['sample']], 'Six factual rows from the 50-store analysis table'),
        'Group the weekly panel by store and assignment, restrict follow-up to weeks 17–24, and average the stockout rates. These rows contain only the factual outcome selected by assignment. Baseline rates come from the pre-treatment period. Use all 50 store averages for the reported estimate; the six rows shown here explain the table structure.')+
      block('Baseline characteristics describe the actual randomized draw',table(['Characteristic','Offered','Usual operation'],[[x['variable'],fmt(x['offered']),fmt(x['usual'])] for x in r['depth']['balance']], 'Measured before the offer'),
        'Mean starting stockout rates are close, while lead time and urban share differ somewhat. These are features of this realized assignment, not evidence that the procedure failed. Keep the pre-treatment definitions and assignment record. The primary analysis below is the predeclared unadjusted contrast; covariate adjustment can be examined as a separate precision analysis.'),phase='Worked application')
    put('calculate','Reconstruct the effect and its uncertainty',
      block('The observed group means imply a reduction of 3.49 points',table(['Assignment','Stores','Mean rate (%)','SD across stores'],[['Usual operation',25,fmt(d['control'].mean()),fmt(np.sqrt(d['v0']))],['Alert offer',25,fmt(d['offered'].mean()),fmt(np.sqrt(d['v1']))]], 'Reduction = usual − offered = 11.9357 − 8.4500 = 3.4857 points'),
        'The general signed treatment effect is offered minus usual, −3.4857 points. Because lower stockouts are desirable, management reports its negative as a positive reduction. Apply the same reversal to interval endpoints, so the reduction interval runs from minus the upper signed-effect endpoint to minus the lower endpoint.')+
      block('Store-level variation gives a standard error of 0.562 points',formula('SE = √(2.0521²/25 + 1.9212²/25) = 0.5622\n95% interval = 3.4857 ± 2.0109 × 0.5622 = [2.3552, 4.6162]'),
        'The Welch degrees of freedom are 47.793 and the two-sided 95% t multiplier is 2.0109. The main estimate is an average offer effect for the pilot population. The interval quantifies uncertainty in that average; it is not a range of individual-store effects. The calculation uses all 50 store averages, not only a displayed extract.')+
      block('The fitted treatment coefficient reproduces the same signed effect',table(['Regression quantity','Value'],[['Intercept: usual-operation mean',fmt(d['beta'][0])],['Offer coefficient',fmt(d['beta'][1])],['Fitted offered mean',fmt(sum(d['beta']))],['HC2 standard error',fmt(np.sqrt(d['hc2'][1,1]))]], 'Rate = intercept + offer coefficient × offer'),
        'HC2 corrects each squared residual for its regression leverage and reproduces the Welch standard error for this two-group design. For the identical interval, retain the Welch degrees of freedom; a package’s default normal or residual-df multiplier can differ. The appendix derives this connection. Adding controls changes the specification and should be explained as a separate analysis.')+step_link(7,'calculation'),phase='Worked application')
    put('interpret','Translate precision into the operating decision',
      block('The policy must reduce stockouts by 2.38 points to cover its cost',formula('1 point = 140 × 0.01 = 1.4 product-days\nValue per point = 1.4 × 6 = 8.40 CU\nBreak-even reduction = (12 + 8)/8.40 = 2.38 points'),
        'Each store-week has 140 product-days. The stated accounting charge is 6 currency units per stockout product-day. The alert fee is 12 and extra inventory holding cost is 8 per store-week. This is the specified cost rule, so an improvement must cover 20 before it saves money. It is not a measured estimate of lost customer lifetime value.')+
      block('The service interval excludes zero but includes the break-even threshold',interval_picture(d),
        'The entire interval is positive, supporting a reduction in stockouts. Its lower endpoint, 2.355 points, is slightly below the 2.381-point break-even threshold. That is why a service improvement and assured cost recovery are different conclusions. Compare the interval with the actual decision threshold, not only with zero.')+
      block('The estimated saving is positive while its interval includes a small loss',formula('Saving = 8.40 × 3.4857 − 20 = 9.28 CU per store-week\n95% interval = 8.40 × [2.3552, 4.6162] − 20 = [−0.22, 18.78]'),
        'Multiplying by a positive constant and subtracting the fixed cost transforms both interval endpoints. The same answer follows from directly comparing group mean operating costs, because exposure and treatment cost are fixed here. Management can weigh the estimated saving, its uncertainty, and the cost of another learning phase. A significance cutoff alone is not a rollout rule.'),phase='Worked application')
    put('act','Decide and carry the design into the next phase',
      block('A staged expansion preserves the evidence needed for the next decision',bullets('Keep the alert offer and cost definitions fixed','Track delivery, staff effort, inventory, and service','Choose the next review horizon before measuring results','Use the next cohort to test whether the gain transfers'),
        'The pilot supports a measured next phase with the same primary service outcome and accounting rule. Staff effort and wider inventory consequences are operating measures to collect, not extra results already observed in this dataset. Replication tests whether the result persists in another period or population. Voluntary adoption in Lesson 8 requires reconstructing its different assignment process.')+
      block('After the decision, potential paths explain the observed pilot reduction',formula('Observed reduction = ATT reduction + untreated-path difference\n3.4857 = 3.6071 + (−0.1214)'),
        'Reveal this only after students decide from observed evidence. Here both generated paths are available for checking the reasoning. The offered stores’ realized average reduction is 3.6071 points. Under usual operation, control stores’ mean would be 0.1214 points lower than the offered stores’ mean. That chance difference shifts this assignment’s estimate below its ATT reduction.')+
      block('The realized and expected pilot effects refer to different averages',table(['Quantity','Reduction (points)'],[['Observed randomized contrast',fmt(r['effect']['value'])],['Average realized potential-path reduction',fmt(r['depth']['ate'])],['Average expected reduction before outcome draws',fmt(r['truth'])]], 'Different quantities; one continuing pilot population'),
        'The realized potential-path average is 0.5×3.6071 + 0.5×3.8321 = 3.7196 points. It averages the two generated paths for all 50 stores. The expected 3.808-point effect averages their underlying probability differences before the stockout outcomes are drawn. Assignment variation separates the observed contrast from the realized average, and outcome variation separates the realized average from its expectation.'),phase='Worked application')
    c['question']='The 95% reduction interval excludes zero but crosses the cost threshold. What does each comparison tell the director?'
    c['answer']='The interval supports a service improvement. Under the stated cost rule it also includes a small accounting loss. The estimated saving is positive, so a staged expansion can collect further evidence while measuring the same service, implementation, and cost outcomes.'
    c['code']=CALCULATIONS
    c['technical']=[
      'The factual pilot analysis uses 50 store averages from weeks 17–24, with 25 offers and 25 controls. The four-unit table is a separate hypothetical teaching example. The advertising extension uses the original deck’s two summary rows and is not part of the retail dataset.',
      'Execute the same calculations used in the lesson: four-unit effects, all six assignments, the retail Welch interval, regression with HC2 variance, original binary A/B comparisons, and the potential-path reveal. All quantities are reproducible from the shared source and the labelled example inputs.',
      'Welch uncertainty uses s0²/n0+s1²/n1 and Welch–Satterthwaite degrees of freedom. HC2 supplies the same standard error in the intercept-plus-indicator regression. The same interval requires the same t multiplier. Cost intervals use the positive affine transformation 8.4×reduction−20.',
      'Change the alert cost while preserving the observed estimate. Recalculate the threshold and explain the decision. Then change the four-unit assignment, observe the selected outcomes, and compare the new estimate with the unchanged ATE. Do not treat this demonstration as a permutation test.'
    ]
    details=[
      (formula('Δobs = E[Y(1)|D=1] − E[Y(0)|D=0]\nAdd 0 = −E[Y(0)|D=1] + E[Y(0)|D=1]\nΔobs = ATT + {E[Y(0)|D=1] − E[Y(0)|D=0]}'),
       'The switching equation justifies the first line. The added pair is algebraically zero. Regrouping identifies the first component as the mean individual effect among treated units. In the four-unit example the observed contrast is 2, ATT is 0, and the selection term is 2. In the reduction convention every signed-effect term is negated consistently.'),
      (table(['Constructed counterexample','Y(0)','Y(1)','Effect'],[['Untreated unit',5,5,0],['Treated unit',5,7,2]],'Both untreated paths equal 5; treatment effects still differ'),
       'The selection component is zero and the observed contrast is ATT=2. But ATU=0 and ATE=1 for equally weighted units. Thus equal untreated means do not imply equal effects. Independence of assignment from both potential outcomes establishes the stronger population equalities. The main four-unit example and this two-unit counterexample are distinct labelled illustrations.'),
      (formula('E_D[Ȳ₁] = (1/N)ΣYᵢ(1); E_D[Ȳ₀] = (1/N)ΣYᵢ(0)\nE_D[Ȳ₁−Ȳ₀] = (1/N)Στᵢ'),
       'Under complete randomization with fixed n1 and n0, each unit’s inclusion probability in treatment is n1/N. The expectation of (1/n1)ΣD_iY_i(1) therefore equals the population mean of Y(1). Apply the same argument to control and subtract. Hold potential outcomes fixed and average over assignment. No constant individual effect is needed.'),
      (formula('ν = (s₁²/n₁+s₀²/n₀)² / {(s₁²/n₁)²/(n₁−1)+(s₀²/n₀)²/(n₀−1)}'),
       'Use sample variances with denominator n_g−1. For the pilot, ν=47.793 and t_.975=2.0109. This is the lesson’s approximate Welch interval. For a finite randomized population, the exact randomization variance also involves the variance of individual effects, which ordinary factual data do not identify; the usual two-group variance omits that subtractive term. Do not describe the Welch interval as an exact randomization interval.'),
      (formula('V_HC2 = (X′X)⁻¹ X′ diag[eᵢ²/(1−hᵢ)] X (X′X)⁻¹'),
       'In an intercept-plus-indicator model, leverage is 1/n_g within group g. Dividing squared residuals by 1−1/n_g changes each group’s residual sum into its sample-variance contribution. The slope variance becomes s1²/n1+s0²/n0. HC0 instead uses the unadjusted residual squares. Point-estimate equivalence holds for both, but finite-sample variance conventions differ.'),
      (formula('Δp = p̂A−p̂B\nSE_large = √[p̂A(1−p̂A)/nA + p̂B(1−p̂B)/nB]'),
       'This is the large-sample unpooled binary comparison used for the original advertising illustration and matches the HC0 variance of its indicator regression. It assumes independent eligible observations under the design. Repeated users or cluster assignment would need corresponding unit-level treatment. Two million synthetic rows are unnecessary when the relevant information is the two counts and denominators.'),
      (table(['Outcome','A / 1m','B / 1m','Difference (pp)','Two-sided p'],[[a['name'],a['a'],a['b'],f"{100*a['gap']:.4f}",f"{a['pvalue']:.3f}"] for a in d['advertising']], 'Optional transfer example: advertising counts from the original deck'),
       'Clicks are 0.3323% versus 0.3128%, a 0.0195-point difference and 6.23% relative lift. Actions are 0.0032% versus 0.0021%, a 0.0011-point difference and 52.38% relative lift. The large-sample 95% intervals in points are [0.00378,0.03522] and [−0.000327,0.002527]. The action estimate has a much larger relative lift but weaker precision. Each rate uses impressions as denominator.'),
      (table(['Version','Cost','Actions','Observed cost/action'],[['A','1,000',32,'31.25'],['B','1,000',21,'47.62']], 'Impression cost: 0.001; one million impressions per version'),
       'A has the lower observed cost per action. That ratio summarizes the realized sample; the imprecise action difference should inform the next decision. There are 6,451 total clicks. This corrected example uses the supplied counts rather than the original duplicated action-output screenshot. A click count is not automatically a count of unique people.'),
      (table(['Pilot target','Reduction (points)'],[['ATT',fmt(r['depth']['att'])],['ATU',fmt(r['depth']['atu'])],['ATE',fmt(r['depth']['ate'])],['Control minus treated Y(0)',fmt(r['depth']['selection_component'])]], 'Both generated paths are used only for the teaching reveal'),
       'The observed reduction equals ATT plus the control-minus-treated untreated-path difference. The population average equals the weighted average of ATT and ATU. In actual observational data the treated Y(0) and untreated Y(1) remain hidden; this table explains the problem rather than supplying a generally available adjustment recipe.'),
    ]
    refs='<p>Further reading: <a href="https://www.theeffectbook.net/ch-TreatmentEffects.html">Treatment-effect targets</a>; <a href="https://www.theeffectbook.net/ch-UndertheRug.html#it-lurks-they-call-it-sutva">Treatment versions and interference</a>.</p>'
    c['appendix_extra']='<section id="causal-details"><h2>Work through identification and experimental estimation</h2>'+''.join(block(t,v,n) for t,(v,n) in zip(DETAIL_TITLES,details))+refs+'</section>'
    return c
