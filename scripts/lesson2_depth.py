"""Lesson 2 visual reasoning and probability, from the shared store records.

Each block is a single authored slide with paragraph notes. Figures use SVG so
reading, presentation, and print share the same accessible visual content.
"""
from functools import lru_cache
from html import escape
import numpy as np

PROBABILITY_TITLES = [
    'A sample space lists outcomes and an event selects a subset',
    'Discrete probabilities add; continuous densities contribute area',
    'Subtract the intersection when adding event probabilities',
    'Conditioning changes the denominator; independence preserves the probability',
    'Bayes combines a prior probability with new evidence',
    'Expected values and variances weight outcomes by their probabilities',
    'Joint probabilities determine conditional means and covariance',
    'Bernoulli and binomial models describe indicators and counts',
    'Uniform and normal models specify different continuous shapes',
    'Lognormal and Pareto models describe positive right tails',
    'Standardize aligned proxies before constructing a composite score',
    'Principal components summarize variation through data-chosen weights',
]

def figure(title, body, desc, height=340):
    e=escape
    return f'<figure><svg viewBox="0 0 720 {height}" role="img" aria-label="{e(title)}"><title>{e(title)}</title><desc>{e(desc)}</desc>{body}</svg><figcaption>{e(title)}. {e(desc)}</figcaption></figure>'

