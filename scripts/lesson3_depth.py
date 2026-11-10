"""Inference illustrated, then reconstructed using the existing shelf audit.

General-theory illustrations are explicitly labelled. Case calculations use
the same audit, matched system readings, and random stream as the course labs.
"""
from functools import lru_cache
import numpy as np
from scipy.stats import binom, norm, t
from lesson2_depth import figure, text

DETAIL_TITLES = [
    'Unbiasedness, consistency, and root-n behavior describe different estimator properties',
    'The central limit theorem concerns scaled estimation error',
    'The audit combines store selection with within-store measurement variation',
    'Wilson intervals estimate a proportion without using a symmetric Wald interval',
    'Pairing makes the within-unit difference the observation',
    'Welch combines two variance contributions and approximates degrees of freedom',
    'Confidence intervals and tests agree when their directions and levels match',
    'Family-wise control sets a stricter rule across a planned test family',
]

def curve(xs,ys,sx,sy,color='#276451',dash=False):
    points=' '.join(f'{sx(x):.2f},{sy(y):.2f}' for x,y in zip(xs,ys))
    return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.6"'+(' stroke-dasharray="7 5"' if dash else '')+'/>'

def area(xs,ys,sx,sy,color='#b65b32'):
    points=[(sx(xs[0]),sy(0))]+[(sx(x),sy(y)) for x,y in zip(xs,ys)]+[(sx(xs[-1]),sy(0))]
    return '<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{color}" opacity=".35"/>'

def means_figure():
    body=''
    for j,n in enumerate([1,10,50]):
        left=40+230*j;sx=lambda x:left+180*x;sy=lambda y:230-175*y/.65
        k=np.arange(n+1);prob=binom.pmf(k,n,.4)
        body+=text(left,25,f'n = {n}',17)+text(left,48,'Probability',12)
        body+=f'<path d="M {left} 55 V 230 H {left+185}" fill="none" stroke="#9eaa9e"/>'
        for x,y in zip(k/n,prob):body+=f'<line x1="{sx(x)}" x2="{sx(x)}" y1="230" y2="{sy(y)}" stroke="#276451" stroke-width="{max(2,18/n)}"/>'
        body+=f'<line x1="{sx(.4)}" x2="{sx(.4)}" y1="58" y2="230" stroke="#9b421e" stroke-dasharray="4 4"/>'
        for v in [0,.4,1]:body+=text(sx(v),252,v,12,'middle')
        body+=text(left+90,280,f'SE = {np.sqrt(.24/n):.3f}',14,'middle')
    body+=text(360,317,'Sample proportion; dashed line marks the fixed p = 0.4',15,'middle')
    return figure('Larger samples concentrate the mean around its target',body,'Illustrative independent Bernoulli model with p = 0.4. Exact probability masses, not audit observations. All panels use the same axes.')

def coverage_figure():
    rng=np.random.default_rng(20261109+331);draws=rng.normal(10,2,(24,30))
    means=draws.mean(axis=1);margin=t.ppf(.975,29)*draws.std(axis=1,ddof=1)/np.sqrt(30)
    low=means-margin;high=means+margin;covers=(low<=10)&(high>=10)
    sx=lambda x:75+(x-8)*142.5;body=''
    for i,(m,l,h,ok) in enumerate(zip(means,low,high,covers)):
        yy=40+i*10;color='#276451' if ok else '#b65b32'
        body+=f'<line x1="{sx(l)}" x2="{sx(h)}" y1="{yy}" y2="{yy}" stroke="{color}" stroke-width="2"/><circle cx="{sx(m)}" cy="{yy}" r="2.8" fill="{color}"/>'
    body+=f'<line x1="{sx(10)}" x2="{sx(10)}" y1="25" y2="285" stroke="#9b421e" stroke-dasharray="5 4"/>'
    for v in [8,9,10,11,12]:body+=text(sx(v),310,v,14,'middle')
    body+=text(75,18,f'{int(covers.sum())} of these 24 intervals cover the fixed mean',16)
    return figure('Intervals vary across samples while the population mean stays fixed',body,'Illustration: 24 independent normal samples, n = 30, population mean 10 and SD 2. Each line is a 95% t interval; orange lines miss the target.',340)

