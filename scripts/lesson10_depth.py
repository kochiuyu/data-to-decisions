"""Follow the DiD identification argument through one balanced rollout panel."""
from functools import lru_cache

CALCULATIONS = '''# Build one before and one after outcome for each rollout store.
l10_w = world()
l10_rows = l10_w['panel'].query("cohort=='Rollout' and 17<=week<=32").copy()
assert len(l10_rows)==800 and not l10_rows.duplicated(['store_id','week']).any()
assert l10_rows.groupby('store_id').offer.nunique().eq(1).all()
l10_rows['after'] = (l10_rows.week>=25).astype(int)
assert (l10_rows.active==l10_rows.offer*l10_rows.after).all()
assert l10_rows.groupby(['store_id','after']).size().eq(8).all()
l10_periods = l10_rows.groupby(['store_id','offer','after']).stockout_rate.mean().reset_index()
assert len(l10_periods)==100 and not l10_periods.duplicated(['store_id','after']).any()
l10_v = l10_periods.pivot(index=['store_id','offer'],columns='after',values='stockout_rate')
l10_v = l10_v.rename(columns={0:'pre',1:'post'}).reset_index().sort_values('store_id')
assert len(l10_v)==50 and not l10_v.isna().any().any()
l10_v['change'] = l10_v['post']-l10_v['pre']
l10_v = l10_v.merge(l10_w['stores'][['store_id','lead_days','urban','baseline_rate']],on='store_id',validate='one_to_one')
l10_a = l10_v[l10_v.offer==1]; l10_c = l10_v[l10_v.offer==0]
assert len(l10_a)==len(l10_c)==25
l10_effect = difference(l10_c.change,l10_a.change)
l10_counterfactual = l10_a.pre.mean()+l10_c.change.mean()
l10_saved = lesson_result(10)
# The saturated interaction model reconstructs all four means.
l10_X = np.column_stack([np.ones(100),l10_periods.offer,l10_periods.after,l10_periods.offer*l10_periods.after])
l10_beta = np.linalg.lstsq(l10_X,l10_periods.stockout_rate,rcond=None)[0]
l10_F = np.column_stack([np.ones(50),l10_v.offer])
l10_fd,l10_Vfd,_ = fit_ols(l10_F,l10_v.change)
l10_cells = np.array([[1,0,0,0],[1,1,0,0],[1,0,1,0],[1,1,1,1]])
l10_predictions = l10_cells@l10_beta
assert np.allclose(l10_predictions,[l10_c.pre.mean(),l10_a.pre.mean(),l10_c.post.mean(),l10_a.post.mean()])
assert np.isclose(-l10_beta[3],l10_effect['value']) and np.isclose(-l10_fd[1],l10_effect['value'])
assert np.isclose(l10_effect['value'],l10_saved['effect']['value'])
# Independent store changes supply Welch uncertainty.
l10_variances = [l10_c.change.var(ddof=1),l10_a.change.var(ddof=1)]
l10_parts = np.array(l10_variances)/25
l10_se = np.sqrt(l10_parts.sum())
l10_df = l10_parts.sum()**2/np.sum(l10_parts**2/24)
l10_critical = t.ppf(.975,l10_df)
l10_ci = l10_effect['value']+np.array([-1,1])*l10_critical*l10_se
assert np.allclose(l10_ci,[l10_saved['effect']['low'],l10_saved['effect']['high']])
# Cluster the two period rows of each store; retain the finite-sample correction.
l10_resid = l10_periods.stockout_rate.to_numpy()-l10_X@l10_beta
l10_bread = np.linalg.inv(l10_X.T@l10_X); l10_meat = np.zeros((4,4))
for _,l10_g in l10_periods.groupby('store_id'):
    l10_idx = l10_g.index; l10_score = l10_X[l10_idx].T@l10_resid[l10_idx]
    l10_meat += np.outer(l10_score,l10_score)
l10_cluster = (50/49)*(99/96)*l10_bread@l10_meat@l10_bread
l10_C = np.column_stack([np.ones(50),l10_v.offer,l10_v.lead_days,l10_v.urban,l10_v.baseline_rate])
l10_controlled,l10_Vc,_ = fit_ols(l10_C,l10_v.change)
assert np.isclose(-l10_controlled[1],l10_saved['depth']['controlled']['value'])
# Fixed baseline priority weights define a new weighted comparison.
l10_weights = np.where(l10_v.lead_days>=4,2.,1.)
l10_group_weights = [float(l10_weights[l10_v.offer==j].sum()) for j in [0,1]]
l10_weighted_changes = [float(np.average(l10_v.loc[l10_v.offer==j,'change'],weights=l10_weights[l10_v.offer==j])) for j in [0,1]]
l10_weighted_sums = [a*b for a,b in zip(l10_group_weights,l10_weighted_changes)]
l10_wls = np.linalg.lstsq(l10_F*np.sqrt(l10_weights[:,None]),l10_v.change*np.sqrt(l10_weights),rcond=None)[0]
assert np.isclose(-l10_wls[1],l10_weighted_changes[0]-l10_weighted_changes[1])
assert np.isclose(-l10_wls[1],l10_saved['depth']['priority_weighted'])
# A pre-period placebo compares weeks 17-20 with weeks 21-24.
l10_early = l10_rows[l10_rows.week<=24].assign(later=lambda x:(x.week>=21).astype(int))
l10_early = l10_early.groupby(['store_id','offer','later']).stockout_rate.mean().unstack('later').reset_index()
l10_early['change'] = l10_early[1]-l10_early[0]
l10_placebo = difference(l10_early[l10_early.offer==0].change,l10_early[l10_early.offer==1].change)
assert np.isclose(l10_placebo['value'],l10_saved['depth']['placebo']['value'])
l10_subgroups = []
for l10_u,l10_g in l10_v.groupby('urban'):
    l10_est = difference(l10_g[l10_g.offer==0].change,l10_g[l10_g.offer==1].change)
    l10_subgroups.append(dict(urban=int(l10_u),**l10_est))
l10_threshold = 20/(140*.01*6)
l10_shock = l10_effect['value']-l10_threshold
l10_saving = 8.4*l10_effect['value']-20
assert np.isclose(l10_saving,l10_saved['savings']['value'])
# Log extension uses the same positive store-period outcomes and equal weights.
assert (l10_v[['pre','post']]>0).all().all()
l10_log_change = np.log(l10_v['post'])-np.log(l10_v['pre'])
l10_log_beta = np.linalg.lstsq(l10_F,l10_log_change,rcond=None)[0]
l10_log_ratio = np.exp(l10_log_beta[1])
l10_geometric_ratios = [float(np.exp(l10_log_change[l10_v.offer==j].mean())) for j in [0,1]]
assert np.isclose(l10_log_ratio,l10_geometric_ratios[1]/l10_geometric_ratios[0])
assert np.isclose(100*np.expm1(-.179),-16.38941006029645)
'''