def text(x,y,label,size=14,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="#183f36">{escape(str(label))}</text>'

@lru_cache(maxsize=1)
def stores():
    from retail_case import world
    return world()['stores']

def histogram_pair(y):
    body=''
    for j,width in enumerate([2,4]):
        left=55+350*j; edges=np.arange(4,24+width,width)
        counts,_=np.histogram(y,edges); shares=100*counts/len(y)
        body+=text(left,24,f'Bin width: {width} points',16)
        for tick in [0,20,40,60]:
            yy=250-3.2*tick
            body+=f'<line x1="{left}" x2="{left+280}" y1="{yy}" y2="{yy}" stroke="#d5ddd4"/>'+text(left-5,yy+4,tick,12,'end')
        for lo,share in zip(edges[:-1],shares):
            xx=left+(lo-4)*14; hh=share*3.2
            body+=f'<rect x="{xx+1}" y="{250-hh}" width="{width*14-2}" height="{hh}" fill="#276451"/>'
        for tick in [4,8,12,16,20,24]:body+=text(left+(tick-4)*14,273,tick,12,'middle')
    body+=text(55,50,'Stores (%)',13)+text(405,50,'Stores (%)',13)+text(360,316,'Baseline stockout rate (%)',15,'middle')
    return figure('Both bin widths locate the same central concentration',body,'The same 150 stores, common 4–24% horizontal range and 0–60% vertical scale. Each bar is a within-bin share.')

def group_boxes(s):
    body='';sx=lambda v:170+24*v
    for j,(name,g) in enumerate(s.groupby('risk_group')):
        y=g.baseline_rate.to_numpy();q1,med,q3=np.quantile(y,[.25,.5,.75]);iqr=q3-q1
        low=min(y[y>=q1-1.5*iqr]);high=max(y[y<=q3+1.5*iqr]);yy=90+110*j
        body+=text(10,yy-8,name,14)+text(10,yy+14,f'n = {len(y)}',13)
        body+=f'<line x1="{sx(low)}" x2="{sx(high)}" y1="{yy}" y2="{yy}" stroke="#276451" stroke-width="2"/>'
        for v in [low,high]:body+=f'<line x1="{sx(v)}" x2="{sx(v)}" y1="{yy-10}" y2="{yy+10}" stroke="#276451"/>'
        body+=f'<rect x="{sx(q1)}" y="{yy-23}" width="{sx(q3)-sx(q1)}" height="46" fill="#e4eedc" stroke="#276451"/><line x1="{sx(med)}" x2="{sx(med)}" y1="{yy-23}" y2="{yy+23}" stroke="#9b421e" stroke-width="3"/>'
        for v in y[(y<q1-1.5*iqr)|(y>q3+1.5*iqr)]:body+=f'<circle cx="{sx(v)}" cy="{yy}" r="3" fill="#9b421e"/>'
    for tick in [0,5,10,15,20]:body+=text(sx(tick),277,tick,13,'middle')
    body+=text(410,315,'Baseline stockout rate (%)',15,'middle')
    return figure('The delivery groups overlap despite different centres',body,'Boxes mark quartiles and medians; whiskers end at observed values within 1.5 IQR. Isolated dots mark values outside the fences.')

def composition(s):
    body=''; colors=['#276451','#97b9a3','#b65b32']
    for j,(name,g) in enumerate(s.groupby('risk_group')):
        counts=[int((g.baseline_rate<=10).sum()),int(((g.baseline_rate>10)&(g.baseline_rate<=15)).sum()),int((g.baseline_rate>15).sum())]
        xx=170;yy=65+90*j;body+=text(5,yy+16,name)+text(5,yy+36,f'n = {len(g)}')
        for count,color in zip(counts,colors):
            share=100*count/len(g);ww=share*5
            body+=f'<rect x="{xx}" y="{yy}" width="{ww}" height="48" fill="{color}"/>'+text(xx+ww/2,yy+72,f'{share:.1f}%',12,'middle');xx+=ww
    for j,label in enumerate(['At/below 10%','Above 10–15%','Above 15%']):
        xx=30+230*j;body+=f'<rect x="{xx}" y="280" width="16" height="16" fill="{colors[j]}"/>'+text(xx+24,294,label)
    return figure('Within-group percentages reveal the heavier high-stockout share',body,'Each bar represents 100% of its delivery group. Labels report shares; the adjoining table supplies exact values.',330)

def gallery():
    x=np.arange(-3,4,dtype=float)
    examples=[('Perfect positive',x),('Perfect negative',-x),('Positive, dispersed',x+np.array([1,-2,1,0,1,-2,1])),('Zero, curved',x*x)]
    body=''
    for j,(label,y) in enumerate(examples):
        xx=25+(j%2)*350;yy=15+(j//2)*175
        corr=np.corrcoef(x,y)[0,1];body+=text(xx,yy+14,f'{label}: r = {corr:.2f}',15)
        body+=f'<path d="M {xx+25} {yy+40} V {yy+135} H {xx+290}" fill="none" stroke="#8c9c8e"/>'
        for a,b in zip(x,y):
            cx=xx+45+(a+3)*37;cy=yy+125-80*(b-min(y))/(max(y)-min(y))
            body+=f'<circle cx="{cx}" cy="{cy}" r="5" fill="#276451"/>'
        body+=text(xx+285,yy+153,'X',12)+text(xx+8,yy+40,'Y',12)
    return figure('Correlation measures linear pattern, not every relationship',body,'Illustrative coordinates, not store data. A U-shaped relationship has zero correlation in this symmetric example.',385)

def restore(c):
    from retail_ui import table,formula,section,scatter_figure
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    s=stores();y=s.baseline_rate.to_numpy();x=s.baseline_demand.to_numpy()
    def block(title,visual,*notes):return teach(title,visual,list(notes))
    def add(key,heading,body,before,phase):
        item=dict(**section(key,heading,body),phase=phase)
        c['sections'].insert(next(i for i,v in enumerate(c['sections']) if v['id']==before),item)
        c['headlines'][key]=[title for title,_ in visual_frames(Tree(body).root,heading)]

    add('theory-visual','Read and design a statistical display',
        block('Purpose, encoding, scales, and annotation make a graph readable',bullets('Purpose: name the comparison the reader should make','Encoding: use position, length, or area consistently','Scaffolding: label axes, units, scope, and denominators','Annotation: identify the pattern that answers the question'),
        'Choose the question before the chart. A histogram describes one numerical distribution; grouped boxes compare distributions; a scatterplot compares paired numerical values; a 100% stacked bar compares category shares. Use a table for precise values and a graph for patterns. Common scales support comparisons across panels. Labels and annotations should explain the relevant feature without obscuring the observations.')+
        block('Frequency, relative frequency, and density use different vertical scales',formula('Count = nⱼ; share = nⱼ/n; density = nⱼ/(n × bin width)'),
        'Absolute frequency counts observations in a bin. Relative frequency divides by the total count. Histogram density additionally divides by bin width, so bar area gives the share and the total area is one. With unequal widths, compare areas rather than treating heights as probabilities. A smoothed density uses the same area interpretation. For example, 30 of 150 stores in a two-point interval give a share of 0.20 and a density of 0.10 per percentage point.')+
        block('Mode, percentile range, and relative spread answer additional questions',table(['Summary','Definition','Use'],[
        ['Mode','Most frequent value or category','Identify the most common outcome'],['P90 − P10','90th minus 10th percentile','Spread of the central 80%'],['Coefficient of variation','SD / mean','Spread relative to a positive ratio-scale mean']], 'Three complementary summaries'),
        'A dataset can have several equally frequent modes. For near-continuous measurements, an exact-value mode is sensitive to rounding; a modal histogram interval also depends on the bins. P90 minus P10 omits both outer tails. The coefficient of variation is dimensionless, but its interpretation needs a meaningful zero and a positive mean away from zero. It suits relative variation in quantities such as demand; it is not meaningful for arbitrary temperature origins.'),
        'theory-method','General theory')
    add('theory-covariance','Build association from paired deviations',
        block('Covariance averages products of deviations from the two means',formula('sₓᵧ = Σ(xᵢ − x̄)(yᵢ − ȳ)/(n − 1); r = sₓᵧ/(sₓsᵧ)'),
        'A pair above both means or below both means has a positive product. A pair on opposite sides has a negative product. Adding those signed contributions describes whether the variables move together. Covariance uses the product of the original units; dividing by both standard deviations yields a unit-free correlation.',
        'Here the sample covariance and both sample variances use n−1. A descriptive population convention uses n in all three quantities. Either consistent convention gives the same correlation because the factors cancel. Correlation requires nonzero variation in both variables.')+
        block('Linear association can be strong, weak, or absent in a curved pattern',gallery(),
        'Read the direction and dispersion together. All points on an increasing straight line give r = 1; a decreasing straight line gives r = −1. Dispersed points can retain positive co-movement. In the final illustrative panel, Y equals X squared at symmetric X values, so the signed products cancel even though knowing X determines Y. Inspect the scatterplot before interpreting a small correlation.')+
        block('A pooled correlation and a within-group correlation describe different comparisons',bullets('Pooled: compare every observation with the overall means','Within-group: recalculate means and spread inside each group','Report the group definition and observation count','Interpret differences through group mix and operating conditions'),
        'The pooled coefficient includes both between-group and within-group co-movement. A subgroup coefficient centers and scales using that subgroup. It can therefore differ in sign or magnitude from the pooled value, and is not obtained by simply averaging subgroup correlations. Restricted ranges and small groups also change the comparison. Use the observed pattern to choose the next descriptive question; a causal explanation requires a separate design.'),
        'read-data','General theory')

    add('bin-widths','Compare two views of the same stores',block('Changing bin width changes detail while preserving the broad concentration',histogram_pair(y),
        'Both panels contain all 150 store averages for weeks 1–8. The horizontal range and vertical percentage scale are identical. Two-point bins show finer local detail; four-point bins merge adjacent intervals and therefore have larger shares. The broad concentration persists. A local bump that appears under one width is a reason to inspect the rows, rather than an established new segment.'),
        'distributions','Worked application')
    summaries=[]
    for name,g in s.groupby('risk_group'):
        q=np.quantile(g.baseline_rate,[.25,.5,.75])
        summaries.append([name,len(g),f'{g.baseline_rate.mean():.2f}',f'{q[1]:.2f}',f'{g.baseline_rate.std(ddof=1):.2f}',f'{q[2]-q[0]:.2f}'])
    add('group-distributions','Compare full distributions before prioritizing groups',
        block('Long-lead stores have a higher centre with overlapping store outcomes',group_boxes(s),
        'The boxes share a single stockout-rate axis and use one store as the observation. Compare the median lines first, then the quartiles, whiskers, and individual outliers. The long-lead group is shifted upward, but the overlap means delivery group does not determine an individual store’s performance. This supports prioritizing review while still inspecting each store.')+
        block('Group spread shows how representative each group average is',table(['Delivery group','n','Mean','Median','SD','IQR'],summaries,'Store-level baseline rates; all summaries in percentage points except n'),
        'Calculate every summary separately within the named group, using the same eight-week baseline and measurement rule. The mean locates the average; SD and IQR report variation around and within the distribution. Read these values with the boxes rather than ranking groups solely by their means. The counts show how much of the chain each comparison represents.'),
        'calculate','Worked application')
    add('raw-association','Inspect individual stores before averaging',
        block('Individual stores vary substantially around the demand relationship',scatter_figure(x,y,'Baseline demand and stockouts across all stores','Baseline demand index','Baseline stockout rate (%)'),
        'Each dot joins a store’s average demand to its average stockout rate over weeks 1–8. The upward tendency coexists with substantial variation at similar demand. Follow this with the five-bin display: sorting by demand, forming equal-count groups, and averaging produces a clearer broad pattern while hiding the within-bin spread. Both plots use the same stores; the five averages are not five new observations.'),
        'association','Worked application')
    # Add a chart directly after its existing composition table, retaining the
    # exact original title map for the remaining authored application blocks.
    a=next(v for v in c['sections'] if v['id']=='association')
    tree=Tree(a['body']);first=tree.root.elements()[0]
    title='A stacked bar makes the within-group composition visible'
    extra=block(title,composition(s),'The table first counts stores in each ordered stockout band, divides each count by its own delivery-group total, and multiplies by 100. The chart displays those percentages as adjacent segments. Keep the category order and colours consistent across groups. Equal bar lengths compare composition; group counts remain visible beside the bars.')
    a['body']=a['body'][:first.stop]+extra+a['body'][first.stop:]
    c['headlines']['association'].insert(1,title)
    dx=x-x.mean();dy=y-y.mean();products=dx*dy;cov=products.sum()/(len(s)-1);corr=np.corrcoef(x,y)[0,1]
    rows=[[s.iloc[i].store_id,f'{dx[i]:.3f}',f'{dy[i]:.3f}',f'{products[i]:.3f}'] for i in range(4)]
    subgroup=[['All stores',len(s),f'{corr:.3f}']]+[[name,len(g),f'{g.baseline_demand.corr(g.baseline_rate):.3f}'] for name,g in s.groupby('risk_group')]
    add('worked-covariance','Reconstruct the association from the shared rows',
        block('Each store contributes a signed product to the covariance',table(['Store','Demand − mean','Rate − mean','Product'],rows,'First four stores; products use unrounded deviations'),
        f'The full-store means are demand {x.mean():.3f} and rate {y.mean():.3f}%. Subtract those means for every store. Multiply the two deviations in each row. Positive contributions place a store on the same side of both means; negative contributions place it on opposite sides. These four rows illustrate the calculation; the total on the next slide includes all {len(s)} stores.')+
        block('The full-store product sum yields a positive but dispersed association',formula(f'Covariance = {products.sum():.3f} / 149 = {cov:.3f}; r = {cov:.3f} / ({x.std(ddof=1):.3f} × {y.std(ddof=1):.3f}) = {corr:.3f}'),
        'Use all 150 centered products, divide by 149 for sample covariance, and divide again by both sample standard deviations for correlation. Calculations use unrounded values. Covariance is in demand-index units times percentage points; correlation is unit-free. The resulting moderate positive association matches the upward but dispersed individual-store scatter.')+
        block('Within-group correlations retain their own counts and comparison scope',table(['Comparison','Stores','Demand–rate correlation'],subgroup,'Pearson correlations recalculated within each delivery group'),
        'For each row, recalculate the mean demand, mean rate, covariance, and standard deviations using only that row’s stores. Compare these coefficients with the all-store value. They describe association within the delivery categories rather than the full mixture. Use both perspectives when identifying operating questions for regression in later lessons; the coefficients do not measure the effect of changing demand.'),
        'act','Worked application')

    probability=[]
    def prob(i,visual,*notes):probability.append(block(PROBABILITY_TITLES[i],visual,*notes))
    prob(0,bullets('Outcome ω: one possible result','Sample space Ω: all possible results','Event A: a set of outcomes','P(Ω) = 1; P(Aᶜ) = 1 − P(A)'),
        'For a product-day availability check, the sample space can be {available, unavailable}. The stockout event selects unavailable. A random variable maps each outcome to a number: X equals one for unavailable and zero otherwise. Distinguish the outcome, the event, and the numerical variable before assigning probabilities.')
    prob(1,bullets('Discrete: finitely many or countably infinite possible values','Probability mass: p(x) ≥ 0 and Σp(x) = 1','Continuous density: f(x) ≥ 0 and ∫f(x)dx = 1','P(a ≤ X ≤ b) = ∫ₐᵇ f(x)dx for a continuous variable'),
        'A count can have infinitely many possible integer values and remain discrete. For an absolutely continuous model, interval probabilities are areas and any single point has probability zero. A density height can exceed one because the area, not the height, is the probability. Empirical frequencies describe observed rows; a probability model describes possible repetitions.')
    prob(2,formula('P(A ∪ B) = P(A) + P(B) − P(A ∩ B)'),
        'The union means A or B or both, and the intersection means both. Adding event probabilities counts the intersection twice, so subtract it once. Mutually exclusive events have an empty intersection and therefore zero overlap. For example, mutually exclusive stockout bands form a partition of stores whose shares add to one.')
    prob(3,formula('P(A | B) = P(A ∩ B)/P(B); independence: P(A ∩ B) = P(A)P(B)'),
        'Conditional probability uses B as the restricted denominator, provided P(B)>0. Under independence, learning B leaves P(A) unchanged. Mutually exclusive events with positive probabilities cannot be independent: observing one makes the other impossible. Independence permits simultaneous occurrence with a product probability.')
    prob(4,formula('P(A | B) = P(B | A)P(A) / [P(B | A)P(A) + P(B | Aᶜ)P(Aᶜ)]'),
        'Bayes reverses the direction of conditioning by combining a prior with likelihoods. Illustrative planning example: suppose 20% of stores are high risk; a flag appears for 80% of high-risk stores and 10% of other stores. Among 100 stores, expect 16 flagged high-risk and 8 flagged others. The high-risk share among flagged stores is 16/(16+8)=2/3. These probabilities illustrate Bayes and are not fitted results from the case. The denominator must be positive.')
    prob(5,formula('μ = E[X] = Σₓ x p(x); Var(X) = Σₓ (x − μ)²p(x); SD(X) = √Var(X)'),
        'For an illustrative count with values 0, 1, and 2 and probabilities 0.5, 0.3, and 0.2, the expectation is 0.7. The weighted squared deviations are 0.5×0.49 + 0.3×0.09 + 0.2×1.69 = 0.61, so SD is about 0.781. These are population probability moments and use no n−1 correction. Continuous models replace the sums by integrals when the moments exist.')
    prob(6,formula('E[Y | X=x] = Σᵧ y p(y | x); Cov(X,Y) = ΣₓΣᵧ (x−μₓ)(y−μᵧ)p(x,y)'),
        'A joint distribution assigns probability to pairs. Divide p(x,y) by p(x)>0 to get p(y|x), then average Y using those conditional probabilities. Covariance weights paired deviations by the joint probabilities. The empirical calculation gives every observed pair equal weight; the sample version additionally uses the n−1 normalization. For continuous pairs, use joint and conditional densities and integrals.')
    prob(7,table(['Model','Support and probability','Mean; variance'],[
        ['Bernoulli(p)','0 or 1; P(X=1)=p','p; p(1−p)'],['Binomial(n,p)','k=0,…,n; C(n,k)pᵏ(1−p)ⁿ⁻ᵏ','np; np(1−p)']], 'Indicator and count models'),
        'A Bernoulli model describes one binary opportunity with 0≤p≤1. A binomial model sums n independent Bernoulli opportunities with the same p; n is a nonnegative integer. C(n,k)=n!/[k!(n−k)!] counts the arrangements with k successes. A stockout count fits this model only when the specified opportunity structure matches those assumptions; the formulas explain the model itself.')
    prob(8,table(['Model','Parameters and support','Mean; variance'],[
        ['Uniform(a,b)','a<b; a≤x≤b; density 1/(b−a)','(a+b)/2; (b−a)²/12'],['Normal(μ,σ²)','σ>0; all real x','μ; σ²']], 'Continuous distributions and their parameters'),
        'Uniform density is flat on a bounded interval: intervals of equal length have equal probability. Normal density is symmetric and bell-shaped, with location μ and scale σ. Its density is exp(−(x−μ)²/(2σ²))/(σ√(2π)). Standard deviation is the square root of each listed variance. Specify support along with the shape to decide whether the model can describe the variable.')
    prob(9,table(['Model','Support and definition','Mean; variance'],[
        ['Lognormal(μ,σ²)','x>0; log X ~ Normal(μ,σ²)','exp(μ+σ²/2); (exp(σ²)−1)exp(2μ+σ²)'],['Pareto(xₘ,α)','x≥xₘ>0; α>0; F(x)=1−(xₘ/x)ᵅ','αxₘ/(α−1); αxₘ²/[(α−1)²(α−2)]']], 'Positive distributions; Pareto moments require α>1 and α>2 respectively'),
        'The lognormal parameters describe log X, not the level mean and SD. The Pareto formula uses scale xₘ and shape α consistently: its mean is finite only for α>1 and its variance only for α>2. Its survival probability (xₘ/x)^α illustrates a power-law tail. Take the square root of variance for SD. This corrects the mixed Pareto parameterization in the original slides.')
    prob(10,formula('zᵢⱼ = (proxyᵢⱼ − meanⱼ)/SDⱼ; compositeᵢ = Σⱼ wⱼzᵢⱼ, with Σⱼwⱼ = 1'),
        'A latent concept, such as operating capability, is not directly observed. A proxy is a recorded indicator intended to measure part of it. Choose one defensible proxy or combine several. For a composite, align directions so larger scores always mean the same thing, standardize measures on a stated reference sample, and declare the weights. A zero-variance proxy cannot be standardized. A common 1–5 scorecard can instead average aligned items on their existing common scale.',
        'Illustrative example: a standardized replenishment-discipline score of 1 and a standardized record-accuracy score of −0.5 give an equal-weight composite of 0.25. The index makes a measurement choice explicit; it does not establish that the latent concept has been measured without error.')
    prob(11,bullets('Start with aligned, usually standardized indicators','The first component maximizes variance of a linear combination','Later components summarize remaining orthogonal directions','Inspect loadings and give the resulting score a substantive meaning'),
        'Principal component analysis (PCA) chooses weights from the indicator covariance or correlation matrix. The first loading vector has unit length and maximizes the variance of the resulting score. Later components are orthogonal and capture remaining variation. PCA weights need not be positive or sum to one, and their overall sign is arbitrary. It is an optional way to reduce dimension, not a guarantee that the largest-variance direction is the business concept of interest.')
    c['appendix_extra']='<section id="probability"><h2>Probability and measurement extend the descriptive toolkit</h2>'+''.join(probability)+'</section>'
    return c
