"""Trace regression standardization and matching on the same voluntary stores."""
from functools import lru_cache

CALCULATIONS = '''# One outcome per store; every input precedes week-17 adoption.
l9_w = world()
l9_post = l9_w['panel'].query("cohort=='Voluntary' and 17<=week<=24")
assert len(l9_post)==400 and l9_post.groupby('store_id').size().eq(8).all()
l9_v = l9_post.groupby(['store_id','offer']).stockout_rate.mean().reset_index()
l9_vars = ['lead_days','urban','baseline_rate']
l9_v = l9_v.merge(l9_w['stores'][['store_id']+l9_vars],on='store_id',validate='one_to_one')
assert len(l9_v)==50 and l9_v.offer.sum()==26 and not l9_v.isna().any().any()
l9_D = l9_v.offer.to_numpy(); l9_y = l9_v.stockout_rate.to_numpy()
l9_X = voluntary_design(l9_v,l9_D)
# Fit the observed outcomes, then change treatment and its interactions together.
l9_beta,l9_V,l9_residual = fit_ols(l9_X,l9_y)
l9_X0 = voluntary_design(l9_v,np.zeros(50))
l9_X1 = voluntary_design(l9_v,np.ones(50))
l9_C = l9_X0-l9_X1; l9_effect = l9_C@l9_beta
l9_v['pred0'] = l9_X0@l9_beta; l9_v['pred1'] = l9_X1@l9_beta
l9_v['reduction'] = l9_effect
l9_c = l9_C.mean(axis=0); l9_se = float(np.sqrt(l9_c@l9_V@l9_c))
l9_targets = [float(l9_effect.mean()),float(l9_effect[l9_D==1].mean()),float(l9_effect[l9_D==0].mean())]
l9_saved = lesson_result(9)
# Nearest neighbors use covariates only; outcomes enter after choosing matches.
l9_tr = l9_v[l9_v.offer==1]; l9_ct = l9_v[l9_v.offer==0]
l9_scale = l9_v[l9_vars].std(ddof=0).to_numpy()
l9_dist = (((l9_tr[l9_vars].to_numpy()[:,None,:]-l9_ct[l9_vars].to_numpy()[None,:,:])/l9_scale)**2).sum(axis=2)
l9_nearest = l9_dist.argmin(axis=1)  # store-ID order breaks exact ties
l9_pairs = [(int(i),int(l9_ct.index[j])) for i,j in zip(l9_tr.index,l9_nearest)]
l9_nn = float(np.mean([l9_y[j]-l9_y[i] for i,j in l9_pairs]))
l9_candidate = l9_ct[['store_id']+l9_vars].copy()
l9_candidate['distance'] = l9_dist[0]
l9_candidate = l9_candidate.sort_values(['distance','store_id']).head(4)
# Exact strata and coarsened strata keep only cells with both options.
l9_groups = []; l9_comparisons = []
l9_frame = l9_v.assign(band=np.floor(l9_v.baseline_rate/5).astype(int))
for l9_cols in [['lead_days','urban'],['lead_days','urban','band']]:
    l9_kept = []; l9_gains = []; l9_cells = []
    for l9_key,l9_g in l9_frame.groupby(l9_cols):
        l9_a = l9_g[l9_g.offer==1]; l9_b = l9_g[l9_g.offer==0]
        l9_cells.append(dict(key=l9_key,n1=len(l9_a),n0=len(l9_b),ids=l9_g.store_id.tolist(),control_mean=float(l9_b.stockout_rate.mean())))
        if len(l9_a) and len(l9_b):
            l9_kept.extend(l9_a.index); l9_gains.extend(l9_b.stockout_rate.mean()-l9_a.stockout_rate)
    l9_groups.append(l9_cells)
    l9_comparisons.append(dict(n=len(l9_kept),match=float(np.mean(l9_gains)),model=float(l9_effect[l9_kept].mean()),kept=l9_kept))
# Fit a regularized logistic score using only the recorded starting variables.
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
l9_score_model = make_pipeline(StandardScaler(),LogisticRegression(C=1.,max_iter=1000))
l9_score_model.fit(l9_v[l9_vars],l9_D)
l9_score = l9_score_model.predict_proba(l9_v[l9_vars])[:,1]
l9_v['score'] = l9_score; l9_v['logit'] = np.log(l9_score/(1-l9_score))
l9_caliper = .2*l9_v.logit.std(ddof=1); l9_ps_pairs = []
# A fixed logit caliper rejects distant candidates; controls may be reused.
l9_controls = l9_v[l9_v.offer==0]
for l9_a in l9_v[l9_v.offer==1].itertuples():
    l9_j = nearest_score_match(l9_controls,l9_a.logit)
    if abs(l9_controls.loc[l9_j,'logit']-l9_a.logit)<=l9_caliper:
        l9_ps_pairs.append((int(l9_a.Index),int(l9_j)))
l9_kept = [i for i,j in l9_ps_pairs]; l9_used = [j for i,j in l9_ps_pairs]
l9_ps = float(np.mean([l9_y[j]-l9_y[i] for i,j in l9_ps_pairs]))
l9_comparisons.append(dict(n=len(l9_kept),match=l9_ps,model=float(l9_effect[l9_kept].mean()),kept=l9_kept))
l9_balance = []
# Keep the original pooled standard deviation fixed; count reused controls again.
for l9_col in l9_vars:
    l9_denom = np.sqrt((l9_tr[l9_col].var(ddof=1)+l9_ct[l9_col].var(ddof=1))/2)
    l9_before = (l9_tr[l9_col].mean()-l9_ct[l9_col].mean())/l9_denom
    l9_after = (l9_v.loc[l9_kept,l9_col].mean()-l9_v.loc[l9_used,l9_col].mean())/l9_denom
    l9_balance.append(dict(variable=l9_col,before=float(l9_before),after=float(l9_after)))
l9_urban_counts = [int(l9_v.loc[l9_kept,'urban'].sum()),int(l9_v.loc[l9_used,'urban'].sum())]
l9_example = l9_v.iloc[0].to_dict()
l9_nn_unique = len(set(j for i,j in l9_pairs))
l9_ps_unique = len(set(l9_used))
# Verify published results without changing the shared generator or estimates.
assert np.allclose(l9_targets[:2],[l9_saved['estimate'],l9_saved['att']])
assert np.isclose(l9_se,l9_saved['se']) and np.isclose(l9_nn,l9_saved['matching_att'])
assert np.allclose(l9_beta,l9_saved['coefficients'])
for l9_actual,l9_expected in zip(l9_comparisons,l9_saved['depth']['matching']):
    assert l9_actual['n']==l9_expected['matched_adopters'] and np.isclose(l9_actual['match'],l9_expected['estimate'])
for l9_actual,l9_expected in zip(l9_balance,l9_saved['depth']['balance']):
    assert np.allclose([l9_actual['before'],l9_actual['after']],[l9_expected['before'],l9_expected['after']])
assert l9_ps_unique==10 and l9_urban_counts==[11,16]
'''