def t_figure():
    xs=np.linspace(-4,4,321);sx=lambda x:70+(x+4)*72;sy=lambda y:250-490*y
    body=''
    for label,ys,col,dash in [('Normal',norm.pdf(xs),'#183f36',False),('t, df = 4',t.pdf(xs,4),'#b65b32',True),('t, df = 29',t.pdf(xs,29),'#3259a2',True)]:
        body+=curve(xs,ys,sx,sy,col,dash)
    body+=f'<line x1="70" x2="650" y1="250" y2="250" stroke="#9eaa9e"/>'
    for v in [-4,-2,0,2,4]:body+=text(sx(v),275,v,13,'middle')
    body+=text(70,25,'Density',14)+text(360,309,'Standardized statistic',15,'middle')
    return figure('Small-sample t reference distributions have heavier tails',body,'Normal: dark solid; t with 4 degrees of freedom: orange dashed; t with 29: blue dashed. The t distribution approaches normal as degrees of freedom increase.')

def rejection_figure():
    body='';xs=np.linspace(-4,4,401)
    for j,two in enumerate([False,True]):
        left=40+350*j;sx=lambda x:left+32*(x+4);sy=lambda y:230-390*y
        cutoff=t.ppf(.975 if two else .95,29);ys=t.pdf(xs,29)
        body+=text(left,25,'Two-sided: 2.5% in each tail' if two else 'Right-sided: 5% in one tail',14)
        for sign in ([-1,1] if two else [1]):
            xx=np.linspace(-4,-cutoff,100) if sign==-1 else np.linspace(cutoff,4,100)
            body+=area(xx,t.pdf(xx,29),sx,sy)
            body+=f'<line x1="{sx(sign*cutoff)}" x2="{sx(sign*cutoff)}" y1="85" y2="230" stroke="#9b421e" stroke-dasharray="4 3"/>'
            body+=text(sx(sign*cutoff),258,f'{sign*cutoff:.3f}',13,'middle')
        body+=curve(xs,ys,sx,sy)+text(sx(0),279,'0',12,'middle')
    body+=text(360,315,'Null t distribution with 29 degrees of freedom',15,'middle')
    return figure('A 5% rejection rule allocates tail area according to the alternative',body,'Reject beyond the marked boundary or boundaries. The critical value is a quantile of the null distribution; it is not always 2.')

def power_figure():
    xs=np.linspace(-4,6,501);sx=lambda x:65+(x+4)*59;sy=lambda y:245-480*y;c=norm.ppf(.95)
    tail=np.linspace(c,6,180);body=area(tail,norm.pdf(tail),sx,sy,'#b65b32')+area(tail,norm.pdf(tail-2),sx,sy,'#4b79ad')
    body+=curve(xs,norm.pdf(xs),sx,sy,'#b65b32')+curve(xs,norm.pdf(xs-2),sx,sy,'#3259a2',True)
    body+=f'<line x1="{sx(c)}" x2="{sx(c)}" y1="30" y2="250" stroke="#183f36" stroke-dasharray="5 4"/>'
    body+=text(75,25,'Null: N(0,1), solid',15)+text(380,25,'Alternative: N(2,1), dashed',15)
    for v in [-4,-2,0,2,4,6]:body+=text(sx(v),275,v,13,'middle')
    body+=text(360,310,f'Right-tail cutoff {c:.3f}; power = {100*norm.sf(c-2):.1f}%',15,'middle')
    return figure('Power is the alternative probability beyond the rejection boundary',body,'Illustrative normal reference model: false-positive probability is 5%; detection probability is 63.9% for the stated two-SE shift. The remaining alternative area is a missed signal.')

def draw_figure(ids):
    labels=[('Observed excerpt',ids),('Subsample, no replacement',[ids[0],ids[2],ids[4]]),('Bootstrap, with replacement',[ids[1],ids[1],ids[3],ids[0],ids[3]])]
    body=''
    for j,(label,vals) in enumerate(labels):
        yy=60+90*j;body+=text(18,yy-20,label,15)
        for k,v in enumerate(vals):
            xx=30+128*k;body+=f'<rect x="{xx}" y="{yy}" width="100" height="40" rx="5" fill="#e9efdf" stroke="#276451"/>'+text(xx+50,yy+25,v,16,'middle')
    return figure('Replacement determines whether a store can appear twice in a draw',body,'Five actual audit IDs illustrate the mechanics. The full bootstrap draws 30 rows from all 30 audited stores; the subsampling exercise draws 15 distinct stores.',340)