CODE_TITLES = [
 'Validate eight weeks per store before forming the two period averages',
 'Create complete store changes and calculate the adopter comparison',
 'Recover the four means with interaction and first-difference regressions',
 'Calculate Welch uncertainty from variation across independent store changes',
 'Cluster repeated period rows and fit the baseline-adjusted change model',
 'Reconstruct weighted changes and prepare the pre-period placebo',
 'Check the placebo and connect subgroup effects to the spending rule',
 'Convert the same positive store outcomes into a log-change comparison',
]
DETAIL_TITLES = [
 'No anticipation lets observed baseline outcomes enter the identification argument',
 'A complete panel preserves the same units across the two dates',
 'The two fitted equations recover identical point contrasts on this sample',
 'Welch uncertainty uses two variances and their store counts',
 'Store clustering preserves dependence between the two period residuals',
 'Baseline adjustment permits changes to depend on starting conditions',
 'Priority weights change the target rather than measuring error precision',
 'A log contrast compares proportional changes in geometric means',
 'The same positive retail outcomes support a separate log-scale comparison',
 'A fixed dose and a changing dose define different comparisons',
 'An unrelated favorable shock reduces the effect attributed to alerts',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    scope=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson10-worked-calculations','exec'),scope)
    return scope

def counterfactual_figure(r):
    sy=lambda y:265-25*(y-8)
    a,b,c,e=(r[k] for k in ['adopter_pre','adopter_post','comparison_pre','comparison_post'])
    cf=r['counterfactual'];gap=r['effect']['value']
    return f'''<figure><svg viewBox="0 0 760 350" role="img" aria-label="The no-alert benchmark is 14.97 percent, above the observed 10.39 percent"><title>The missing no-alert path supplies the DiD comparison</title><desc>Period means for weeks 17–24 and 25–32. Adopters move from {a:.2f} to {b:.2f}; comparison stores from {c:.2f} to {e:.2f}. The dashed adopter benchmark ends at {cf:.2f}. Its gap from the observed adopter mean is {gap:.2f} percentage points.</desc>
<line x1="95" y1="280" x2="545" y2="280" stroke="#536576"/><line x1="95" y1="55" x2="95" y2="280" stroke="#536576"/>
<text x="95" y="28" font-size="17">Stockout rate (%)</text><line x1="325" y1="50" x2="325" y2="280" stroke="#aab6b0" stroke-dasharray="3 5"/><text x="325" y="47" text-anchor="middle" font-size="15">Week 25 rollout</text>
<path d="M120 {sy(c):.1f} L515 {sy(e):.1f}" stroke="#3259a2" stroke-width="3" fill="none"/>
<path d="M120 {sy(a):.1f} L515 {sy(b):.1f}" stroke="#276451" stroke-width="4" fill="none"/>
<path d="M120 {sy(a):.1f} L515 {sy(cf):.1f}" stroke="#9b421e" stroke-width="3" stroke-dasharray="8 5" fill="none"/>
<path d="M530 {sy(cf):.1f} h12 M536 {sy(cf):.1f} V{sy(b):.1f} M530 {sy(b):.1f} h12" stroke="#9b421e" stroke-width="2" fill="none"/>
<text x="112" y="{sy(a)-10:.1f}" text-anchor="end" font-size="16">{a:.2f}</text><text x="112" y="{sy(c)-10:.1f}" text-anchor="end" font-size="16">{c:.2f}</text>
<text x="550" y="{sy(cf)+4:.1f}" font-size="16">{cf:.2f} without alerts</text><text x="550" y="{sy(b)+5:.1f}" font-size="16">{b:.2f} observed</text><text x="370" y="{sy(e)-12:.1f}" font-size="16">Comparisons: {e:.2f}</text>
<text x="555" y="{(sy(cf)+sy(b))/2:.1f}" font-size="17" fill="#9b421e">{gap:.2f}-point gap</text>
<text x="120" y="305" text-anchor="middle" font-size="16">Before</text><text x="515" y="305" text-anchor="middle" font-size="16">After</text><text x="120" y="328" text-anchor="middle" font-size="14">Weeks 17–24</text><text x="515" y="328" text-anchor="middle" font-size="14">Weeks 25–32</text>
</svg><figcaption>Green: observed adopters. Blue: observed comparisons. Dashed brown: the adopters’ no-alert benchmark under parallel trends. Lines connect period means.</figcaption></figure>'''

def restore(c):
    from retail_ui import table,formula,p,chart
    from retail_content import section
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();r=d['l10_saved'];v=d['l10_v'];depth=r['depth'];f=lambda x:f'{x:.2f}'
    c['authored_sections']=True;c['sections']=[]
    c['headlines']={k:val for k,val in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    def block(title,visual,*notes):
        return teach(title,visual.replace('\n','<br>') if 'class="calculation"' in visual else visual,list(notes))
    def put(key,title,body,phase='General theory'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    c['brief']='The chain introduces alerts at 25 of its 50 remaining stores in week 25. These stores began with higher stockout rates. How much of their later improvement came from alerts, beyond the movement already occurring elsewhere? Learn how comparing changes constructs the missing no-alert path, then trace the result from weekly records to the final expansion decision.'
    c['scope']=['Explain what the two differences remove','Reconstruct the panel, regression and weighted comparison','Connect the treated-store effect to the expansion decision']
    c['motivation']=['Later adopters begin with higher stockout rates','Separate the rollout improvement from background movement','Decide whether comparable stores justify continued expansion']
    put('did-theory','Separate persistent differences from changes over time',
      block('A before-and-after improvement includes both treatment and background movement',bullets('D=1: units treated after the intervention date','D=0: comparison units remaining untreated','Before and after use the same outcome definition','A panel follows the same units in both periods'),
        'A policy can begin while demand, seasonality or operations are already changing. Comparing a treated group with its own past removes persistent differences across units, but still includes these time changes. A comparison group supplies a candidate estimate of the background movement. This lesson uses a balanced panel with one common intervention date; define the groups and windows before computing an effect.')+
      block('Two subtractions remove the group level and the common time change',table(['Group mean','Before','After','Change'],[['Comparison','a','a+c','c'],['Treated','a+b','a+b+c+τ','c+τ'],['Treated − comparison','b','b+τ','τ']], 'Additive mean model: b is a persistent level gap; c is a shared change'),
        'Read the last column first: differencing within each group removes its starting level. Then subtract the comparison change from the treated change, leaving τ. Reading across the last row gives the same result. This table expresses a population mean model with a common untreated change; observed sample means also contain sampling variation. It does not claim that every unit’s residual cancels exactly.')+
      block('The conventional DiD is the treated change minus the comparison change',formula('DiD = (Ȳ₁,after − Ȳ₁,before) − (Ȳ₀,after − Ȳ₀,before)'),
        'The subscripts 1 and 0 label treatment groups, not time. A negative DiD means the outcome fell more, or rose less, in the treated group. Whether that is favorable depends on the outcome: fewer stockouts are desirable. Keep the conventional signed outcome effect in the theory and explicitly reverse its sign when reporting a positive reduction in the application.'))
    put('identify-att','Identify the missing untreated change for the treated population',
      block('Potential outcomes reveal the comparison that the data cannot show',formula('ATT = E[Yafter(1) − Yafter(0) | D=1]\nMissing quantity: E[Yafter(0) | D=1]'),
        'ATT is the average treatment effect on the treated group. Yafter(1) and Yafter(0) describe the same unit with and without treatment after the intervention. We observe only the option received. No anticipation lets the baseline outcome represent the untreated state for future adopters; consistency links received treatment to the observed outcome, and the comparison group must remain untreated by this intervention, including spillovers.')+
      block('The observed difference in changes equals ATT plus untreated-trend bias',formula('DiD = ATT + δ\nδ = E[ΔY(0) | D=1] − E[ΔY(0) | D=0]'),
        'Start with the treated group’s observed change, E[Yafter(1)−Ybefore(0)|D=1]. Add and subtract its missing Yafter(0). The expression becomes its treatment effect plus its untreated change. Subtracting the comparison group’s untreated change leaves ATT plus δ. The appendix writes every step. The extra term shows precisely what remains when the untreated trends differ.')+
      block('Parallel trends sets the remaining bias term to zero',formula('E[ΔY(0) | D=1] = E[ΔY(0) | D=0]\nTherefore δ=0 and DiD identifies ATT'),
        'Parallel trends concerns average changes without treatment, not equal starting levels or identical observed paths after treatment. A persistent level gap is compatible with this condition. The operating history and pre-period evidence help assess the comparison; they do not make the missing after-period path observable. Selected adopters can have different treatment effects from other stores, so an ATT does not automatically become an all-store ATE.'))
    put('regression-theory','Express the same contrast through two fitted equations',
      block('The group-by-period interaction recovers the four-cell contrast',formula('Yᵢₜ = a + bDᵢ + cAfterₜ + d(Dᵢ×Afterₜ) + eᵢₜ'),
        'The intercept is the comparison mean before treatment. b is the initial group gap; c is the comparison change; d is the additional treated change. The four combinations of D and After give four fitted means. On the same observations and weights, this saturated two-by-two model reproduces the difference of changes exactly. Identification still comes from the trend argument, not from fitting an interaction.')+
      block('First differences remove a unit’s persistent level and leave one change',formula('ΔYᵢ = α + βDᵢ + uᵢ\nα = comparison change; β = signed DiD'),
        'With two periods and complete paired observations, subtract before from after within each unit. A time-invariant unit component disappears. Regressing those changes on an intercept and D estimates the difference between the two group mean changes. Under the common balanced design, the first-difference and interaction coefficients agree. Preserve the unit in the uncertainty calculation rather than treating repeated rows as independent assignments.')+
      block('Controls and weights answer specified questions about changes and populations',bullets('Baseline controls allow changes to vary with starting conditions','Subgroups restrict the population being compared','Fixed baseline weights change which units count most','Keep sample, target and specification beside every estimate'),
        'Adjustment is useful when untreated changes differ systematically with measured starting conditions and a conditional trend argument is credible. Choose controls by timing and causal role, using Lesson 8’s logic; being measured early does not make every variable a suitable control. Priority or exposure weights define a target average. Inverse-variance weights instead address error precision under an explicit error model.'))
    app='Worked application'
    put('read-data','Build one complete change for each rollout store',
      block('Eight hundred weekly records become fifty complete store changes',table(['Step','Rows / units','Definition'],[['Keep S101–S150, weeks 17–32','800 weekly rows','50 stores × 16 weeks'],['Average within store and period','100 period rows','8 weeks before; 8 after'],['Pair by store ID and subtract','50 changes','After − before'],['Split by future adoption','25 + 25 stores','Fixed group membership']], 'No store is excluded from this balanced rollout panel'),
        'The before window is weeks 17–24; the after window is weeks 25–32. Every week has 140 monitored product-days, so averaging weekly percentages gives the same rate as pooling the counts within a store-period. Equal windows also keep each store equally weighted. The lab checks a unique store-week key, eight weeks per window, complete pairs and one-to-one joins to baseline attributes.')+
      block('Group membership exists before treatment becomes active',table(['Store group / period','D','After','D×After'],[['Comparison, before',0,0,0],['Adopter, before',1,0,0],['Comparison, after',0,1,0],['Adopter, after',1,1,1]], 'D is the offer field; active equals D×After in this window'),
        'A future adopter has D=1 in both periods. Coding D as zero before rollout would confuse group membership with active treatment and remove the initial group-gap term from the intended model. The cohort’s offer flag is constant within store. The active field switches on in week 25 for adopters and remains zero for comparisons.')+
      block('Each store’s two averages produce the change used by the analysis',table(['Store','D','Before %','After %','Change'],[[x.store_id,int(x.offer),f(x.pre),f(x.post),f(x.change)] for x in v.head(5).itertuples()], 'First five paired stores; changes are percentage points'),
        'For S101, 10.178571−13.035714=−2.857143 points. S103 is a comparison store and also improves, illustrating why an individual before-after change cannot isolate the policy effect. The group analysis uses all fifty changes. A missing period would prevent that unit from supplying a paired change and would require an explicit eligibility decision.'),app)
    series=r['weekly'];weekly=chart([x['week'] for x in series],{'Later adopters':[x['adopters'] for x in series],'Comparison stores':[x['usual'] for x in series]},'Observed stockout paths before and after the rollout')
    weekly_figure=weekly.split('<div class="table-scroll"',1)[0].replace('exact values follow in the table.','exact weekly values are in the technical appendix.')
    marker=70+600*(25-1)/31
    weekly_figure=weekly_figure.replace('</svg>',f'<line x1="{marker:.1f}" x2="{marker:.1f}" y1="30" y2="250" stroke="#536576" stroke-dasharray="3 4"/><text x="{marker-7:.1f}" y="24" text-anchor="end" font-size="14">Week 25 rollout</text></svg>')
    put('observed-paths','Locate the intervention in the observed history',block('The rollout begins at week twenty-five after distinct starting levels',weekly_figure,
        'The selected adopters began with higher baseline stockout rates. The chart supplies context for the dated comparison and shows that the groups need not have the same level. The main estimate averages weeks 17–24 and 25–32; the earlier weeks help describe the history. Inspect other changes at the rollout date with the operations team. The complete thirty-two-week table is available in the appendix.'),app)
    put('calculate','Construct the missing no-alert benchmark from four means',
      block('Comparison stores worsen while adopter stores improve',table(['Group','Before %','After %','Change'],[['Adopters',f(r['adopter_pre']),f(r['adopter_post']),f(r['adopter_change'])],['Comparisons',f(r['comparison_pre']),f(r['comparison_post']),f(r['comparison_change'])]], 'Mean of twenty-five store outcomes per group and period'),
        'The adopter change is −3.346429 points and the comparison change is +1.239286. The latter supplies the estimated background movement. Each cell uses the same stores with the same equal weights, so the change in group means equals the mean of within-store changes. This sample consistency is what lets the table and the regressions agree.')+
      block('Subtracting the background change gives a 4.59-point stockout reduction',formula('Signed DiD = −3.346429 − 1.239286 = −4.585714\nReported reduction = −DiD = 4.585714 points\nNo-alert benchmark = 13.732143 + 1.239286 = 14.971429%'),
        'A smaller stockout outcome is favorable, so the business result reports the negative of the conventional DiD. Under parallel trends, adopters would have moved from 13.73% to 14.97% without alerts. Their observed after mean is 10.39%. The estimated improvement attributable to the policy comparison is therefore larger than the adopter group’s raw 3.35-point improvement.')+
      block('The dashed no-alert path makes the missing comparison visible',counterfactual_figure(r),
        'The dashed line is an inferred counterfactual, not an observed third group. It starts at the adopters’ own before mean and adds the comparison change. The vertical difference at the after period is the positive reduction. The lines connect period averages and should not be read as weekly trajectories. Their role is to make the identification argument and the subtraction concrete.'),app)
    put('did-regression','Recover the same result through regression',
      block('Four fitted coefficients reconstruct the entire before-and-after table',table(['Coefficient','Value','Meaning'],[['a',f'{d["l10_beta"][0]:.6f}','Comparison before mean'],['b',f'{d["l10_beta"][1]:.6f}','Initial adopter gap'],['c',f'{d["l10_beta"][2]:.6f}','Comparison change'],['d',f'{d["l10_beta"][3]:.6f}','Additional adopter change']], 'Y = a + bD + cAfter + d(D×After)'),
        'These coefficients come from the one hundred store-period rows. For example, b=13.732143−10.357143=3.375. The intervention coefficient d is negative because the outcome is a stockout percentage. Its negative is the reported positive reduction. Retain all four terms when reconstructing the group-period predictions.')+
      block('Substituting each indicator combination recovers its observed cell mean',table(['Cell','Fitted sum','Predicted %'],[['Comparison before','a','10.357143'],['Adopter before','a+b','13.732143'],['Comparison after','a+c','11.596429'],['Adopter after','a+b+c+d','10.385714']], 'The saturated regression reproduces all four equally weighted means'),
        'The adopter-after cell needs every term: 10.357143 + 3.375 + 1.239286 − 4.585714 = 10.385714. These fitted cell means are exactly the sample group-period averages apart from rounding. This is an algebraic property of the saturated model. It does not establish the causal interpretation, which still depends on the untreated-trend comparison.')+
      block('Regressing fifty store changes produces the same signed effect',formula('ΔŶ = 1.239286 − 4.585714D\nD=0: +1.239286; D=1: −3.346429'),
        'The fifty-row change model and the one-hundred-row interaction model agree on the point estimate because they use the same balanced stores and weights. The former makes the independent unit visible. It also gives a natural place to add baseline characteristics when modeling differences in changes. Their uncertainty calculations must account for the respective row structure.'),app)
    put('interpret','Use stores as the units of uncertainty',block('Variation across fifty store changes gives the 3.92–5.25 interval',formula(f'SE = √(s²comparison/25 + s²adopter/25) = {d["l10_se"]:.5f}\n95% interval = 4.58571 ± {d["l10_critical"]:.4f} × 0.33178\n= [3.91830, 5.25313] percentage points'),
        'Each group variance describes twenty-five independent store changes. Welch’s degrees of freedom are 47.107, giving the displayed t multiplier. Aggregating within store keeps the repeated weeks together. One hundred period rows do not mean one hundred independent stores. In a period-row regression, clustering by store preserves dependence; its finite-sample correction can produce a slightly different standard error. The appendix calculates both.'),app)
    put('diagnostics','Check the comparison and show the adjusted result',
      block('A pre-period placebo compares two windows before alerts began',formula('Early window: weeks 17–20; later window: weeks 21–24\nPlacebo reduction: −0.13571 points\n95% interval: [−1.39189, 1.12047]'),
        'Repeat the same comparison of changes before any rollout treatment is active. The estimated divergence is small relative to its uncertainty. This is useful evidence about the chosen comparison, but the interval also allows nontrivial pre-period differences. Combine the diagnostic with knowledge of simultaneous changes; a test that does not reject is not a certificate for the unobserved post-period trend.')+
      block('Baseline adjustment asks whether starting conditions explain different changes',formula('ΔY = α + βD + γL + ηU + κB + u\nAdjusted reduction −β = 4.00 points\n95% HC1 normal interval: [2.66, 5.34]'),
        'L is delivery lead time, U is urban location and B is baseline stockout percentage measured in weeks 1–8. The model uses the same fifty store changes. Its constant β describes an additive adjusted group contrast; interpreting it causally requires a suitable conditional trend argument, overlap and specification. Do not choose between the adjusted 4.00 and unadjusted 4.59 merely because one is more attractive. The appendix shows the complete fitted coefficients.')+
      block('Subgroup effects remain attached to their smaller comparison samples',table(['Location','Adopters','Comparisons','Reduction','95% interval'],[['Urban' if x['urban'] else 'Other',x['adopters'],x['comparison'],f(x['value']),f'{x["low"]:.2f}–{x["high"]:.2f}'] for x in depth['subgroups']], 'Separate equal-store comparisons; percentage points'),
        'Urban stores have a somewhat larger estimated reduction, but only six urban comparison stores supply their background change. Compare both sample sizes and uncertainty. The two group estimates answer narrower population questions. A difference between their individual significance labels would not test whether the subgroup effects differ.'),app)
    put('weighted-comparison','Make the weighting target visible before fitting weighted least squares',
      block('Doubling long-lead stores creates an explicit planning-weighted comparison',table(['Group','Sum of weights','Sum of weighted changes','Weighted change'],[[name,f'{w:.0f}',f'{total:.5f}',f'{mean:.5f}'] for name,w,total,mean in zip(['Comparison','Adopter'],d['l10_group_weights'],d['l10_weighted_sums'],d['l10_weighted_changes'])], 'Weight 2 if baseline lead time is at least four days; otherwise weight 1'),
        'Use each store’s fixed baseline weight in both periods. Divide the weighted sum of changes by the group’s weight total, not by its number of stores. The totals are 34 for comparisons and 48 for adopters. These priorities deliberately change how stores contribute. They are not measured sales counts or inverse estimates of error variance.')+
      block('Weighted least squares reproduces the weighted difference in changes',formula('Weighted mean change = ΣwᵢΔYᵢ / Σwᵢ\nWeighted reduction = 1.234244 − (−3.351935)\n= 4.586178 percentage points'),
        'Weighted least squares on an intercept and D gives the two weighted group means, so its treatment coefficient is their signed difference. The near equality to the unweighted 4.585714 is a result of these data and this priority rule, not a general identity. To interpret the new comparison causally, defend the untreated trend for the weighted target. Equal monitoring exposure explains why equal-store and exposure weighting coincide in the original analysis.'),app)
    put('sensitivity','Translate differential-trend bias into the spending decision',
      block('An unrelated favorable adopter shock would inflate the reported reduction',formula('Let s = a separate favorable adopter change in points\nReduction attributable to alerts = 4.585714 − s\nAccounting saving = 8.4 × (4.585714 − s) − 20'),
        'This is a hypothetical sensitivity scenario. A separate favorable change makes the signed untreated-trend bias δ negative and the reported positive reduction too large. For example, s=1 point reduces the policy contrast to 3.585714 and the weekly saving to 10.12 currency units. An operational response caused by alerts belongs within their total effect; a genuinely unrelated simultaneous change is the concern in this exercise.')+
      block('A 2.20-point unrelated improvement would erase the estimated accounting advantage',formula('Break-even reduction = 20 / (140×0.01×6) = 2.380952\nPoint-estimate break-even shock = 4.585714 − 2.380952\n= 2.204762 points'),
        'A one-point stockout reduction avoids 1.4 stockout product-days per week; valued at 6 currency units each, it saves 8.4 before the 20-unit alert fee. The sensitivity threshold links the trend assumption to the decision. It is not an estimated shock, a confidence bound or a claim that such a shock occurred. It tells the director how large a competing explanation would need to be to remove the point estimate’s accounting gain.'),app)
    put('act','Complete the expansion recommendation with traceable evidence',block('The rollout supports staged expansion for comparable stores with continued measurement',bullets('Later-adopter reduction: 4.59 points; interval 3.92–5.25','Accounting saving: 18.52 CU per adopter-week','Preserve dates, store IDs and the monitoring basket','Review simultaneous changes and the next target population'),
        'The saving interval is 12.91–24.13 currency units per adopter-week under the stated accounting rule. Continue staged expansion for stores resembling this cohort, documenting the next decision population. The final memo should bring together the earlier burden, forecasting work, randomized pilot, voluntary comparison and this rollout study. Each estimate has its own population and time window; the synthesis page assembles them without treating them as interchangeable measurements.'),app)
    next(s for s in c['sections'] if s['id']=='calculate')['body']+='<p><a href="lesson-10-appendix.html#calculation">Follow this calculation further →</a></p>'
    c['memo']='The later rollout estimates a 4.59-point reduction for the selected adopters, with a 95% interval of 3.92–5.25 and an accounting saving of 18.52 CU per adopter-week. Continue staged expansion for comparable stores while recording timing and simultaneous changes. An unrelated favorable adopter shock of 2.20 points would erase the point estimate’s accounting advantage.'
    c['question']='Suppose a separate process change improved only adopter stores by one percentage point at rollout. What happens to the estimated alert reduction and accounting saving?'
    c['answer']='Subtract that hypothetical one-point improvement: the alert reduction becomes 3.585714 points. Weekly accounting saving becomes 8.4×3.585714−20=10.12 CU. Distinguish a separate simultaneous cause from a mechanism that is itself caused by alerts.'
    c['presentation_points']={'memo':['Later adopters: 4.59-point reduction; 18.52 CU weekly saving','Continue staged expansion for comparable stores','Record simultaneous changes and the next target population'],'question':['A separate process change improves adopters by one point','Recalculate the alert reduction and weekly saving'],'answer':['Adjusted reduction: 4.585714−1=3.585714 points','Accounting saving: 8.4×3.585714−20=10.12 CU','Separate unrelated causes from mechanisms of the alert policy']}
    c['headlines']['memo']=['The memo connects the rollout contrast to a population and spending rule','How would a separate one-point improvement change the rollout recommendation?']
    c['headlines']['decision-brief']=['The rollout question requires separating policy effects from background movement']
    c['bigger']='Difference-in-differences turns an operating history into an explicit missing comparison. The two subtractions remove persistent levels and a shared change; the untreated-trend argument gives the remaining contrast its causal meaning. Across business settings, keep the population, dates, unit and target weights visible from the raw records to the decision.'
    c['transfer_points']=['Two differences isolate a contrast in changes','The untreated-trend argument determines its causal meaning','Units, dates and target weights carry through to the decision']
    c['code']=CALCULATIONS
    c['technical']=['Keep the fifty rollout stores, S101–S150, during weeks 17–32. Check a unique store-week key and eight weeks per store in each window. The 800 weekly observations become 100 store-period means and fifty complete changes. D is fixed future-adopter membership, while active=D×After. All outcomes have the same 140-product-day weekly exposure.',
      'Trace the complete sample, four means, interaction regression, first-difference fit, Welch interval, store-cluster covariance, baseline adjustment, fixed-weight comparison and pre-period placebo. The optional log calculation uses these same positive store-period outcomes. Intermediate variables beginning l10_ remain available for inspection; assertions verify the existing published results.',
      'The main interval uses Welch uncertainty across twenty-five independent changes in each group. The adjusted regression uses HC1 covariance and a normal multiplier. The period-row comparison clusters by store with a specified CR1 finite-sample correction. Identical point estimates need not have identical intervals when covariance conventions differ.',
      'Work the unrelated-shock scenario: subtract s from the positive reduction and calculate 8.4×(4.585714−s)−20. At s=1, the saving is 10.12 CU. The point-estimate break-even value is s=2.204762. Treat s as a declared sensitivity scenario; it is not an observed operational shock or a confidence limit.']
    details=[
      (formula('DiD = E[Yafter(1)−Ybefore(0)|D=1] − E[ΔY(0)|D=0]\nAdd and subtract E[Yafter(0)|D=1]\n= E[Yafter(1)−Yafter(0)|D=1] + E[ΔY(0)|D=1] − E[ΔY(0)|D=0]\n= ATT + δ'),
       'No anticipation and consistency justify the first observed-to-potential-outcome substitution, while an untreated comparison supplies its observed untreated change. Parallel trends removes δ. This is an ATT for the selected treated population and after window. Selection on persistent outcome levels need not violate parallel trends; selection on future untreated changes can. Generalizing to all stores requires additional population and effect assumptions.'),
      (bullets('Assert unique store-week and store-period keys','Verify both period averages before subtracting','Use one-to-one baseline joins and fixed group labels','Sort dates before any alternative grouped diff operation'),
       'The lab pivots on an explicit before/after indicator, avoiding dependence on input order. A grouped diff implementation should first sort by store and time and verify the two dates. A count of two rows alone does not prove one observation at each date when duplicate keys are possible. If logs are used, form the positive complete-pair sample first and use exactly that sample in both descriptive tables and regression.'),
      (formula('Ŷ = 10.357143 + 3.375D + 1.239286After − 4.585714D×After\nΔŶ = 1.239286 − 4.585714D'),
       'The first equation uses 100 store-period rows; the second uses 50 changes. With equal weights and two complete periods per unit, the coefficient identities follow from the four cell means. If a descriptive table drops a different set of nonpositive or missing observations, or uses different weights, it no longer supplies an exact check of the regression.'),
      (formula(f's²comparison = {d["l10_variances"][0]:.6f}; s²adopter = {d["l10_variances"][1]:.6f}\nSE² = s²comparison/25 + s²adopter/25\nν = (v₀+v₁)² / (v₀²/24+v₁²/24) = {d["l10_df"]:.6f}\nwhere vⱼ=s²ⱼ/25; t₀.₉₇₅,ν = {d["l10_critical"]:.6f}'),
       'These are sample variances of store changes, using divisor 24 within each group. The interval is estimate plus or minus the t multiplier times SE. There are fifty independent store units under this sampling model. Additional weekly observations can improve each store-period measurement, but do not create independent policy assignments.'),
      (formula('Cluster score sᵢ = Xᵢ′eᵢ for each store’s two rows\nV = (X′X)⁻¹(Σᵢsᵢsᵢ′)(X′X)⁻¹ × (50/49)×(99/96)\nCluster CR1 SE(d) = 0.333468\nFirst-difference HC1 SE(β) = 0.331779'),
       'The CR1 factor uses G/(G−1) times (N−1)/(N−K), with 50 stores, 100 rows and four coefficients. The first-difference HC1 model uses 50/(50−2). Finite-sample conventions explain this small difference even though the point contrast agrees. The lesson’s reported interval remains the explicitly calculated Welch interval; a regression package’s default interval may use a different covariance and reference distribution.'),
      (table(['Term in change regression','Coefficient'],[[name,f'{value:.6f}'] for name,value in zip(['Intercept','D','Delivery days L','Urban U','Baseline rate B'],d['l10_controlled'])], 'Same fifty changes; HC1 covariance'),
       'The adjusted treatment coefficient is −3.997935. The HC1 normal interval for its negative is [2.657488,5.338382]. Baseline rate comes from weeks 1–8, before either evaluation window. This additive model allows changes associated with the recorded starting variables and imposes a constant adjusted D contrast. A conditional parallel-trends argument and a suitable model are needed for its causal interpretation.'),
      (formula('wᵢ = 2 if baseline delivery lead time ≥4; otherwise 1\nΔ̄ⱼ,w = ΣDᵢ=j wᵢΔYᵢ / ΣDᵢ=j wᵢ\nWLS minimizes Σᵢwᵢ(ΔYᵢ−α−βDᵢ)²'),
       'With an intercept and a binary D, the normal equations set the two fitted values equal to the group weighted means. The signed coefficient is their treated-minus-comparison difference. Priority weights, exposure weights and inverse-variance weights have different motivations. Fix baseline target weights before the intervention; post-treatment weights can change with treatment and alter the comparison. This example reports a weighted point contrast rather than borrowing the unweighted interval.'),
      (formula('βlog = Δmean(log Y|D=1) − Δmean(log Y|D=0)\nexp(βlog) = (GM₁,after/GM₁,before) / (GM₀,after/GM₀,before)\nExact proportional contrast = 100[exp(βlog)−1]\nIllustration: βlog=−0.179 gives −16.39%, approximately −17.9%'),
       'GM is the geometric mean, obtained by exponentiating the mean log. The approximate conversion 100β is accurate only for sufficiently small magnitudes; label it as an approximation. These quantities are not automatically ratios of arithmetic means. A causal interpretation on the log scale requires an appropriate parallel-trends argument for untreated log outcomes, which is not implied by parallel trends in levels. The −0.179 value is an illustrative conversion of the original deck’s displayed coefficient, not the retail estimate.'),
      (formula(f'Use log(after store mean) − log(before store mean)\nComparison geometric ratio: {d["l10_geometric_ratios"][0]:.6f}\nAdopter geometric ratio: {d["l10_geometric_ratios"][1]:.6f}\nRatio of ratios = {d["l10_log_ratio"]:.6f}; proportional contrast = {100*(d["l10_log_ratio"]-1):.2f}%'),
       'Every store-period mean in this release is positive, so the optional log calculation retains all fifty stores. Log of a period average differs from the average of weekly logs; the displayed recipe specifies the former. This is a different outcome scale and a descriptive comparison under a different specification. The main accounting decision continues to use percentage points because it values avoided stockout product-days.'),
      (table(['Specification','Exposure definition','Coefficient meaning'],[['ΔY = α+βx+u','Fixed baseline exposure x','Outcome change per unit of x'],['ΔY = α+βΔx+u','Exposure change after−before','Outcome change per unit of Δx']], 'Two continuous-exposure formulations; neither is fitted to an invented retail dose'),
       'A baseline-dose-by-After interaction in levels becomes the first equation after differencing. Differencing a level model with a time-varying exposure can produce the second. Define the units, timing, functional form and comparison argument before interpreting either coefficient as an effect gradient. The binary rollout does not record continuous alert intensity, so no continuous-dose effect is claimed.'),
      (formula('Signed contrast = ATT + δ\nA separate favorable adopter shift s implies δ=−s\nTrue policy reduction in this scenario = observed reduction − s\nBreak-even s = 4.585714 − 20/8.4 = 2.204762'),
       'The scenario shifts the effect attribution, not the observed table. At s=1 the attributed reduction is 3.585714 and the saving is 10.12. At the break-even value the point-estimate saving is zero. This calculation does not estimate the probability or size of the competing shock. Its purpose is to turn an identifying assumption into a concrete management question about simultaneous operations.')
    ]
    refs='<p>Further reading: <a href="https://www.jonathandroth.com/assets/files/roth_pretrends_testing.pdf">Roth: pre-trend diagnostics and pretesting</a>. Related lessons: <a href="lesson-7.html">potential outcomes and assignment</a>; <a href="lesson-8.html">choosing controls by causal role</a>; <a href="lesson-4.html">log transformations</a>.</p>'
    c['appendix_extra']='<section id="did-worked"><h2>Trace identification, estimation and extensions</h2>'+''.join(block(t,vis,note) for t,(vis,note) in zip(DETAIL_TITLES,details))+refs+'</section>'
    c['appendix_extra']+='<section id="weekly-values"><h2>Inspect the complete observed weekly series</h2>'+table(['Week','Adopters %','Comparison %'],[[x['week'],f(x['adopters']),f(x['usual'])] for x in series], 'Observed rollout-cohort means; weeks 17–24 and 25–32 form the main contrast')+p('Each weekly value averages twenty-five stores in its group. The vertical marker in the main chart identifies week 25. These are observed paths, not the constructed counterfactual line used in the two-period diagram.')+'</section>'
    return c
