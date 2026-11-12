"""Independent student tasks and reproducible answers for the course bridges.

Exercise extracts are explicitly labelled; the shared case is never mutated.
All code runs after the existing self-contained retail_case setup.
"""
from functools import lru_cache

WORK = {
1: '''# A separate fictional export: B has an unresolved count; C has conflicting duplicates.
extract = pd.DataFrame({'store':['A','B','C','C'], 'count':[10,np.nan,8,12], 'exposure':[100,50,40,40]})
assert extract.duplicated('store').sum()==1
# The two C records describe the same 40 opportunities: never add both denominators.
complete_low = 100*(10+8)/(100+40)
complete_high = 100*(10+12)/(100+40)
all_low = 100*(10+0+8)/190
all_high = 100*(10+50+12)/190
equal_store_low = (10+100*8/40)/2
assert all_low < complete_low < complete_high < all_high
answer = dict(complete_low=complete_low,complete_high=complete_high,
              all_low=all_low,all_high=all_high,equal_store_low=equal_store_low)
''',
2: '''# Fictional 100 product-days, with mutually exclusive delivery groups and equal counting units.
counts = np.array([[54,6],[28,12]])  # rows: short/long delivery; columns: available/stockout
assert counts.sum()==100
group_share = counts.sum(axis=1)/counts.sum()
conditional = counts[:,1]/counts.sum(axis=1)
overall = counts[:,1].sum()/counts.sum()
weighted = group_share@conditional
# Y is 1 for stockout and 0 for available: E[Y] is the probability of stockout.
assert np.isclose(overall,weighted) and np.allclose(conditional,[.1,.3])
# A changed population mix changes the overall risk even if both conditional risks stay fixed.
new_mix = np.array([.25,.75])
answer = dict(overall=overall,short=conditional[0],long=conditional[1],
              weighted=weighted,new_mean=float(new_mix@conditional),
              joint_long_stockout=counts[1,1]/counts.sum())
''',
3: '''# Planning assumptions, not estimates from the realized experiment.
from scipy.stats import norm
sigma = 4.0  # SD in percentage points across independent store outcomes
margin = 1.0
audit_n = int(np.ceil((norm.ppf(.975)*sigma/margin)**2))
budget_n = 40
budget_margin = norm.ppf(.975)*sigma/np.sqrt(budget_n)
# Two equal randomized arms: two-sided 5% test, 80% power, worthwhile reduction 2 points.
delta = 2.0
per_arm = int(np.ceil(2*(norm.ppf(.975)+norm.ppf(.8))**2*sigma**2/delta**2))
assert audit_n==62 and per_arm==63
answer = dict(audit_n=audit_n,budget_margin=float(budget_margin),per_arm=per_arm,
              audit_cost=25*audit_n,budget_cost=25*budget_n)
''',
4: '''# Illustrative population: five equally likely X values; true mean is X squared.
x = np.array([-2.,-1.,0.,1.,2.]); mean_y = x*x
X = np.column_stack([np.ones(5),x])
beta = np.linalg.lstsq(X,mean_y,rcond=None)[0]
residual = mean_y-X@beta
candidate_loss = [float(np.sum((mean_y-(a+b*x))**2)) for a,b in [(0,0),(2,0),(2,1)]]
assert np.allclose(beta,[2,0]) and np.allclose(X.T@residual,0)
# Conditional mean errors remain 2,-1,-2,-1,2 despite the two zero sample moments.
assert not np.allclose(residual,0)
answer = dict(intercept=float(beta[0]),slope=float(beta[1]),loss=candidate_loss,
              residual=residual.tolist(),sum_residual=float(residual.sum()))
''',
5: '''# Reconstruct the delivery coefficient in the same six-column baseline model.
s = world()['stores']; x = s.lead_days.to_numpy(); y = s.baseline_rate.to_numpy()
Z = np.column_stack([np.ones(len(s)),s.urban,s.baseline_demand-100,s.promotion_share,x*s.urban])
rx = x-Z@np.linalg.lstsq(Z,x,rcond=None)[0]
ry = y-Z@np.linalg.lstsq(Z,y,rcond=None)[0]
partial = float(rx@ry/(rx@rx))
X = np.column_stack([np.ones(len(s)),x,s.urban,s.baseline_demand-100,s.promotion_share,x*s.urban])
b,V,e = fit_ols(X,y)
assert np.isclose(partial,b[1])
# Urban delivery slope is b_delivery+b_interaction: covariance is part of its uncertainty.
variance_parts = [float(V[1,1]),float(V[5,5]),float(2*V[1,5])]
urban_slope = float(b[1]+b[5]); se = float(np.sqrt(sum(variance_parts)))
assert np.isclose(se,np.sqrt(np.array([0,1,0,0,0,1])@V@np.array([0,1,0,0,0,1])))
answer = dict(partial=partial,full=float(b[1]),variance_parts=variance_parts,
              urban_slope=urban_slope,se=se,low=urban_slope-1.96*se,high=urban_slope+1.96*se,
              first_rows=[[str(s.iloc[i].store_id),float(rx[i]),float(ry[i])] for i in range(3)])
''',
6: '''# Secondary retrospective operating check: keep the original RMSE-selected procedure frozen.
rows = world()['panel'].query('3<=week<=16').copy()
development = rows.query('week<=13'); final = rows.query('week>=14').copy()
selection,depth = prediction_analysis()
fitted = fit_forecast(development,selection['selected'],depth['alpha'])
final['model'] = predict_forecast(fitted,final)
final['lag_only'] = final.lag_rate
metrics = []
for name in ['model','lag_only']:
    selected = pd.concat([g.sort_values([name,'store_id'],ascending=[False,True]).head(5)
                          for _,g in final.groupby('week')])
    metrics.append(dict(rule=name,rmse=float(np.sqrt(np.mean((final.stockout_rate-final[name])**2))),
                        reviewed=len(selected),burden=float(selected.stockout_days.sum()),
                        mean_rate=float(selected.stockout_rate.mean()),
                        share=float(selected.stockout_days.sum()/final.stockout_days.sum())))
# Repeat-fit experiment at X=0, under a known quadratic mean and independent noise variance 1.
rng = np.random.default_rng(6112); grid = np.linspace(-2,2,20)
predictions = {1:[],2:[]}
for repeat in range(500):
    y = grid**2+rng.normal(size=len(grid))
    for degree in predictions:
        predictions[degree].append(float(np.polynomial.polynomial.polyfit(grid,y,degree)[0]))
decomposition = []
for degree,values in predictions.items():
    values = np.array(values); bias2=float(values.mean()**2); variance=float(values.var(ddof=0))
    assert np.isclose(np.mean(values**2),bias2+variance)
    decomposition.append(dict(degree=degree,bias2=bias2,variance=variance,expected_loss=bias2+variance+1))
answer = dict(metrics=metrics,decomposition=decomposition)
''',
7: '''# Separate fictional incomplete-delivery trial; assignment stays the analysis group.
# 50 offered: 40 observed at 12%, 10 missing. 50 controls: all observed at 15%.
offer_observed_mean = 12.; control_mean = 15.
complete_case_reduction = control_mean-offer_observed_mean
# Outcome bounds 0%-100%; no missing-at-random claim is assumed.
offer_low = (40*12+10*0)/50
offer_high = (40*12+10*100)/50
reduction_bounds = [control_mean-offer_high,control_mean-offer_low]
# If a documented sensitivity assumption restricts missing outcomes to 12%-20%:
sensitivity = [control_mean-(40*12+10*m)/50 for m in [20,12]]
answer = dict(complete_case_reduction=complete_case_reduction,bounds=reduction_bounds,
              sensitivity=sensitivity,observed_fraction=.8)
''',
8: '''# Enumerate backdoor paths in two small, explicitly specified competing stories.
# A: measured baseline workload W causes both offer D and outcome Y.
# B: unmeasured management U also causes D and Y; recorded W is just one measured cause.
paths_a = [['D','W','Y']]
paths_b = [['D','W','Y'],['D','U','Y']]
def open_fork_paths(paths,controls):
    # This helper handles only these noncollider fork paths, not arbitrary DAGs.
    return [path for path in paths if not set(path[1:-1]).intersection(controls)]
assert open_fork_paths(paths_a,{'W'})==[]
assert open_fork_paths(paths_b,{'W'})==[['D','U','Y']]
answer = dict(story_a_open=open_fork_paths(paths_a,{'W'}),
              story_b_open=open_fork_paths(paths_b,{'W'}),identified_from_W_alone=[True,False])
''',
9: '''# Design first: exact location plus the original logit caliper, without inspecting outcomes.
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
w = world(); vars = ['lead_days','urban','baseline_rate']
v = w['stores'].query("cohort=='Voluntary'")[['store_id','offer']+vars].sort_values('store_id').reset_index(drop=True)
model = make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000))
score = model.fit(v[vars],v.offer).predict_proba(v[vars])[:,1]
v['logit'] = np.log(score/(1-score)); caliper=.2*v.logit.std(ddof=1)
treated=v[v.offer==1]; controls=v[v.offer==0]; pairs=[]
for i,row in treated.iterrows():
    candidates=controls[controls.urban==row.urban]
    if candidates.empty: continue
    j=nearest_score_match(candidates,row.logit)
    if abs(candidates.loc[j,'logit']-row.logit)<=caliper: pairs.append((i,j))
kept=[i for i,j in pairs]; used=[j for i,j in pairs]
balance=[]
for col in vars:
    scale=np.sqrt((treated[col].var(ddof=1)+controls[col].var(ddof=1))/2)
    balance.append(dict(variable=col,smd=float((v.loc[kept,col].mean()-v.loc[used,col].mean())/scale)))
assert all(v.loc[i,'urban']==v.loc[j,'urban'] for i,j in pairs)
# Freeze the design before attaching outcomes. Results are diagnostic; no further outcome-driven search.
outcome=w['public'].query("cohort=='Voluntary' and 17<=week<=24").groupby('store_id').stockout_rate.mean()
v['y']=v.store_id.map(outcome); X=voluntary_design(v,v.offer.to_numpy())
b,V,e=fit_ols(X,v.y.to_numpy())
C=voluntary_design(v,np.zeros(len(v)))-voluntary_design(v,np.ones(len(v)))
c=C[kept].mean(axis=0); adjusted=float(c@b); se=float(np.sqrt(c@V@c))
matched=float(np.mean([v.loc[j,'y']-v.loc[i,'y'] for i,j in pairs]))
reuse=pd.Series(used).value_counts().to_numpy()
answer=dict(retained=len(kept),excluded=26-len(kept),unique_controls=len(set(used)),
            balance=balance,matched=matched,adjusted=adjusted,se=se,
            low=adjusted-1.96*se,high=adjusted+1.96*se,
            effective_controls=float(reuse.sum()**2/(reuse@reuse)),
            max_reuse=int(reuse.max()),caliper=float(caliper))
''',
10: '''# Separate no-treatment scenario: selection follows a temporary baseline shock.
before=np.array([18.,18.,10.,10.]); after=np.array([14.,14.,14.,14.]); D=np.array([1,1,0,0])
did=(after[D==1]-before[D==1]).mean()-(after[D==0]-before[D==0]).mean()
assert did==-8  # apparent reduction of 8 points even though nobody receives treatment
# A separate composition example has identical changes within every store, but an unpaired mean misleads.
pre=np.array([20.,10.]); post=np.array([18.,8.]); observed_post=np.array([True,False])
unpaired=float(post[observed_post].mean()-pre.mean())
paired=float((post-pre)[observed_post].mean())
# Three periods, common trend +2 per period, treatment -3 only at final date in this illustration.
period=np.tile([0,1,2],4); store=np.repeat(np.arange(4),3); treated=np.repeat(D,3)
y=np.repeat([10.,12.,14.,16.],3)+2*period-3*treated*(period==2)
design=np.column_stack([np.ones(12),pd.get_dummies(store,drop_first=True,dtype=float),
                        pd.get_dummies(period,drop_first=True,dtype=float),treated*(period==2)])
coef=np.linalg.lstsq(design,y,rcond=None)[0]
assert np.isclose(coef[-1],-3)
answer=dict(false_reduction=-float(did),unpaired_change=unpaired,paired_change=paired,
            fixed_effect=float(coef[-1]))
'''
}