def histogram(values,title,xlabel,markers=(),bins=16):
    counts,edges=np.histogram(values,bins=bins);lo=min(edges[0],min([v for v,_ in markers],default=edges[0]));hi=max(edges[-1],max([v for v,_ in markers],default=edges[-1]))
    assert counts.sum() == len(values), 'Every plotted observation must fall within the bins'
    pad=.05*(hi-lo or 1);lo-=pad;hi+=pad;sx=lambda v:70+580*(v-lo)/(hi-lo);sy=lambda v:230-175*v/max(counts)
    body=text(70,23,'Count',14)
    for tick in range(5):
        v=max(counts)*tick/4;body+=text(60,sy(v)+4,f'{v:.0f}',12,'end')+f'<line x1="70" x2="650" y1="{sy(v)}" y2="{sy(v)}" stroke="#d6dfd1"/>'
    for a,b,n in zip(edges[:-1],edges[1:],counts):body+=f'<rect x="{sx(a)+.5}" y="{sy(n)}" width="{max(.1,sx(b)-sx(a)-1)}" height="{230-sy(n)}" fill="#276451"/>'
    for v in np.linspace(lo+pad,hi-pad,5):body+=text(sx(v),255,f'{v:.1f}',12,'middle')
    for v,label in markers:
        body+=f'<line x1="{sx(v)}" x2="{sx(v)}" y1="38" y2="230" stroke="#9b421e" stroke-width="2" stroke-dasharray="5 3"/>'+text(sx(v),35,label,12,'middle')
    body+=text(360,292,xlabel,15,'middle')
    return figure(title,body,'The vertical axis counts draws or observations in each interval; dashed lines identify the stated reference values.',315)

@lru_cache(maxsize=1)
def evidence():
    from retail_case import world,SEED,interval,difference
    w=world();audit=w['audit'];a=audit.stockout_rate.to_numpy();rng=np.random.default_rng(SEED+303)
    boot=a[rng.integers(0,len(a),(2000,len(a)))].mean(axis=1)
    paired=audit[['store_id','stockout_rate']].merge(w['panel'].query('week==16')[['store_id','stockout_rate','urban']],on='store_id',suffixes=('_audit','_system'),validate='one_to_one')
    paired['difference']=paired.stockout_rate_audit-paired.stockout_rate_system
    d=paired.difference.to_numpy();pi=interval(d);wi=difference(paired[paired.urban==1].stockout_rate_audit,paired[paired.urban==0].stockout_rate_audit)
    return audit,a,boot,paired,d,pi,wi