CODE_TITLES = [
 'Construct fifty complete store outcomes from four hundred dated records',
 'Predict both options and average their contrasts for the chosen population',
 'Rank potential controls using standardized starting conditions',
 'Form exact and coarsened cells with both treatment options',
 'Estimate adoption probabilities from measured starting conditions',
 'Apply the logit caliper and retain the accepted adopter comparisons',
 'Measure balance with the original scale and repeated control weights',
 'Verify the published estimates and the failed urban balance check',
]
DETAIL_TITLES = [
 'An explicit data contract keeps treatment and outcome periods aligned',
 'Logical filters and category labels determine the population being analyzed',
 'The fitted design separates baseline relationships from treatment heterogeneity',
 'The average contrast carries coefficient uncertainty into the population estimate',
 'Exact cells weight each retained adopter equally',
 'Standardization makes the distance rule reproducible across measurement units',
 'Propensity scores summarize assignment while overlap still limits the comparison',
 'Repeated controls retain their matching weights in the balance calculation',
 'Matching uncertainty must account for how comparisons were constructed',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    scope=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson9-worked-calculations','exec'),scope)
    return scope

def restore(c):
    from retail_ui import table,formula,p
    from retail_content import section
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();r=d['l9_saved'];v=d['l9_v'];f=lambda x:f'{x:.2f}';f3=lambda x:f'{x:.3f}'
    c['authored_sections']=True;c['sections']=[]
    c['headlines']={k:val for k,val in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    def block(title,visual,*notes):return teach(title,visual.replace('\n','<br>') if 'class="calculation"' in visual else visual,list(notes))
    def put(key,title,body,phase='General theory'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    c['brief']='Managers chose whether to adopt replenishment alerts. How much did alerts help, once we account for their different starting conditions? Learn two ways to construct the missing comparison: predict both options for each store, or find comparable stores operating without alerts. Then trace both methods through the same records.'
    c['scope']=['Define the population and its observed comparison','Calculate adjusted effects using regression and matching','Judge balance before interpreting a matched estimate']
    put('ideal-experiment','Define the experiment the observed comparison should emulate',
      block('An observational evaluation begins with the experiment we would like to run',bullets('Specify eligible units, treatment and usual operations','Set the assignment date and outcome window','Choose whose average effect matters','Explain how the observed assignment differs from random allocation'),
        'A target trial is a precise description of the experiment that would answer the decision question. It fixes eligibility, treatment strategies, time zero, follow-up, outcome and effect target before choosing an estimator. A controlled experiment assigns treatment deliberately; a natural experiment uses an external assignment event whose credibility must be argued. Voluntary adoption needs a comparison justified by recorded starting conditions.')+
      block('Comparable starting conditions connect observed outcomes to the causal question',formula('(Y(0), Y(1)) ⟂ D | X\n0 < P(D=1|X=x) < 1\nmⱼ(x) = E[Y|D=j,X=x]'),
        'D is treatment and X is the chosen set of pre-treatment controls. Conditional exchangeability says assignment carries no further information about potential outcomes once X is held fixed. Consistency relates the observed outcome to the defined treatment, and overlap supplies both options at relevant profiles. Lesson 8 develops the graph argument. Here we turn its adjustment set into estimated conditional means, m₀ and m₁.')+
      block('Assignment history determines controls before any regression is fitted',bullets('Common causes can make adoption endogenous','Earlier outcomes can influence later adoption','Treatment-induced effort belongs inside the total effect','Internal validity and transfer to other populations are separate questions'),
        'Endogeneity here means that an unadjusted assignment comparison mixes treatment with other outcome determinants. Reverse causation should be dated explicitly: earlier performance can affect adoption, which then affects later performance. A time-indexed account avoids a circular graph. Use the causal story to select controls; a small p-value cannot decide which variables belong. Internal validity concerns the effect for the study population, while external validity concerns its relevance elsewhere.'))
    put('regression-theory','Predict both potential outcomes for the same target rows',
      block('Regression adjustment predicts two outcomes for each target unit',formula('Fit m̂₀(x) and m̂₁(x) using observed outcomes\nτ̂ᵢ = m̂₁(xᵢ) − m̂₀(xᵢ)\nATE estimate = (1/n) Σᵢ τ̂ᵢ'),
        'Fit a conditional outcome relationship using each unit’s observed treatment and outcome. Then hold its baseline characteristics fixed and predict under treatment zero and one. Only one outcome was observed for that unit; both model predictions are estimates, not newly observed counterfactuals. Averaging the paired differences standardizes to the distribution of X in the target rows.')+
      block('Treatment interactions let the effect vary across starting profiles',formula('m̂(D,X) = β̂₀ + β̂D D + β̂X X + γ̂ DX\nτ̂(x) = β̂D + γ̂x'),
        'A model without treatment interactions imposes the same additive treatment contrast at every profile. Adding interactions between D and selected baseline variables allows that contrast to vary. Interacting two controls with each other can make the baseline outcome surface more flexible, but does not itself create treatment-effect heterogeneity. Specification should express the comparison and effect structure being estimated.')+
      block('The population weights turn individual contrasts into ATE or ATT',table(['Target','Rows averaged','Question'],[['ATE','All eligible units','What is the average effect here?'],['ATT','Treated units','How much did participants gain?'],['ATU','Untreated units','What could nonparticipants gain?']], 'All averages use the same fitted response surfaces'),
        'ATE, ATT and ATU are average treatment effects for all units, treated units and untreated units. Change the rows over which predictions are averaged, not the definition of a unit’s contrast. With heterogeneous effects the targets differ. A regression coefficient at one reference profile need not equal any of these population averages.'))
    put('matching-theory','Construct the comparison before reading its outcome',
      block('Matching uses comparable untreated units to supply the missing comparison',formula('For treated unit i, choose controls using X\nτ̂ᵢ = Yᵢ − Σⱼ wᵢⱼYⱼ, with Σⱼ wᵢⱼ = 1\nAverage over the retained treated units'),
        'Weights describe which untreated observations supply a treated unit’s comparison. An exact cell may use the mean of several controls; nearest-neighbor matching may use one. Choose matches from baseline variables before examining outcome differences. The resulting average targets the retained treated population, which may exclude treated units with no suitable comparison.')+
      block('Exact, coarsened and distance matching define similarity differently',table(['Method','How a comparison qualifies'],[['Exact','Same values of selected baseline variables'],['Coarsened exact','Same prespecified categories or bands'],['Nearest neighbor','Smallest distance on scaled variables'],['Propensity score','Nearby estimated probability of adoption']], 'The matching rule determines retained units and weights'),
        'Exact matching becomes sparse as the number of distinct profiles grows. Coarsening trades finer comparability for more populated cells. A distance rule permits approximate matches but needs a scale and a policy for poor candidates. A propensity score summarizes assignment probabilities; equal estimated scores do not guarantee that a particular small matched sample balances every variable.')+
      block('A caliper limits distance while replacement permits control reuse',bullets('Caliper: reject a candidate beyond a chosen distance','With replacement: a control can serve several treated units','Without replacement: earlier choices restrict later options','Record exclusions, repeated controls and the tie rule'),
        'A nearest control can still be far away, so proximity needs to be judged rather than assumed. Replacement can preserve closer comparisons but concentrates weight on a smaller number of distinct controls. The same control’s outcome is then used more than once. Tie-breaking and matching order should be explicit so another analyst can reproduce the design.')+
      block('Balance evaluates the constructed comparison on the original covariates',formula('Standardized mean difference =\n(treated mean − weighted control mean) / original pooled SD'),
        'Hold the original pooled within-group standard deviation fixed so the before and after numbers use the same scale. Values near zero indicate similar means; the sign shows which group is higher. Inspect distributions and overlap as well as means. Outcome prediction accuracy and assignment classification accuracy do not replace balance diagnostics.'))
    app='Worked application'
    put('read-data','Build the store-level analysis table',
      block('Four hundred dated records become fifty independent store outcomes',table(['Preparation step','Rows or units','Purpose'],[['Voluntary cohort, weeks 17–24','400 store-weeks','One common follow-up window'],['Average eight weeks within each store','50 stores','One outcome per decision unit'],['Join starting conditions by store ID','50 complete rows','One-to-one merge'],['Split by observed adoption','26 adopters; 24 controls','Define the observed groups']], 'Stores S051–S100; no stores are dropped in this release'),
        'Each store contributes eight post-period observations. Their mean is the outcome for this analysis, so the regression has fifty observations rather than four hundred independent store-weeks. The outcome remains a stockout percentage. The supplied lab checks eight weeks per store, a unique merge, complete inputs and the treatment count. Each week has the same monitoring exposure, making the mean of weekly rates appropriate here.')+
      block('The analysis fixes adoption at week seventeen and controls measured earlier',table(['Field','Definition'],[['D','1 for adoption; 0 for usual operations'],['Y','Mean stockout percentage, weeks 17–24'],['L','Delivery lead time in days'],['U','Urban indicator: 1 urban, 0 otherwise'],['B','Baseline stockout percentage, weeks 1–8']], 'One row per store; starting variables are measured before adoption'),
        'The measured adjustment set is delivery time, urban location and baseline performance, as established in Lesson 8. Post-alert review effort and escalations are not added to this total-effect comparison. Coding D as a binary indicator, checking its counts and recording exclusions are part of the estimand: they determine which units and options are compared. Unordered categories would use indicators with named reference levels rather than arbitrary integer scores.')+
      block('The first rows show both adoption groups in the same data structure',table(['Store','D','L','U','Baseline %','Outcome %'],[[x.store_id,int(x.offer),int(x.lead_days),int(x.urban),f(x.baseline_rate),f(x.stockout_rate)] for x in v.head(5).itertuples()], 'Observed outcomes; model predictions come next'),
        'S051 and S052 operated without alerts, while S053 and S054 adopted them. Baseline is measured before the choice, and outcome after it. The table lets us trace a complete row through the model and matching rules. It also distinguishes an observed post-period rate from the fitted predictions that follow.'))
    put('calculate','Calculate the two fitted outcomes and their difference',
      block('A positive reduction reverses the signed stockout effect',formula('Signed effect = alert rate − usual-operation rate\nReported reduction = usual-operation rate − alert rate'),
        'General theory uses treatment minus control. In this application fewer stockouts are better, so every displayed improvement is the negative of the signed treatment effect. Rates are percentages and differences are percentage points. Keep that convention for the regression, matched pairs and cost calculation.')+
      block('The fitted model separates usual operations from the alert adjustment',formula('m̂(D,L,U,B) = m̂₀(L,U,B) + D × â(L,U)\nm̂₀ = 7.110 + 1.137(L−3.5) + 1.707U + 0.296B\nâ = −3.188 − 0.957(L−3.5) − 0.294U'),
        'Least squares fits all seven coefficients jointly on the fifty observed rows. Centering delivery time at 3.5 makes the treatment coefficient refer to a nonurban store with that lead time. The baseline-rate slope is common across treatment states in this specification. The appendix gives more digits, the design matrix and the exact reproducible code. Rounded coefficients here are for reading; calculations use full precision.')+
      block('S051 has an estimated usual-operation stockout rate of 11.658 percent',formula('S051: L=3, U=1, B=11.517857\nm̂₀ = 7.110133 + 1.137155(−0.5)\n       + 1.707366 + 0.295988(11.517857)\n     = 11.658070%'),
        'Use the starting variables from S051’s actual row and set D=0. This is the fitted conditional mean, not its observed outcome of 12.678571%. Residual variation explains why a fitted value and observed value need not agree. Keeping that distinction clear prevents a predicted counterfactual from being presented as a measured result.')+
      block('Turning alerts on changes S051’s prediction by minus 3.004 points',formula('â = −3.188210 − 0.956853(−0.5) − 0.294452\n   = −3.004235 points\nm̂₁ = 11.658070 − 3.004235 = 8.653835%\nReduction = 11.658070 − 8.653835 = 3.004235'),
        'Set D=1 and change both D interactions with it. Delivery time, location and baseline performance stay fixed. The baseline term cancels in this paired difference because this model contains no D×B interaction; that cancellation is a specification choice, not a general property of baseline adjustment. S051 was a control store, so its alert outcome is unobserved.')+
      block('Repeating the calculation yields a paired reduction for every store',table(['Store','Usual prediction %','Alert prediction %','Reduction points'],[[x.store_id,f(x.pred0),f(x.pred1),f(x.reduction)] for x in v.head(5).itertuples()], 'Same five starting profiles; both options predicted for each'),
        'S053 has a longer delivery cycle than S051 and therefore a larger predicted reduction under the fitted treatment interaction. We do not average the predictions for separate observed groups. We predict both options on the same target rows and then average their paired differences.'))
    put('population-effects','Average the contrasts and quantify their uncertainty',
      block('All fifty stores average a 3.01-point predicted reduction',formula('Average usual prediction = 11.22195%\nAverage alert prediction = 8.21332%\nAverage paired reduction = 11.22195 − 8.21332 = 3.00864 points'),
        'The difference of the two target averages equals the average of the fifty paired differences. Every store has weight 1/50. This standardized estimate uses delivery time, location and baseline performance together, extending Lesson 8’s broader delivery-group demonstration.')+
      block('Adopter weighting raises the model’s average reduction to 3.38 points',table(['Target population','Stores','Model reduction'],[['All stores',50,f(d['l9_targets'][0])],['Adopters',26,f(d['l9_targets'][1])],['Nonadopters',24,f(d['l9_targets'][2])]], 'Same fitted model; different target weights; percentage points'),
        'Adopters include more profiles with larger predicted benefits. The all-store estimate is the weighted average of the adopter and nonadopter estimates: (26/50)×3.38356+(24/50)×2.60247=3.00864. A management question about current adopters should use their target, while expansion to current nonadopters has a different population.')+
      block('The interval uses uncertainty in the average model contrast',formula('SE = 0.31489 points\n95% interval = 3.00864 ± 1.96 × 0.31489\n= [2.39145, 3.62583] points'),
        'The paired predictions share estimated coefficients and are therefore correlated. Averaging individual standard errors is incorrect. Average the contrast vectors first, then use the coefficient covariance matrix. This interval uses HC1 heteroskedasticity-robust covariance, a normal multiplier and the observed target covariates held fixed. Its sampling uncertainty is distinct from the substantive assignment assumptions.')+
      block('Richer adjustment changes the estimate while preserving the analysis rows',table(['Specification','Reduction','95% interval'],[[x['model'],f(x['reduction']),f(x['low'])+' to '+f(x['high'])] for x in r['depth']['models']], 'All specifications use the same fifty stores'),
        'The raw comparison gives 2.06 points. A common additive treatment contrast after controlling starting variables gives 2.90. Allowing delivery and urban interactions and standardizing to all fifty stores gives 3.01. These are transparent specification changes on fixed rows. Choose controls and effect structure from the comparison argument, rather than selecting whichever estimate is largest.'))
    first=d['l9_tr'].iloc[0];scale=d['l9_scale'];nearest=d['l9_candidate'].iloc[0]
    put('nearest-matching','Follow one adopter through a distance-based match',
      block('Scaling makes delivery days and baseline percentages comparable in a distance',formula('Distance²(i,j) = Σₖ [(Xᵢₖ−Xⱼₖ)/sₖ]²\n'+f's = ({f3(scale[0])} delivery days, {f3(scale[1])} urban, {f3(scale[2])} baseline points)'),
        'Use full-cohort standard deviations with divisor n, not n−1, for this distance rule. A large numerical baseline percentage should not dominate merely because it has different units from an urban indicator. The squared Euclidean distance is a similarity rule, not a probability or a causal test. This example uses matching with replacement and no distance caliper.')+
      block('S053’s closest candidate is S052 under the stated distance rule',table(['Candidate','L','U','Baseline %','Distance²'],[[x.store_id,int(x.lead_days),int(x.urban),f(x.baseline_rate),f3(x.distance)] for x in d['l9_candidate'].itertuples()], 'S053: lead 5 days, urban 1, baseline 17.50%; four closest controls'),
        f'S053 is the first adopter in store-ID order. Compare it with every one of the 24 controls before sorting. S052 has lead time 4, urban indicator 1 and baseline rate 13.839286. Its distance is ((5−4)/{scale[0]:.6f})²+((1−1)/{scale[1]:.6f})²+((17.5−13.839286)/{scale[2]:.6f})²={nearest.distance:.6f}. Outcomes play no role in choosing this candidate.')+
      block('Only after selecting S052 do we calculate the observed pair difference',formula('S052 usual-operation outcome: 14.37500%\nS053 alert outcome: 10.44643%\nMatched reduction: 14.37500 − 10.44643 = 3.92857 points'),
        'This pair uses two different stores’ observed outcomes. It therefore differs from the regression’s two fitted outcomes for a single profile. S052 is the nearest available control under the chosen rule, not an identical store. The baseline differences remain visible in the candidate table.')+
      block('The twenty-six matched pairs average a 2.90-point reduction',table(['Adopter','Selected control','Observed reduction'],[[x['adopter'],x['comparison'],f(x['reduction'])] for x in r['matches']], 'First five pairs; average uses all twenty-six'),
        f'The full average is {r["matching_att"]:.5f} points. All 26 adopters remain and {d["l9_nn_unique"]} distinct controls supply their comparisons. S064 serves both S056 and S063 in the displayed extract, so its outcome receives more than one pair weight. The model estimate for the same 26 adopters is 3.38356 points. Matching and regression construct the missing comparison differently; neither wins simply by producing a preferred number.'))
    cells=d['l9_groups'][0];cell=next(g for g in cells if g['key']==(3,1));g=v[(v.lead_days==3)&(v.urban==1)];a=g[g.offer==1];b=g[g.offer==0]
    put('exact-matching','Use cells to make eligibility and exclusions visible',
      block('Exact matching on delivery and location retains twenty adopters',table(['Delivery days','Urban','Adopters','Controls','Use cell?'],[[int(x['key'][0]),int(x['key'][1]),x['n1'],x['n0'],'Yes' if x['n1'] and x['n0'] else 'No'] for x in cells[:4]+cells[-2:]], 'Selected exact cells, including both excluded profiles; all cells are in the lab'),
        'Within each lead-time and urban cell, average control outcomes and compare each adopter with that mean. Cells lacking either group cannot supply an observed within-cell contrast. Across all cells, 20 of 26 adopters remain and six are excluded. Exactness applies to these two variables only: baseline stockout rates can still differ within a cell.')+
      block('Each retained adopter receives the mean of its exact-cell controls',formula(f'Delivery 3 days, urban 1: {len(a)} adopters and {len(b)} controls\nControl-cell mean = {b.stockout_rate.mean():.5f}%\nS054 reduction = {b.stockout_rate.mean():.5f} − {v.loc[v.store_id=="S054","stockout_rate"].iloc[0]:.5f}\n= {b.stockout_rate.mean()-v.loc[v.store_id=="S054","stockout_rate"].iloc[0]:.5f} points'),
        'Every adopter in the cell uses the same control mean, but keeps its own observed alert outcome. Pool the resulting adopter-level differences across eligible cells. Giving each cell equal weight would answer a different question because cell sizes differ. The full exact-cell estimate is 2.56205 points for the retained twenty adopters.')+
      block('Adding five-point baseline bands leaves thirteen comparable adopters',formula('Baseline band = floor(B / 5)\nBand 2: 10% ≤ B < 15%\nMatch on delivery days, urban status and baseline band\nRetained: 13/26 adopters; reduction: 2.79567 points'),
        'The bands are defined before reading outcome differences. This coarsened exact match adds baseline comparability to the previous two variables, so fewer cells contain both treatment groups. For example, baseline 11.517857% belongs to band 2 and 17.5% to band 3. The reduction refers to thirteen retained adopters, not automatically all twenty-six. Closer grouping and wider population coverage are competing design considerations.'))
    put('propensity-matching','Inspect what the fitted assignment score actually achieves',
      block('The propensity model predicts adoption from the three starting variables',formula('e(X) = P(D=1|X)\nFit logistic adoption on standardized L, U and B\nMatch on logit(ê) = log[ê/(1−ê)]'),
        'This is a model of adoption, not of the stockout outcome. The supplied implementation standardizes inputs and fits regularized logistic regression with C=1. The true propensity score has a balancing property; a fitted score and finite matching procedure still need their balance checked. Genuine absence of an untreated comparison at a relevant profile cannot be repaired by compressing variables into a score.')+
      block('The logit caliper retains nineteen adopters using ten distinct controls',formula(f'Caliper = 0.2 × SD(logit(ê)) = {d["l9_caliper"]:.5f}\nKeep nearest candidate only when distance ≤ caliper\n19 adopters retained; 7 excluded; 10 unique controls'),
        'For each adopter, choose the closest control logit with replacement. Among distances tied within 10⁻⁸, use the lowest store ID. This declared tolerance keeps the comparison stable when reading the rounded CSV exports. The caliper uses the sample standard deviation over all fifty logits. Inspect the original variables before interpreting the outcome difference; nineteen accepted pairs do not by themselves establish comparability.')+
      block('Propensity matching improves delivery balance but worsens urban balance',table(['Starting variable','Before SMD','After SMD'],[[{'lead_days':'Delivery time','urban':'Urban indicator','baseline_rate':'Baseline stockout rate'}[x['variable']],f(x['before']),f(x['after'])] for x in d['l9_balance']], 'SMD: standardized mean difference; closer to zero means closer means'),
        'Delivery imbalance falls from 0.88 to zero. Baseline imbalance improves in magnitude from 0.64 to −0.24, but urban imbalance worsens from −0.09 to −0.52. The sign reversal tells us that the weighted controls now include a larger urban share. The design improves some dimensions while making another materially less comparable.')+
      block('Eleven urban adopters face sixteen urban control appearances',formula('Matched adopter urban share = 11/19 = 57.9%\nWeighted control urban share = 16/19 = 84.2%\nDifference = −26.3 percentage points\nStandardized difference = −0.52'),
        'There are ten unique controls but nineteen control appearances. Counting each distinct control only once would describe a different comparison from the estimator. Urban location matters to the outcome and to the modeled alert benefit, so this substantial mismatch cannot be dismissed merely because delivery time balances.')+
      block('The failed balance check calls for a revised comparison before a causal conclusion',bullets('Keep the 3.54-point result as a diagnosis of this attempted match','Try exact urban matching before ranking candidates within urban groups','Review baseline balance, distances and lost adopters again','Judge the design before reopening outcome differences'),
        'The proposed revision is a design exercise, not a new verified estimate. Exact urban matching would remove urban mean imbalance for retained pairs, but may lose additional adopters or worsen another covariate. Another option is to reconsider nonlinear terms in the assignment model using baseline balance. Freeze a defensible comparison rule and disclose its retained target before estimating and reporting the outcome contrast.'))
    put('interpret','Compare methods for identical target populations',
      block('Comparing the same retained adopters separates method differences from population changes',table(['Matching rule','Adopters','Matched reduction','Model on same adopters'],[['Nearest covariates',26,f(d['l9_nn']),f(d['l9_targets'][1])]]+[[name,x['n'],f(x['match']),f(x['model'])] for name,x in zip(['Exact L and U','Plus baseline bands','Propensity caliper'],d['l9_comparisons'])], 'Percentage points; propensity result fails the displayed urban balance check'),
        'The model is fitted once on all fifty stores; only its averaging rows change. For the nineteen propensity-retained adopters, its average is 3.03134 points, compared with the matching attempt’s 3.54323. Comparing the latter directly with the 3.38356 model average for all twenty-six adopters would mix a method change with a population change. Agreement alone would not prove identification, and disagreement should trigger inspection of the constructed comparisons.')+
      block('The spending question uses the effect for the stores covered by the decision',formula('One-point reduction saves 140 × 0.01 × 6 = 8.4 CU/week\nAll-store model saving = 8.4 × 3.00864 − 20\n= 5.27 CU per store-week'),
        'The stated accounting scenario charges 20 currency units per week for alerts and values each avoided stockout product-day at 6. The all-store model estimate implies a positive average saving, with uncertainty inherited from the effect estimate. Continuing current adopters and extending to nonadopters use their respective target averages. Carry this observational evidence alongside the randomized pilot, with its population and design stated.'))
    put('act','Carry a defensible comparison into the management memo',
      block('The recommendation reports the target, calculation and comparison quality together',bullets('All-store adjusted reduction: 3.01 points; interval 2.39–3.63','Current-adopter model reduction: 3.38 points','Matching estimates name their retained adopters','The propensity attempt needs redesign because urban balance worsens'),
        'The management memo should not select one attractive number from a menu of estimators. It should state which stores the number represents and show how their missing comparison was constructed. The next lesson uses a separate rollout cohort and compares changes over time. The general task remains the same: build a credible comparison for the decision population.'))
    for s in c['sections']:
        if s['id'] not in {'ideal-experiment','regression-theory','matching-theory'}:s['phase']=app
    next(s for s in c['sections'] if s['id']=='calculate')['body']+='<p><a href="lesson-9-appendix.html#calculation">Follow this calculation further →</a></p>'
    c['memo']='For the fifty voluntary-cohort stores, the outcome model estimates a 3.01-point reduction (95% interval 2.39–3.63). The adopter-target estimate is 3.38 points. The propensity matching attempt retains nineteen adopters but worsens urban balance, so its 3.54-point result motivates redesign rather than a separate rollout claim. Report each matching comparison for its retained stores.'
    c['question']='The propensity attempt gives 3.54 points. Should the memo compare it with the model’s 3.38-point adopter average and present the larger number as stronger evidence?'
    c['answer']='First use the model average for the same nineteen retained adopters: 3.03 points. Then inspect comparison quality: the propensity attempt worsens urban balance, so a larger estimated reduction does not make its causal evidence stronger. Revise the comparison using starting variables, then reassess balance and the retained target.'
    c['presentation_points']={
      'memo':['All-store model: 3.01 points; current-adopter model: 3.38','Name the stores retained by each matching rule','The propensity attempt needs a better urban comparison'],
      'question':['Does the larger propensity-matching estimate provide stronger evidence?','Which model average belongs beside it?'],
      'answer':['Compare the same nineteen adopters: matching 3.54; model 3.03','Urban balance worsens, so inspect and revise the design','A larger estimate does not establish a better comparison']
    }
    c['headlines']['memo']=['The memo connects each estimate to its population and comparison quality','Does a larger estimate make the matched comparison more convincing?']
    c['headlines']['decision-brief']=['Regression and matching construct the missing comparison for voluntary adopters']
    c['bigger']='Regression and matching make the unobserved alternative concrete in different ways. Regression predicts two outcomes for each target profile; matching supplies observed comparisons from other units. In both methods, the credibility of the comparison and the population weights determine what the estimate can contribute to a decision.'
    c['transfer_points']=['A comparison needs a defined population and assignment argument','Predictions or matches make the missing alternative explicit','Balance and target weights give an estimate its interpretation']
    c['code']=CALCULATIONS
    c['technical']=[
      'Keep S051–S100 and weeks 17–24: 400 store-week records become fifty means. Join one row of pre-adoption delivery time, urban status and weeks 1–8 baseline rate per store. Assert complete rows, eight observations per store, 26 adopters and 24 controls. All displayed fitted and matching results use this table.',
      'The code reconstructs the paired regression predictions, three target averages, nearest-neighbor comparisons, exact and coarsened cells, propensity pairs, reused-control weights and same-target model averages. It verifies the published estimates. Variables beginning l9_ retain each intermediate result for inspection in the notebook.',
      'HC1 covariance uses n/(n−p)=50/43 with the seven-column outcome design. The normal interval uses the mean all-store contrast and treats those observed covariates as fixed. Matching estimates are point comparisons: no independent-pairs standard error is claimed when controls are reused.',
      'Revise the propensity comparison by requiring the same urban status before selecting a nearby control. Use only starting variables to choose the design. Record retained adopters and reused controls, then examine all three balance measures. After fixing that design, compare its effect with the fitted-model average for exactly those retained adopters.'
    ]
    details=[
      (table(['Check','Implementation or meaning'],[['Time zero','Week 17; controls measured before adoption'],['Outcome','Eight weekly rates averaged within each store'],['Join','Unique store ID; validate one-to-one'],['Eligibility','50 voluntary stores; no missing inputs'],['Target','All stores or an explicitly named retained subset']], 'The same data contract used in the main calculation'),
       'A row count is an analytical fact, not merely a software check. Inspect missing-value codes, treatment coding and any eligibility filters before fitting. If a future release drops a store, report why and recalculate the counts and target weights. The present release has no analysis-row exclusions before matching. Unequal exposure would require an explicit choice between exposure-weighted and equally weighted rates.'),
      (formula('Inclusive eligibility: (size ≥ 50) AND (size ≤ 5000)\nA retained value must satisfy both limits\nUnordered categories use indicators with named reference levels'),
       'This is a general preparation example adapted from the original deck, not an extra retail eligibility restriction. Using OR between the two inequalities retains every finite value because at least one side is always true. Treat missing-category codes as missing, not as numerical magnitudes. A log requires positive values and changes interpretation. Stable category labels and a reproducible reference group are preferable to treating arbitrary factorization codes as ordered measurements. Lessons 1, 4 and 5 develop these preparation and specification tools.'),
      (table(['Design term','Coefficient'],[[name,f'{value:.6f}'] for name,value in zip(['Intercept','D','L−3.5','U','B'],d['l9_beta'][:5])], 'The first five jointly fitted coefficients')+formula('D×(L−3.5): −0.956853; D×U: −0.294452'),
       'The complete design is [1,D,L−3.5,U,B,D(L−3.5),DU]. The two treatment interactions produce a profile-specific signed effect βD+γL(L−3.5)+γUU. Both interactions must change when predicting a new treatment state. The code retains full precision. A baseline-only interaction would change m₀ and m₁ without necessarily changing their difference; a D×B term would allow baseline-dependent effects.'),
      (formula('Cᵢ = X₀ᵢ − X₁ᵢ; c = mean(Cᵢ)\nc = [0, −1, 0, 0, 0, 0.36, −0.56]\nV = (X′X)⁻¹ X′diag(e²)X (X′X)⁻¹ × 50/43\nSE(cβ̂) = √(cVc′) = 0.31489'),
       'All rows share the same estimated coefficient vector, so their contrasts are correlated. The covariance calculation automatically carries these relationships into the average. For an adopter or retained-subset target, recompute c from those rows. This is model-based sampling uncertainty conditional on the observed design; uncertainty from target-population sampling or a matching search is a different problem.'),
      (formula('For each eligible cell g: Δg = mean(Y₀|g) − mean(Y₁|g)\nReduction = Σg (n₁g / Σh n₁h) Δg\nOnly cells with n₁g>0 and n₀g>0 contribute'),
       'Averaging one control-cell comparison per retained adopter equals weighting each cell difference by its adopter count. The exact rule uses lead time and urban status; the coarsened rule also uses floor(B/5). The weights sum to one over the retained treated population. Both the eligible set and its target change when the additional bands remove cells.'),
      (formula('sₖ² = (1/50) Σᵢ(Xᵢₖ−X̄ₖ)²\nd²(i,j) = Σₖ[(Xᵢₖ−Xⱼₖ)/sₖ]²\nOne nearest control per adopter, with replacement'),
       'Rows are sorted by store ID before argmin, giving a deterministic first choice for exact distance ties. Standardizing by the same common scale makes the distance dimensionless. The notebook keeps l9_dist, l9_pairs and l9_candidate so students can audit a selected control and its alternatives. A covariance-aware distance or a caliper would define a different design and should be evaluated through retained populations and balance.'),
      (formula('True score: e(X)=P(D=1|X)\nBalancing property: D ⟂ X | e(X)\nEstimated score here: standardized logistic regression, C=1\nCaliper: 0.2 × sample SD of all fifty fitted logits'),
       'The balancing property concerns the true assignment probability. Causal identification additionally requires the relevant conditional exchangeability, consistency and overlap assumptions. Estimating a score and finding a nearby value does not create overlap where none exists. In this implementation C=1 sets regularization strength; the caliper is a declared design choice, not a universal guarantee of balance.'),
      (formula('sₚ = √[(s₁²+s₀²)/2], measured before matching\nSMDafter = (X̄treated, retained − X̄control, weighted)/sₚ\nUrban: (11/19 − 16/19)/sₚ = −0.52007'),
       'The matched control mean repeats a control once for every adopter it represents. The original pooled within-group standard deviation uses sample variances with divisor n_group−1 and stays fixed before and after matching. This scale differs from the full-cohort population standard deviation used by the nearest-neighbor distance. Mean balance is one diagnostic; distributions, interactions and extreme matches also merit inspection.'),
      (bullets('Repeated controls create dependence among pair differences','A standard error must match the estimator and its design','A mean-balance check does not measure hidden confounding','Freeze the design before interpreting outcomes'),
       'The lab intentionally reports matching point estimates without applying an independent-pairs formula. Nearest-neighbor estimators also require care when choosing a resampling method; ordinary resampling is not automatically valid for every fixed-neighbor design. A full inferential extension should select an estimator-specific variance procedure, account for control reuse and state whether the retained target is fixed. The main lesson’s HC1 interval applies to regression standardization only.')
    ]
    # The coefficient table and its interaction formula use consecutive slides.
    refs='<p>Further reading: <a href="https://www.stat.cmu.edu/~ryantibs/journalclub/rosenbaum_1983.pdf">Rosenbaum and Rubin: the propensity score</a>; <a href="https://www.statsmodels.org/stable/examples/notebooks/generated/formulas.html">Model formulas and interaction terms</a>; <a href="https://www.nber.org/papers/t0325">Abadie and Imbens: bootstrap limitations for fixed-neighbor matching</a>; <a href="lesson-8.html">Graph-based control selection</a>.</p>'
    c['appendix_extra']='<section id="matching-worked"><h2>Reconstruct the comparison and its diagnostics</h2>'+''.join(block(t,vis,note) for t,(vis,note) in zip(DETAIL_TITLES,details))+refs+'</section>'
    return c
