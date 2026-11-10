"""Worked graphical identification, adjustment, and population weighting."""
from functools import lru_cache
from math import hypot
from lesson7_depth import picture
from lesson2_depth import text

CALCULATIONS = '''# D-separation by ancestral moralization: parents become neighbors.
def l8_separated(edges, a, b, conditioned):
    edges = set(edges); z = set(conditioned); ancestors = {a,b} | z
    while True:
        expanded = ancestors | {u for u,v in edges if v in ancestors}
        if expanded == ancestors: break
        ancestors = expanded
    adjacent = {u:set() for u in ancestors}
    for child in ancestors:
        parents = {u for u,v in edges if v == child}
        for parent in parents:
            adjacent[parent].add(child); adjacent[child].add(parent)
            adjacent[parent].update(parents-{parent})
    reached = set(); frontier = [a]
    while frontier:
        node = frontier.pop()
        if node in reached or node in z: continue
        reached.add(node); frontier.extend(adjacent[node]-reached-z)
    return b not in reached
# The graph supplies assumptions; these checks do not learn arrows from data.
l8_queries = [
    ([('X','M'),('M','Y')], 'X','Y', [], False),
    ([('X','M'),('M','Y')], 'X','Y', ['M'], True),
    ([('X','Y'),('X','Z')], 'Y','Z', ['X'], True),
    ([('B','A'),('C','A'),('A','R')], 'B','C', [], True),
    ([('B','A'),('C','A'),('A','R')], 'B','C', ['R'], False),
    ([('C','A'),('C','B'),('B','E'),('D','E')], 'A','D', ['E'], False),
    ([('C','A'),('C','B'),('B','E'),('D','E')], 'A','D', ['E','C'], True),
]
assert all(l8_separated(e,a,b,z)==answer for e,a,b,z,answer in l8_queries)
# A deterministic population covariance calculation verifies sign reversal.
l8_var_t = .5**2+1; l8_sorting = .5/l8_var_t
l8_short = 1-5*l8_sorting
assert np.isclose(l8_short,-1)
# Y=2T+e, C=5T+Y+v, Var(e)=Var(v)=.04, independent disturbances.
l8_collider_slope = 2-7*(.04/(.04+.04))
assert np.isclose(l8_collider_slope,-1.5)
# Homoskedastic linear-model variance factors, relative to no extra control.
l8_outcome_only_factor = 1/(2**2+1)
l8_treatment_only_factor = (2**2+1)/1
assert np.allclose([l8_outcome_only_factor,l8_treatment_only_factor],[.2,5])
# One post-period mean per store in the voluntary-adoption cohort.
l8_panel = world()['panel']
l8_rows = l8_panel.query("cohort=='Voluntary' and 17<=week<=24")
l8_stores = l8_rows.groupby(['store_id','offer','risk_group']).stockout_rate.mean().reset_index()
l8_strata = []
for name, rows in l8_stores.groupby('risk_group'):
    contrast = rows.loc[rows.offer==0,'stockout_rate'].mean()-rows.loc[rows.offer==1,'stockout_rate'].mean()
    l8_strata.append(dict(group=name,n=len(rows),n1=int(rows.offer.sum()),n0=int((1-rows.offer).sum()),reduction=float(contrast)))
l8_estimates = {target:sum(g['reduction']*g[count]/sum(h[count] for h in l8_strata) for g in l8_strata)
                for target,count in [('ate','n'),('att','n1'),('atu','n0')]}
l8_saved = lesson_result(8)
for target in l8_estimates:
    assert np.isclose(l8_estimates[target],l8_saved['depth'][target])
assert np.isclose(l8_estimates['ate'],26/50*l8_estimates['att']+24/50*l8_estimates['atu'])
# The existing separate mechanism experiments are reproducible in the shared source.
for experiment in l8_saved['depth']['simulations']:
    assert experiment['total_reduction'] == 3 and np.isfinite(experiment['adjusted'])
'''
CODE_TITLES = [
 'Collect ancestors before checking the graph implied by conditioning',
 'Connect common parents and test reachability after conditioning',
 'Verify chain and combined collider path exercises',
 'Calculate population bias and compare precision under explicit linear models',
 'Construct store comparisons and the three target weighting rules',
 'Verify population averages and reproduce the mechanism summaries',
]
DETAIL_TITLES = [
 'Ancestral moralization checks whether conditioning blocks every path',
 'The graph exercises have reproducible separation answers',
 'Regression simulations connect the diagrams to changes in estimated slopes',
 'The omitted-variable identity explains the sign reversal algebraically',
 'A collider can reverse a coefficient even without initial confounding',
 'Precision depends on residual noise and remaining treatment variation',
 'Conditional exchangeability identifies the observed comparison within each stratum',
 'Changing population weights changes the average while keeping comparisons fixed',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    scope=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson8-worked-calculations','exec'),scope)
    return scope

def graph(title,nodes,edges,caption,marked=(),height=250):
    """Native SVG causal diagram; fill indicates a conditioned variable."""
    body=''
    for start,end in edges:
        x,y=nodes[start];xx,yy=nodes[end];length=hypot(xx-x,yy-y);dx=(xx-x)/length;dy=(yy-y)/length
        ax,ay=x+29*dx,y+29*dy;bx,by=xx-33*dx,yy-33*dy
        body+=f'<line x1="{ax}" y1="{ay}" x2="{bx}" y2="{by}" stroke="#436c61" stroke-width="3"/>'
        body+=f'<path d="M {bx} {by} L {bx-10*dx+5*dy} {by-10*dy-5*dx} L {bx-10*dx-5*dy} {by-10*dy+5*dx} Z" fill="#436c61"/>'
    for name,(x,y) in nodes.items():
        fill='#cce6da' if name in marked else '#f7faf7'
        body+=f'<circle cx="{x}" cy="{y}" r="28" fill="{fill}" stroke="#436c61" stroke-width="2"/>'+text(x,y+7,name,22,'middle')
    return picture(title,body,caption,height)

def restore(c):
    from retail_ui import table,formula,p
    from retail_content import section
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();r=d['l8_saved'];g=r['strata'];fmt=lambda x:f'{x:.2f}'
    c['authored_sections']=True
    c['sections']=[]
    c['headlines']={k:v for k,v in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    def block(title,visual,*notes):return teach(title,visual.replace('\n','<br>') if 'class="calculation"' in visual else visual,list(notes))
    def put(key,title,body,phase='General theory'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    c['brief']='Managers in a separate 50-store cohort chose whether to adopt alerts. Which starting differences must the comparison account for? Learn to read the causal paths first, then choose an adjustment set and calculate a like-for-like comparison.'
    put('identification','Define what makes an observational comparison credible',
      block('Comparable potential outcomes require conditioning on the relevant starting variables',formula('(Y(0), Y(1)) ⟂ D | X\n0 < P(D=1 | X=x) < 1'),
        'Conditional exchangeability means that within X, treatment assignment carries no further information about either potential outcome. Positivity, or overlap, supplies both options at each relevant profile. Consistency connects the observed outcome to the defined treatment received. These conditions turn a comparison into a causal argument; they are not established by a good model fit.')+
      block('A causal graph states assumptions about how variables affect one another',bullets('Nodes represent variables; arrows represent direct causal links','A parent sends an arrow; a descendant lies downstream','A path follows connected nodes in either direction','A directed acyclic graph has no directed feedback loop'),
        'A DAG is a directed acyclic graph. Time order and knowledge of the assignment process guide its arrows. A path need not follow all arrows forward: D ← X → Y is a path between D and Y. Feedback over time can be represented using variables at different dates. Software checks implications of a supplied graph; it does not make the causal assumptions true.'))
    put('graph-structures','Read the three basic structures before choosing controls',
      block('A chain transmits an effect through an intermediate variable',graph('Chain: D → M → Y',{'D':(110,110),'M':(360,110),'Y':(610,110)},[('D','M'),('M','Y')],'M is the mediator; conditioning on M blocks this path.',height=220),
        'In this pure chain, D and Y are d-separated given M: after fixing the mediator, the graph has no remaining open D–Y path. Without that conditioning the path is open. For a total-effect question, the pathway through M is part of the effect. Conditioning on it removes that pathway; a direct-effect question needs its own identification argument.')+
      block('A fork creates an association through a shared cause',graph('Fork: D ← X → Y',{'D':(140,175),'X':(360,65),'Y':(580,175)},[('X','D'),('X','Y')],'X is a common cause; fixing X blocks this path.'),
        'In the pure fork, conditioning on X d-separates D and Y. If a direct causal arrow D → Y is also present, adjustment removes the common-cause path but leaves the causal path open. Removing confounding is therefore different from removing every association between treatment and outcome.')+
      block('A collider blocks a path until it or its descendant is conditioned on',graph('Collider: D → C ← Y',{'D':(140,65),'C':(360,175),'Y':(580,65)},[('D','C'),('Y','C')],'C is a common consequence; selecting C can link its two causes.'),
        'Two arrowheads meet at C, making it a collider on this path. The path is blocked without conditioning. Among units selected for a common consequence, one cause may compensate for another: among stores escalated because of alerts or poor performance, knowing one reason changes what we infer about the other. Conditioning includes regression adjustment, stratification and restricting the sample.')+
      block('D-separation requires every path between the queried variables to be blocked',table(['Middle node on a path','Without conditioning','When conditioned'],[['Noncollider: chain or fork','Open at this node','Blocked at this node'],['Collider','Blocked unless a descendant is conditioned on','Open at this node']], 'A path is open only if no node blocks it'),
        'To evaluate a path, a conditioned noncollider blocks it. A collider blocks it unless the collider or one of its descendants is conditioned on. Two variables are d-separated when every path between them is blocked. Under the DAG assumptions this implies conditional independence. An open path permits association, but it does not guarantee a nonzero coefficient or a significant test in every sample.'))
    put('combined-paths','Practice how conditioning changes a path',
      block('Conditioning downstream of a collider can also open its path',graph('B → A ← C, with A → R',{'B':(160,55),'C':(560,55),'A':(360,125),'R':(360,220)},[('B','A'),('C','A'),('A','R')],'Predict whether B and C are separated: no control, A, then R.',height=270),
        'Pause before revealing the answer. A is a collider between B and C. R is its descendant. Even if A itself is not included as a control, selecting on R supplies information about A and can open the same collider path.')+
      block('The descendant exercise changes from separated to connected',table(['Conditioning set','B and C d-separated?','Reason'],[['None','Yes','A blocks the path'],['A','No','The collider is conditioned on'],['R','No','A descendant of the collider is conditioned on']], 'Read the blocking rule at each internal node'),
        'The answer concerns the graph’s implied separation, not a test performed on data. A downstream consequence can create the same selection problem as directly controlling the common consequence. The appendix checks these implications using the graph edges.')+
      block('Opening a collider does not prevent another node from blocking the same path',graph('A ← C → B → E ← D',{'A':(70,130),'C':(215,55),'B':(360,130),'E':(505,205),'D':(650,130)},[('C','A'),('C','B'),('B','E'),('D','E')],'Compare no control, E, then E together with C.',height=260),
        'Start at A and trace the only route to D. C is a noncollider on this path; E is a collider. Ask students to identify the blocking node for each conditioning set before showing the next table.')+
      block('Conditioning on the noncollider reblocks the opened route',table(['Conditioning set','A and D d-separated?','Blocking node'],[['None','Yes','E is an unconditioned collider'],['E','No','No node now blocks the route'],['E and C','Yes','C is a conditioned noncollider']], 'A variable’s role is evaluated on a particular path'),
        'Conditioning on E opens that node, but conditioning on C closes another point of the same route. Thus a simple slogan about one variable is not enough: evaluate the whole path and then every other path. These query answers do not themselves specify a treatment effect.'))
    put('backdoor','Choose a set that blocks all backdoor paths',
      block('The standard backdoor criterion preserves causal paths while removing confounding routes',bullets('Name treatment D, outcome Y and the total-effect target','List paths whose first arrow points into D','Block every such path with the proposed adjustment set','Exclude descendants of D from this standard set'),
        'The backdoor criterion is a sufficient graphical identification rule. A backdoor path starts with an arrow entering treatment. D → C ← Y is a noncausal collider path, but is not a backdoor path because its first arrow leaves D. For total-effect adjustment, use a set with no treatment descendants that blocks every incoming-treatment path. Other identification strategies exist; this is the rule used here.')+
      block('Two common causes create two separate backdoor paths',graph('Both X and Z affect assignment and outcome',{'D':(130,130),'Y':(590,130),'X':(360,45),'Z':(360,215)},[('X','D'),('X','Y'),('Z','D'),('Z','Y'),('D','Y')],'Paths: D ← X → Y and D ← Z → Y, plus causal D → Y.',height=275),
        'Assume this graph contains the relevant causes. There are two backdoor routes, one through X and one through Z. A model with only X still mixes the causal effect with the path through Z. The direct treatment arrow should remain open.')+
      block('Controlling only one common cause leaves the other route open',table(['Proposed set','Path through X','Path through Z','Valid here?'],[['None','Open','Open','No'],['X','Blocked','Open','No'],['Z','Open','Blocked','No'],['X and Z','Blocked','Blocked','Yes']], 'Validity is relative to the stated graph and total-effect question'),
        'The table is a complete path audit for this graph, not a recommendation to include every recorded variable. Adding a mediator could remove part of the intended total effect; adding a selected consequence could open a new route. Explain what each control does before fitting the regression.'))
    sims=r['depth']['simulations']
    put('regression-effects','Connect graph roles to fitted coefficients',
      block('The same added control changes the comparison according to its causal role',table(['Mechanism','Added variable','Unadjusted reduction','Adjusted reduction'],[[x['mechanism'],x['control'],fmt(x['naive']),fmt(x['adjusted'])] for x in sims], 'Three separate 3,000-scenario mechanism experiments; known total reduction = 3'),
        'Each row comes from a separate generated mechanism experiment, not additional operating stores. The outcome is a continuous stockout-pressure index. Regress it first on an offer indicator and then add the named variable. Report minus the offer coefficient as a reduction. The chain comparison removes a pathway, the fork comparison removes confounding, and the collider comparison introduces selection. Full generation equations and reproducible source appear in the appendix.')+
      block('Removing a mediator and removing a confounder answer different questions',bullets('Chain: review transmits the whole effect; the remaining direct effect is near zero','Fork: starting pressure affects offer and outcome; adjustment recovers the total effect','Collider: escalation follows offer and outcome; adjustment distorts the total effect'),
        'The chain’s adjusted estimate is not a failed estimate of the same target: conditioning on the sole mediator removes the route that generated the total reduction. In the fork, treatment still has a direct effect after the common cause is controlled. In the collider experiment the original randomized comparison already identifies the effect, so adding escalation creates the problem. Statistical significance cannot choose among these causal stories.')+
      block('Omitted-variable bias can reverse the sign of a treatment coefficient',formula('Short slope = causal slope + omitted effect × sorting slope\n−1 = +1 + (−5) × 0.4'),
        'Recall Lesson 5’s coefficient identity. Consider the explicit linear model T=0.5X+u and Y=T−5X+e, with independent mean-zero disturbances and Var(X)=Var(u)=1. The regression of X on T has slope 0.5/1.25=0.4. Omitting X changes the population treatment slope from +1 to −1. The causal graph supplies the interpretation that the omitted X is a common cause; algebra alone does not establish that.')+
      block('Adding a collider can reverse an otherwise correct treatment coefficient',formula('Y = 2T + e; C = 5T + Y + v\nSlope of Y on T: +2\nSlope of Y on T and C: −1.5'),
        'For this labelled population example, T, e and v are mutually independent, with Var(e)=Var(v)=0.04. C is caused by both T and Y. At fixed C, larger T must be offset by other components, inducing a misleading conditional relation. The appendix derives the −1.5 coefficient. This example is separate from the binary-offer retail mechanism experiment.'))
    put('precision-controls','Separate identification from estimation precision',
      block('An outcome-only predictor can reduce unexplained outcome variation',graph('D → Y ← X',{'D':(130,100),'Y':(360,100),'X':(590,100)},[('D','Y'),('X','Y')],'D and X are independent; X predicts Y and is measured before treatment.',height=210),
        'Assume Y=βD+2X+e with D, X and e mutually independent, Var(X)=Var(e)=1 and constant error variance. Both the regression on D and the regression on D plus X identify β. Including X reduces residual variance from 5 to 1 without reducing the population variation in D. The large-sample slope variance is one fifth as large in this example. X is a precision control, not a mediator.')+
      block('A treatment-only predictor can reduce the variation available to estimate the effect',graph('X → D → Y',{'X':(130,100),'D':(360,100),'Y':(590,100)},[('X','D'),('D','Y')],'X predicts D but has no separate route to Y.',height=210),
        'Assume D=2X+u and Y=βD+e, with mutually independent disturbances and unit variances for X, u and e. Both regressions identify β. Adding X leaves outcome noise unchanged but reduces residual treatment variance from 5 to 1, so the large-sample slope variance is five times larger. This is a precision comparison under the stated linear model, not a universal claim that treatment predictors create bias.')+
      block('Good prediction alone does not determine a good causal control',table(['Question','What to inspect'],[['Identification','Does the set block the relevant noncausal paths?'],['Target','Does adjustment remove a pathway included in the effect?'],['Precision','How do residual noise and treatment variation change?']], 'Choose the effect and comparison before optimizing the model'),
        'A control may improve prediction while changing the causal target or introducing selection. First establish an admissible comparison, then consider precision. Large datasets do not remove the need to understand assignment and measurement.'))
    put('proxies','Distinguish blocking a path from measuring a related variable',
      block('A measured intermediary can block a route from an unobserved cause',graph('U → M → D → Y, with U → Y',{'U':(130,60),'M':(350,60),'D':(570,60),'Y':(350,195)},[('U','M'),('M','D'),('D','Y'),('U','Y')],'M is measured before D; conditioning on M blocks D ← M ← U → Y.',marked=('M',),height=255),
        'U is unobserved, but all its influence on treatment passes through measured M in this stated graph. Conditioning on M blocks the backdoor path, even though U also directly affects Y. M is downstream of U, not downstream of treatment. This is exact graphical identification under the specified assumptions, rather than a general promise about proxy quality.')+
      block('A noisy proxy can leave the unobserved common-cause path open',graph('U causes M, D and Y',{'U':(350,65),'M':(130,190),'D':(350,190),'Y':(590,190)},[('U','M'),('U','D'),('U','Y'),('D','Y')],'Conditioning on M leaves D ← U → Y open.',marked=('M',),height=250),
        'Here M is a measurement related to U rather than an intermediary through which assignment operates. Adjusting for M need not remove the path through U. A near-perfect measure and a noisy measure are different statistical situations; the graph alone does not guarantee that an ordinary proxy resolves confounding. In the retail world the assignment rule explicitly uses the measured baseline rate, delivery time and location.'))
    put('conditional-effects','Turn the identification argument into a weighted estimate',
      block('Conditional exchangeability connects potential outcomes to observed group means',formula('τ(x) = E[Y(1) − Y(0) | X=x]\n= E[Y(1)|D=1,X=x] − E[Y(0)|D=0,X=x]\n= E[Y|D=1,X=x] − E[Y|D=0,X=x]'),
        'The transition to the second line uses conditional exchangeability: within X, selection into treatment does not change the potential-outcome means. Consistency gives the final observed-outcome line. Positivity ensures both conditional groups are represented. This identifies a conditional effect before any choice of target-population weights.')+
      block('The target population determines which weights combine the conditional effects',formula('ATE = Σₓ τ(x)P(X=x)\nATT = Σₓ τ(x)P(X=x | D=1)\nATU = Σₓ τ(x)P(X=x | D=0)'),
        'Use all-unit, treated-unit or untreated-unit proportions according to whose effect is wanted. In a sample these weights become n_x/n, n_1x/n_1 and n_0x/n_0. The conditional comparisons stay fixed while their weights change. The same identification assumptions support this common-effect-within-X calculation.')+
      block('A missing comparison group prevents a within-stratum estimate',table(['Illustrative stratum','Treated','Untreated','Observed comparison?'],[['Profile A',6,5,'Yes'],['Profile B',4,0,'No']], 'Small teaching example, separate from the course records'),
        'For profile B no untreated observations supply its comparison. A regression prediction there would extrapolate beyond the observed overlap. With many covariates, exact strata can become sparse even in sizeable datasets. Matching offers a different construction of comparable units; Lesson 9 develops distances, retained populations and balance checks.'))
    put('read-data','Specify the retail assignment story before estimating',
      block('The voluntary cohort asks a different question from the randomized pilot',bullets('Stores S051–S100: 50 voluntary-adoption stores','Starting characteristics precede week 17','Outcome: one store average over weeks 17–24','Report a positive reduction as usual rate minus alert rate'),
        'The pilot and voluntary cohorts are distinct studies. For the latter, managers choose alerts rather than receiving a random assignment. Delivery time, urban location and weeks 1–8 baseline performance help describe that selection. The signed outcome effect is alert minus usual; the business improvement reverses that sign because lower stockouts are better. Each store, not each store-week, supplies one outcome here.')+
      block('Recorded starting conditions guide the proposed adoption comparison',graph('L, B and R each affect adoption D and outcome Y',{'L':(150,45),'B':(360,45),'R':(570,45),'D':(160,205),'Y':(560,205)},[('L','D'),('L','Y'),('B','D'),('B','Y'),('R','D'),('R','Y'),('D','Y')],'L: delivery time; B: baseline rate; R: urban indicator. All three are measured.',height=265),
        'R denotes the measured urban indicator. Each baseline variable can affect both adoption and later stockouts. The diagram displays the adjustment argument for these recorded starting conditions; relations among the starting variables are suppressed for readability. Post-alert review effort belongs to the policy pathway, and escalation based on adoption or poor results can be a selected consequence.')+
      block('Adopters begin with longer delivery cycles and higher prior stockout rates',table(['Starting variable','Adopters','Nonadopters'],[[v['variable'],fmt(v['adopters']),fmt(v['comparison'])] for v in r['balance']], 'Measured before adoption; same 50 stores'),
        'The table describes baseline imbalance; it does not determine arrows by statistical testing. Delivery time and prior performance differ between the groups. The graph and operating history explain why these differences matter to the comparison.'))
    put('calculate','Calculate the first within-group comparisons',
      block('Both delivery groups contain adopters and nonadopters',table(['Delivery group','Adopters','Nonadopters','Usual rate','Alert rate','Reduction'],[[x['group'],x['offered'],x['control'],fmt(x['usual']),fmt(x['alerts']),fmt(x['reduction'])] for x in g], 'Rates in percent; differences in percentage points'),
        'Average the eight post-period observations within each store first. Then average stores within treatment and delivery group. Long-delivery stores have a 12.57% usual-operation mean and a 9.26% alert mean; their difference is 3.31 points. The short-delivery comparison is 2.06 points. Both groups have observed treatment and control units.')+
      block('The all-store target weights delivery groups by their population shares',formula('All-store reduction = (18/50) × 3.31101 + (32/50) × 2.06278\n= 1.19196 + 1.32018 = 2.51215 points'),
        'Eighteen of the fifty stores have long delivery cycles; thirty-two have short cycles. These shares sum to one. The raw comparison was 2.06 points, so standardizing the delivery mix changes the estimate to 2.51. Rounded displayed values explain the arithmetic; the executable calculation uses full precision.'))
    put('target-weights','Use the same comparisons for three clearly named populations',
      block('Adopters and nonadopters give different weights to the same delivery groups',table(['Population','Long-delivery weight','Short-delivery weight','Reduction'],[['All 50 stores','18/50','32/50',fmt(r['depth']['ate'])],['26 adopters','12/26','14/26',fmt(r['depth']['att'])],['24 nonadopters','6/24','18/24',fmt(r['depth']['atu'])]], 'Delivery-stratified estimates; percentage-point reductions'),
        'Adopters contain a larger share of long-delivery stores, the group with the larger observed within-stratum reduction. That raises the adopter-weighted average. Changing weights does not create new within-group comparisons or introduce additional adjustment variables.')+
      block('Writing all three sums makes the population choice visible',formula('Adopters: (12/26) × 3.31101 + (14/26) × 2.06278 = 2.63889\nNonadopters: (6/24) × 3.31101 + (18/24) × 2.06278 = 2.37484\nAll stores: (26/50) × 2.63889 + (24/50) × 2.37484 = 2.51215'),
        'The last line verifies the weighting identity from Lesson 7 on these estimated conditional reductions. Name these as delivery-stratified summaries. Delivery groups coarsen lead time and do not also adjust for baseline performance and urban location; Lesson 9 uses the recorded variables together.'))
    put('act','Carry the comparison design into the next analysis',
      block('The next estimate should follow the graph and preserve the target population',bullets('Define the 50-store cohort and week-17 decision','Use recorded starting conditions for the fuller comparison','Keep alert-induced responses inside the total-effect pathway','Check overlap and name the population retained by matching'),
        'The immediate output is an evaluation design, not a search for the regression with the most impressive coefficient. The fuller model and matching analysis in Lesson 9 implement the comparison using the same stores, outcome period and measured covariates. Its estimates should be interpreted for their stated target populations. Software and AI can help draw and check the graph; the analyst remains responsible for defending its arrows and measurement choices.'),phase='Worked application')
    put('interpret','Explain what the initial adjustment has accomplished',
      block('Delivery standardization changes the mix but does not finish the adjustment',bullets('Raw usual-minus-adopter gap: 2.06 points','Common delivery mix: 2.51 points','Location and baseline performance remain part of the comparison design'),
        'The change in the estimate shows why the distribution of starting conditions matters. These broad delivery strata demonstrate the weighting method. They do not claim that every common-cause path in the adoption graph has now been blocked. Carry the complete recorded adjustment set into the next lesson.'),phase='Worked application')
    c['sections'].insert(-1,c['sections'].pop())
    next(s for s in c['sections'] if s['id']=='calculate')['body']+='<p><a href="lesson-8-appendix.html#calculation">Follow this calculation further →</a></p>'
    # Mark all retail sections as applications after the completed theory.
    for s in c['sections']:
        if s['id'] in {'read-data','calculate','target-weights'}:s['phase']='Worked application'
    c['code']=CALCULATIONS
    c['technical']=[
      'Use only S051–S100, one store-level mean over weeks 17–24. The graph exercises and continuous mechanism experiments are separate teaching examples; they do not add rows to the operating dataset.',
      'Run the graph-separation checks, verify the population sign reversals and precision factors, and reconstruct the three delivery-stratified estimates from the shared records. The existing generator also reproduces the three mechanism regressions.',
      'Graphical identification is separate from sampling uncertainty. In the mechanism experiments, the reported coefficient is minus the offer slope. The precision examples compare large-sample homoskedastic linear-regression variances under explicit independent-variable models; their factors are illustrative rather than estimates for the retail cohort.',
      'Add a second common cause to a graph and identify which former adjustment set fails. Then change the retail weights from all stores to nonadopters, keeping stratum comparisons fixed, and explain whose decision the new average informs.'
    ]
    details=[
      (bullets('Retain ancestors of the two queried nodes and the conditioning set','Ignore directions and connect parents sharing a child','Remove conditioned nodes','Check whether the queried nodes remain connected'),
       'The compact lab implements ancestral moralization for these small, valid DAGs with disjoint query sets. Moralization connects parents of a common child in the ancestral graph. Conditioning on a collider descendant can bring the collider into that ancestral set. Removing the conditioned variables then gives an ordinary reachability test. This is a graph check, not a statistical test or a causal-discovery algorithm.'),
      (table(['Graph','Query','Condition','Separated?'],[['Chain','X, Y','M','Yes'],['Fork','Y, Z','X','Yes'],['Collider descendant','B, C','None','Yes'],['Collider descendant','B, C','R','No'],['Fork plus collider','A, D','E','No'],['Fork plus collider','A, D','E and C','Yes']], 'The same graph implications used in the main exercises'),
       'NetworkX provides is_d_separator for a valid DAG and disjoint node sets. Use the exact arrows shown in the lesson: reversing the collider arrows produces a fork and reverses the intended conclusion. All queried nodes must exist. The supplied pure-Python check avoids requiring a graph package for the downloadable lab.'),
      (formula('Chain: M=1.5D+u; Y=20−2M+e\nFork: D=1[0.8X+u>0]; Y=12+2X−3D+e\nCollider: Y=12−3D+e; C=0.8D+0.8Y+v'),
       'The shared source uses 3,000 scenarios per experiment, seed 20261109+808 and independent standard-normal disturbances. D is Bernoulli(0.5) in the chain and collider experiments; X is standard normal in the fork. Regress Y on an intercept and D, then add M, X or C. The displayed reductions are minus the D slopes. The known total reduction is 3 in each experiment; the chain has no remaining direct pathway after fixing M.'),
      (formula('T=0.5X+u; Var(X)=Var(u)=1\nSlope(X on T)=Cov(X,T)/Var(T)=0.5/1.25=0.4\nY=T−5X+e ⇒ short slope=1−5(0.4)=−1'),
       'Independent disturbances make X a common cause and make the adjusted treatment slope equal its structural value +1. The identity is the same algebra taught in Lesson 5, now interpreted using assignment assumptions. Intercepts do not affect these slopes. Finite-sample fitted slopes fluctuate around the population calculation.'),
      (formula('C=5T+Y+v=7T+e+v\nCoefficient on C given T=Var(e)/[Var(e)+Var(v)]=0.5\nCoefficient on T given C=2−7(0.5)=−1.5'),
       'The covariance calculation uses mutually independent T, e and v with equal positive disturbance variances. After partialling out T, C contains e+v and Y contains e. Their regression slope is one half. Subtracting that share of 7T from the original 2T yields −1.5. The reversal is introduced by the collider control, not by pre-existing confounding.'),
      (formula('Large-sample Var(β̂_D) ≈ σ² / [n Var(D residualized on X)]\nOutcome-only example: variance ratio = 1/5\nTreatment-only example: variance ratio = 5'),
       'For the outcome-only example, adding X lowers residual outcome variance from 5 to 1 while D’s variance is unchanged. For the treatment-only example, adding X leaves the outcome error variance unchanged while residual treatment variance falls from 5 to 1. These are asymptotic model-based comparisons; finite samples also use degrees of freedom and actual realized designs. More general heteroskedastic settings need the appropriate covariance calculation.'),
      (formula('E[Y(j)|X=x]=E[Y(j)|D=j,X=x]=E[Y|D=j,X=x]\nτ(x)=m₁(x)−m₀(x); ATE=Σₓ τ(x)P(X=x)'),
       'The first equality uses conditional exchangeability and the second consistency. Positivity is required at the relevant profiles. Averaging over X uses the law of total expectation. ATE, ATT and ATU differ through their target distributions of X. Identification does not require a linear response surface; the sample implementation must still estimate the conditional means adequately.'),
      (formula('w_ATE,x=n_x/n; w_ATT,x=n_1x/n_1; w_ATU,x=n_0x/n_0\nReduction_target=Σₓ w_target,x(ȳ₀x−ȳ₁x)'),
       'For the retail calculation, the two groups contribute 1.19196 and 1.32018 points to the all-store average. There are 26 adopters and 24 nonadopters. The worked lab verifies all three averages and their population-share identity using full precision. Broader covariate adjustment and exact or approximate matching continue in Lesson 9; their retained populations must be named.')
    ]
    refs='<p>Further reading: <a href="https://networkx.org/documentation/stable/reference/algorithms/d_separation.html">Graph separation and software checks</a>; <a href="https://ftp.cs.ucla.edu/pub/stat_ser/r416-reprint.pdf">Pearl: The Mathematics of Causal Inference</a>; <a href="lesson-5.html">Regression and omitted-variable algebra</a>; <a href="lesson-9.html">Matching and fuller adjustment</a>.</p>'
    c['appendix_extra']='<section id="graph-worked"><h2>Reproduce the graphical and numerical reasoning</h2>'+''.join(block(t,v,n) for t,(v,n) in zip(DETAIL_TITLES,details))+refs+'</section>'
    return c