def restore(c):
    from retail_ui import section,table,formula,p
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    audit,a,boot,paired,d,pi,wi=evidence()
    def block(title,visual,*notes):return teach(title,visual,list(notes))
    def add(key,heading,body,before,phase):
        c['sections'].insert(next(i for i,v in enumerate(c['sections']) if v['id']==before),dict(**section(key,heading,body),phase=phase))
        c['headlines'][key]=[title for title,_ in visual_frames(Tree(body).root,heading)]
    add('sampling-visuals','See what repeated sampling changes',
        block('Averages stabilize even though individual observations remain variable',means_figure(),
        'Each observation in this illustration is an independent zero or one with probability 0.4 of one. The first panel is the observation distribution; the next panels are exact distributions of sample means for n=10 and n=50. The observations retain the same SD, while SE of their mean is √[0.4×0.6/n]. The probability of a large error shrinks as n grows: this is the law-of-large-numbers idea.',
        'The central limit theorem addresses a different feature: after centering at the target and scaling by the standard error, the sampling distribution approaches the standard normal under suitable conditions. Here the larger-sample distribution becomes more bell-shaped. The data need not themselves be normal, and convergence is not a claim that every successive realized estimate moves closer to the target.')+
        block('A confidence level describes the interval procedure across repeated samples',coverage_figure(),
        'The vertical line is the fixed population mean. Each horizontal interval uses a different independent sample and therefore has a different centre and width. A 95% procedure covers the target in 95% of repetitions under its model; a finite batch need not have exactly 95% coverage. The confidence interval concerns the mean, not a range containing 95% of individual observations. This general illustration does not reveal the retail audit’s known answer.')+
        block('Estimating variability introduces the heavier tails of the t distribution',t_figure(),
        'When normal observations have unknown population SD, replacing that SD by the sample SD introduces additional uncertainty. The statistic (sample mean − population mean)/(s/√n) then follows t with n−1 degrees of freedom. The raw sample mean is not t-distributed. Small degrees of freedom put more probability in the tails, so a fixed confidence level needs a larger critical value.',
        'For 29 degrees of freedom the two-sided 95% multiplier is about 2.045; the standard-normal multiplier is 1.960. The difference narrows as information increases. This is why an interval calculation specifies its reference distribution and degrees of freedom instead of treating two standard errors as a universal rule.'),
        'theory-method','General theory')
    add('test-visuals','Connect error probabilities with a decision rule',
        block('A test decision can be correct or mistaken in two different ways',table(['Decision','Null true','Specified alternative true'],[
        ['Do not reject','Correct non-rejection','Type II error: probability β'],['Reject','Type I error: controlled by α','Detection: power = 1−β']], 'Truth and decision are different dimensions'),
        'The significance level α bounds false rejection under the null model. Power is the rejection probability under a specified alternative. For fixed sample size and variability, demanding stronger evidence usually lowers false positives while raising missed signals. Increasing the number of independent observations can improve detection at the same α. Failing to reject is not proof that the null is true.')+
        block('One-sided and two-sided tests allocate the same error budget differently',rejection_figure(),
        'Choose the alternative before inspecting the estimate. With α=0.05, a right-sided t test with 29 degrees of freedom rejects above 1.699. A two-sided test splits the error budget between two tails and rejects outside ±2.045. A p-value is the null tail area at least as extreme as the observed statistic in the specified direction or directions. Comparing that area with α gives the same decision as comparing the statistic with the appropriate critical value.')+
        block('Power depends on the particular difference the test must detect',power_figure(),
        'This deliberately simple illustration uses a standard-normal statistic under the null and a normal statistic shifted by two standard-error units under the alternative. The cutoff remains fixed at 1.645. The area beyond it is 5% under the null and 63.9% under the alternative; power is the latter area. A larger shift increases power. For a fixed difference in outcome units, reducing SE through a larger sample also increases the standardized shift.',
        'These are illustrative normal curves rather than the audit’s calculated power. In a formal sample-size calculation, specify the smallest important difference, the expected variability, the design, and α. A t-based power calculation uses the corresponding noncentral t distribution.'),
        'theory-practice','General theory')
    add('resampling-visuals','See the draws behind the resampling result',
        block('A bootstrap draw can repeat an observed store',draw_figure(audit.store_id.head(5).tolist()),
        'The diagram uses a five-ID excerpt to make replacement visible. It is not the analysis sample. The full bootstrap selects 30 store records with replacement from all 30 audit records and recalculates the mean. The full subsampling exercise selects 15 distinct records without replacement. Preserve the observation being sampled: drawing product-days separately would implement a different design.')+
        block('The bootstrap histogram places the interval endpoints in the distribution',histogram(boot,'Two thousand bootstrap means summarize repetition within the audit','Bootstrap mean stockout rate (%)',[(np.quantile(boot,.025),'2.5%'),(np.quantile(boot,.975),'97.5%')]),
        f'The standard deviation of these 2,000 means is {boot.std(ddof=1):.3f} percentage points. Their 2.5th and 97.5th percentiles are {np.quantile(boot,.025):.3f}% and {np.quantile(boot,.975):.3f}%. The distribution is over estimates of an average, not over the 30 individual store rates. The next table compares these endpoints with the analytical t interval.',
        'The percentile method reads endpoints directly from the bootstrap distribution. It does not require that distribution to be perfectly symmetric, but coverage still depends on how well resampling represents the estimator’s uncertainty. More repetitions reduce simulation noise; they do not increase the original audit sample.'),
        'resampling','Worked application')
    # Replace the result-only paired block with a complete sequence below.
    sec=next(v for v in c['sections'] if v['id']=='testing');tree=Tree(sec['body']);cursor=0
    for node in tree.root.elements():
        if not node.has('teaching-block'):continue
        count=len(visual_frames(node.find(lambda x:x.has('teaching-visual')),node.attrs['data-presentation-title']))
        if node.attrs['data-presentation-title']=='Check a paired difference directly':
            sec['body']=sec['body'][:node.start]+sec['body'][node.stop:];del c['headlines']['testing'][cursor:cursor+count];break
        cursor+=count
    sec['body']=sec['body'].replace('H₀: mean stockout rate = 10%; H₁: mean stockout rate &gt; 10%', 'H₀: mean stockout rate ≤ 10%; H₁: mean stockout rate &gt; 10%')
    sec['body']=sec['body'].replace('A composite alternative contains a range of possible values; the null value here is specific.', 'The operational null includes all means at or below 10%; its boundary value, 10%, supplies the reference calculation. Equality of a mean is a restriction on that parameter, not a complete specification of every feature of the distribution.')
    sec['body']=sec['body'].replace('A critical-value rule and a p-value rule make the same decision when they use the same test and significance level.', 'At α=0.05 with 29 degrees of freedom, 2.39 exceeds the right-sided cutoff 1.699 and also the two-sided cutoff 2.045. Both p-values are below 0.05, so both rules reject their respective nulls. The reported two-sided 95% interval corresponds to the two-sided test; a right-sided test instead matches a 95% lower confidence bound.')
    pairrows=[[v.store_id,f'{v.stockout_rate_audit:.2f}',f'{v.stockout_rate_system:.2f}',f'{v.difference:.2f}'] for v in paired.head(4).itertuples()]
    add('paired-analysis','Preserve each store’s two measurements',
        block('Matching by store and week defines the paired comparison',table(['Store','Audit (%)','System (%)','Difference (points)'],pairrows,'First four matched stores; difference = audit − system'),
        'Both measurements concern the same store, week 16, and monitoring basket. Join on store ID after selecting the week, retain only valid matched observations, and check one row per store. The subtraction removes the need to compare one collection of stores with a different collection. The 30 differences, rather than 60 unrelated readings, are the analysis observations.')+
        block('The distribution of differences shows disagreement hidden by a small average',histogram(d,'Audit-minus-system differences across the 30 matched stores','Difference (percentage points)',[(0,'Zero')],bins=np.arange(-5,12,2)),
        f'The average difference is {pi["mean"]:.3f} points, while the SD of differences is {pi["sd"]:.3f} points. Positive values mean the audit reports more stockouts; negative values mean the system reports more. Inspect both tails and the observation keys before testing the mean. An average close to zero can coexist with substantial disagreement for individual stores.')+
        block('The paired t-test applies the one-sample formula to the differences',formula(f'SE = {pi["sd"]:.3f}/√30 = {pi["se"]:.3f}; t = {pi["mean"]:.3f}/{pi["se"]:.3f} = {pi["mean"]/pi["se"]:.3f}'),
        f'Use all 30 paired differences and 29 degrees of freedom. The two-sided p-value is {2*t.sf(abs(pi["mean"]/pi["se"]),29):.4f}; the 95% interval is {pi["low"]:.3f} to {pi["high"]:.3f} points. At the 5% level, the test does not detect a nonzero average difference. Calculations use unrounded values.',
        'This conclusion does not establish equivalence or close agreement. To assess equivalence, first define the largest acceptable mean discrepancy and use a procedure designed for that margin. To assess agreement for individual stores, study the dispersion of their differences. Here the practical next step is to inspect the measurement process behind the larger discrepancies.'),
        'act','Worked application')
    rows=[]
    for label,g in [('Urban',paired[paired.urban==1]),('Nonurban',paired[paired.urban==0])]:
        v=g.stockout_rate_audit;rows.append([label,len(v),f'{v.mean():.3f}',f'{v.std(ddof=1):.3f}',f'{v.var(ddof=1)/len(v):.3f}'])
    add('independent-analysis','Compare groups containing different stores',
        block('Independent groups contribute two separate sources of sampling variation',table(['Group','Stores','Mean (%)','SD (points)','s²/n'],rows,'Same audit; variance contributions use different stores'),
        'Urban and nonurban rows belong to different stores. Equal group sizes do not create a pairing. Under the independent-groups approximation, the variance of the difference in means is s₁²/n₁ + s₀²/n₀; its square root is the standard error. Welch’s procedure allows the two population variances to differ. The final column is in squared percentage points.')+
        block('The urban–nonurban interval includes both small and substantial differences',formula(f'Difference = {wi["value"]:.3f}; SE = {wi["se"]:.3f}; t = {wi["value"]/wi["se"]:.3f}; df ≈ {wi["df"]:.2f}'),
        f'The 95% Welch interval is {wi["low"]:.3f} to {wi["high"]:.3f} percentage points, with two-sided p = {2*t.sf(abs(wi["value"]/wi["se"]),wi["df"]):.4f}. The 5% test does not detect a nonzero mean difference. The interval also shows that the sample leaves a fairly wide range of magnitudes unresolved.',
        'This comparison describes the audited groups under the stated sampling approximation. Urban location was not randomly assigned, so the difference does not identify the effect of changing location. Compare the workflow with the paired calculation: the target contrast is similar, but the construction of the standard error follows the relationship between observations.'),
        'act','Worked application')
    add('scope-and-search','Connect the evidence to its intended use',
        block('Precision within an audit and relevance to a new setting are separate questions',bullets('Name the stores, week, measure, and selection process','Check whether the proposed decision concerns the same target','Compare conditions when transferring to another period or setting','Collect bridging evidence when operating conditions change'),
        'The interval describes uncertainty for its specified audit target. Applying the result to a holiday promotion, a new product basket, or stores outside this chain requires evidence that the relevant conditions transfer. The week-16 audit is not a correction to the weeks-1–8 baseline. Make the transfer question explicit once, then gather the information the next decision needs.')+
        block('Searching many tests increases the chance of at least one false alarm',formula('20 independent true-null tests at 5%: P(any false rejection) = 1 − 0.95²⁰ ≈ 64.2%'),
        'This illustration assumes 20 independent tests whose nulls are all true and whose rejection probabilities are exactly 5%. It explains why reporting only the smallest p-value changes the evidential meaning. Dependent tests need not have this exact probability. Name the planned family, retain all results, and distinguish exploratory findings from planned tests.',
        'For family-wise control, a simple Bonferroni rule compares each of m p-values with α/m. For 20 tests and family α=0.05, that cutoff is 0.0025. The appendix explains this rule and the less conservative step-down Holm procedure. Both address a defined family rather than compensating for an undisclosed search.'),
        'act','Worked application')

    extra=[]
    def detail(i,visual,*notes):extra.append(block(DETAIL_TITLES[i],visual,*notes))
    detail(0,formula('Unbiased: E[θ̂ₙ] = θ; consistent: θ̂ₙ → θ in probability; root-n: error scale ∝ n⁻¹ᐟ²'),
        'Unbiasedness concerns the expectation at a given sample size; consistency concerns convergence as sample size increases. The law of large numbers is a convergence result, not the definition of unbiasedness. For independent identically distributed observations with a finite mean, the sample mean is unbiased and obeys the usual LLN. Finite variance additionally gives Var(x̄)=σ²/n. Efficiency compares variances among estimators under specified conditions.')
    detail(1,formula('For iid observations with 0 < σ² < ∞: √n(x̄ − μ)/σ → Normal(0,1) in distribution'),
        'This is the standard independent, identically distributed finite-variance CLT. The notation means convergence of distributions of the standardized error; it does not make each observation normal. The sample mean is exactly normal for every n when the observations themselves are normal. Otherwise the normal approximation can require more observations when distributions are highly skewed or heavy-tailed. Dependence requires a result matched to the dependence structure.')
    detail(2,bullets('Select 30 stores without replacement from 150','Observe a fresh 140-product-day audit for each selected store','Target the equal-store mean expected week-16 stockout rate','Use the stated introductory store-level SE approximation'),
        'The displayed t calculation uses s/√30 and does not apply a finite-population correction. Selection of stores and within-store outcome measurement both contribute variation. For fixed store expected rates, without-replacement selection reduces the between-store component relative to sampling with replacement. Fresh measurement noise remains even if every store is selected. A design-aware refinement separates these components instead of multiplying the entire observed variance by a finite-population factor. The elementary bootstrap reproduces the displayed independent-store approximation.')
    phat=19/30;z=norm.ppf(.975);den=1+z*z/30;centre=(phat+z*z/60)/den;half=z*np.sqrt(phat*(1-phat)/30+z*z/(4*30**2))/den
    detail(3,formula('Wilson centre = (p̂ + z²/(2n))/(1+z²/n); half-width = z√[p̂(1−p̂)/n + z²/(4n²)]/(1+z²/n)'),
        f'For 19 of 30 stores above target, p̂={phat:.5f} and z={z:.5f}. The centre is {centre:.5f}, the half-width is {half:.5f}, and the endpoints are {100*(centre-half):.2f}% and {100*(centre+half):.2f}%. This estimates the share of stores above the target, a different parameter from the mean stockout rate. Like the introductory mean calculation, it uses an independent-Bernoulli sampling approximation.')
    detail(4,formula('dᵢ = auditᵢ − systemᵢ; SE(d̄) = s_d/√n; t = (d̄ − δ₀)/(s_d/√n), df = n−1'),
        'Compute the sample SD from the differences, using n−1. Within-pair dependence is retained by subtracting matched measurements; independence is assumed across the units that supply the differences. A paired t test and a one-sample t test on d agree. The normal-theory reference distribution is exact for independent normal differences; normality of each measurement separately is not the relevant requirement.')
    detail(5,formula('v₁=s₁²/n₁; v₀=s₀²/n₀; SE=√(v₁+v₀); df≈(v₁+v₀)²/[v₁²/(n₁−1)+v₀²/(n₀−1)]'),
        'Use t=[(mean₁−mean₀)−δ₀]/SE and the Welch–Satterthwaite degrees of freedom. The interval is the observed difference ± t₀.₉₇₅,df×SE. The separate pooled-variance procedure assumes a common population variance and uses n₁+n₀−2 degrees of freedom; n₁+n₀−1 is not the pooled formula. SciPy implements Welch with ttest_ind(group1,group0,equal_var=False).')
    detail(6,table(['Test at level α','Matching confidence statement'],[
        ['Two-sided: μ ≠ μ₀','Two-sided 100(1−α)% interval excludes μ₀'],['Right-sided: μ > μ₀','One-sided 100(1−α)% lower bound exceeds μ₀'],['Left-sided: μ < μ₀','One-sided 100(1−α)% upper bound is below μ₀']], 'Use the same model, estimator, standard error, and reference distribution'),
        'A two-sided 95% interval allocates 2.5% to each tail, whereas a 5% right-sided test allocates all 5% to the right tail. Its lower bound uses t₀.₉₅ rather than t₀.₉₇₅. Simple and composite hypotheses refer formally to whether the whole data distribution is specified. An equality restriction on a mean can leave variance as a nuisance parameter; null hypotheses can also be inequalities. The one-sided audit test is calibrated at its boundary μ=10%.')
    detail(7,bullets('Define the family and its total false-rejection target α','Bonferroni: compare each p-value with α/m','Holm: sort p-values; compare p₍ᵢ₎ with α/(m−i+1)','Stop Holm at the first failure; reject only preceding hypotheses'),
        'Bonferroni controls the probability of at least one false rejection using the union bound, and does not require independent tests when individual p-values are valid. Holm applies a sequence of thresholds and also controls family-wise error under arbitrary dependence. These methods do not automatically repair selective reporting from an undefined family. Raising α makes rejection easier and is not a correction for multiple testing.')
    c['appendix_extra']='<section id="inference-details"><h2>Connect sampling, intervals, and test formulas</h2>'+''.join(extra)+'</section>'
    return c