# Prompt, flawed reasoning, transfer task, and explicit marking criteria.
TASKS = {
1: ('Calculate complete-record rates for both plausible C values and bounds for all 190 opportunities.',
    'A colleague fills B with zero and adds both C rows because every source row must count. Identify both errors.',
    'A clinic reports 4 failures among 20 visits and another reports 9 among 180. Compare the visit-weighted and clinic-weighted rates. Which answers a patient-level question?',
    'Show 18/140 and 22/140; all-opportunity bounds use 18/190 and 72/190. Explain target changes. Clinic answer: 6.5% of visits versus 12.5% average clinic rate.'),
2: ('Use the 2×2 table to calculate the stockout probability, both conditional probabilities, and their weighted average.',
    'Someone divides 12 by 100 and calls it P(stockout | long delivery). Explain the denominator mistake and what 12/100 actually measures.',
    'Keep conditional risks 10% and 30%, but change the long-delivery share to 75%. Calculate the new mean; explain whether this proves delivery causes stockouts.',
    'Show 18%, 10%, 30%, and .6×.1+.4×.3=.18. Transfer mean is 25%. State the population mix and avoid a causal claim.'),
3: ('Plan a 95% audit margin of ±1 point using SD=4 points. Compare with a 40-store budget at 25 CU per store.',
    'An analyst treats 140 product-days at each of 30 stores as 4,200 independent stores. Explain what uncertainty this would miss.',
    'Plan equal randomized arms for a 2-point improvement with SD=4, 80% power and a two-sided 5% test. What changes if stores share a delivery team?',
    'Round upward to 62 audited stores and 63 per trial arm. State normal-approximation and independence assumptions; cluster planning needs team counts and within-team dependence.'),
4: ('Fit a line to the five equally likely values and compare the three candidate squared losses.',
    'Residuals sum to zero, so the population conditional mean must be linear. Diagnose this argument using the residual pattern.',
    'A service-time curve is U-shaped. Explain how zero Pearson correlation could coexist with strong predictability and choose a diagnostic.',
    'Recover intercept 2, slope 0, losses 34,14,24, and residuals 2,-1,-2,-1,2. Distinguish sample orthogonality from correct mean specification.'),
5: ('Remove the other columns from both delivery and stockouts, fit the residual slope, and compare with the full model.',
    'For an urban slope b1+b5, an analyst adds the two standard errors. Replace this with a covariance calculation.',
    'The same stores are observed for 12 weeks. Which uncertainty method would allow within-store dependence, and what must still hold between stores?',
    'Reproduce the full coefficient with both residualizations; include 2V15. Name the reference group in the interaction model. Clustering requires enough independent store clusters.'),
6: ('Compare the frozen model and last-week rate using final RMSE and five reviews per week.',
    'The rule locating the most stockouts must also produce the greatest alert benefit. Explain the missing causal and cost information.',
    'A hospital can review five patients daily. Define a dated input, a capacity-matched evaluation measure, and a separate design to test whether review helps.',
    'Use identical held-out weeks and 15 review slots. Report burden captured and workload. Do not select a new model using the final period or call captured burden prevented harm.'),
7: ('Calculate worst-case and stated-sensitivity bounds for the missing offered-store outcomes.',
    'Drop offered stores that did not use alerts and compare the remaining users with controls. Explain why random assignment no longer protects this comparison.',
    'Draft a staff-training trial: eligibility, randomization unit, worthwhile effect, outcome timing, nonparticipation, missing-data plan and decision threshold.',
    'Worst-case reduction interval is −14.6 to 5.4 points; restricted missing means 12–20 imply 1.4 to 3.0. Assignment defines intention-to-treat; user effects require more assumptions.'),
8: ('List every backdoor path for both stories and decide whether controlling W suffices.',
    'The adjusted regression has high R², so unrecorded management differences cannot matter. Explain why fit does not justify the graph.',
    'A manager offers coaching based on workload and private knowledge of team ability. Workload is observed; ability is not. Draw the two common-cause paths and propose an identification remedy.',
    'Story A blocks D←W→Y. Story B leaves D←U→Y. Accept nonidentification; randomized offers or credible additional design/data are remedies, not merely adding a proxy.'),
9: ('Implement exact urban status plus the same logit caliper, then inspect retention and all balance measures before outcomes.',
    'A match uses a control four times, so it supplies four independent outcomes. Explain the error and how squared weights affect precision.',
    'A stricter design loses the highest-risk adopters. State whose effect remains, which population cannot be covered, and a defensible next step.',
    'Report retained adopters, unique/reused controls and all three SMDs. Keep targets identical across estimates. The robust regression interval is model-based and conditional on the retained covariates, not a matching interval.'),
10: ('Calculate the false treatment effect after selecting temporarily high stores and compare paired versus unpaired changes.',
     'A nonsignificant pre-trend test proves the future untreated trends are parallel. Explain why this does not follow.',
     'Design a rollout evaluation with three baseline periods and a common start date. Explain store effects, time effects, a placebo, attrition checks and a competing-shock sensitivity.',
     'Recover false reduction 8, unpaired change +3 versus paired −2. The three-period illustration recovers −3. Fixed effects remove stable levels, not differential time-varying shocks.')
}

@lru_cache(maxsize=10)
def evidence(n):
    import retail_case
    scope=dict(retail_case.__dict__)
    exec(compile(WORK[n],f'course-practice-{n}','exec'),scope)
    return scope['answer']
