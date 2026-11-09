"""Build wholly original synthetic Lessons 1–3. All numbers come from executed labs."""
import json
from pathlib import Path
from course_common import render_lesson, table, bars, line_chart, write_lab, esc
ROOT=Path(__file__).resolve().parents[1]

def p(s): return '<p>'+s+'</p>'
def formula(s): return '<div class="formula">'+s+'</div>'
def ul(*items): return '<ul>'+''.join('<li>'+x+'</li>' for x in items)+'</ul>'
def sec(id,title,body,check,answer): return dict(id=id,title=title,body=body,check=check,answer=p(answer))
def fmt(x,n=2): return f'{x:,.{n}f}'
def histogram(edges,values,title,ylabel='Count'):
    lo,hi=min(edges),max(edges); top=max(values)*1.1 or 1
    svg=f'<svg viewBox="0 0 720 340" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>Adjacent rectangles have their actual bin widths. Exact values are in the following table.</desc>'
    for i in range(5):
        y=270-i*60; v=top*i/4
        svg+=f'<line x1="70" y1="{y}" x2="680" y2="{y}" stroke="#d4ddd4"/><text x="62" y="{y+4}" text-anchor="end" font-size="13">{v:.3g}</text>'
    for a,b,v in zip(edges[:-1],edges[1:],values):
        x=70+(a-lo)/(hi-lo)*610; w=(b-a)/(hi-lo)*610; h=v/top*240
        svg+=f'<rect x="{x:.2f}" y="{270-h:.2f}" width="{w:.2f}" height="{h:.2f}" fill="#276451" stroke="white"/>'
    # Label fewer edges in dense histograms; preserve all bin values in the table.
    stride=2 if len(values)>8 else 1
    tick_indices=list(range(0,len(values),stride))
    if stride>1 and len(values)-tick_indices[-1]<stride: tick_indices.pop()
    tick_indices.append(len(values))
    for i in tick_indices:
        x=70+(edges[i]-lo)/(hi-lo)*610
        anchor='start' if i==0 else 'end' if i==len(values) else 'middle'
        svg+=f'<text x="{x:.2f}" y="292" text-anchor="{anchor}" font-size="12">{edges[i]:.3g}</text>'
    svg+=f'<text x="70" y="324" font-size="14">{esc(ylabel)} · Synthetic teaching data</text></svg>' 
    rows=[[f'[{a:g}, {b:g}{"]" if i==len(values)-1 else ")"}',fmt(v,6)] for i,(a,b,v) in enumerate(zip(edges[:-1],edges[1:],values))]
    return '<figure>'+svg+'<figcaption>'+esc(title)+'</figcaption></figure>'+table(['Bin',ylabel],rows,title+' — chart data')
def scatter(points,title,xlabel,ylabel):
    xs=[r[0] for r in points]; ys=[r[1] for r in points]; xmin,xmax=min(xs),max(xs); ymin,ymax=min(ys),max(ys); dx=xmax-xmin or 1; dy=ymax-ymin or 1
    svg=f'<svg viewBox="0 0 720 350" role="img" aria-label="{esc(title)}"><title>{esc(title)}</title><desc>Each dot is one synthetic paired observation; exact values follow.</desc>'
    for i in range(5):
        xx=70+i*150; yy=270-i*60
        svg+=f'<text x="{xx}" y="295" text-anchor="middle" font-size="13">{xmin+dx*i/4:.3g}</text><text x="60" y="{yy+4}" text-anchor="end" font-size="13">{ymin+dy*i/4:.3g}</text><line x1="70" y1="{yy}" x2="670" y2="{yy}" stroke="#d4ddd4"/>'
    for x,y in points: svg+=f'<circle cx="{70+(x-xmin)/dx*600:.2f}" cy="{270-(y-ymin)/dy*240:.2f}" r="4" fill="#276451" opacity="0.68"/>'
    svg+=f'<text x="370" y="330" text-anchor="middle">{esc(xlabel)}</text></svg>'
    return '<figure>'+svg+'<figcaption>'+esc(title)+'. Vertical axis: '+esc(ylabel)+'.</figcaption></figure><details><summary>Exact plotted synthetic observations</summary>'+table([xlabel,ylabel],[[fmt(x,5),fmt(y,5)] for x,y in points],title+' — chart data')+'</details>'

LAB1=r'''"""Original synthetic lab: data preparation. No network or external files.
Seed 41021. Invented lodgings, towns, teams and managers. Currency is fictional CU.
Prices, fixture scores and service totals are authored simulation assumptions,
not fitted to external observations. Python 3 with numpy and pandas.
"""
import json
import numpy as np
import pandas as pd
rng=np.random.default_rng(41021)
# 1. Define a row: a two-night quote for one lodging on one arrival date.
# The latent base price is uniform 65..155 CU; quote noise has SD 9 CU.
records=[]
for i in range(30):
    base=rng.uniform(65,155)
    for date in ['2030-04-10','2030-04-17']:
        records.append(dict(lodging_id=f'L{i+1:03d}',arrival=date,
          town=['Willow Bay','Cedar Reach','Juniper Vale'][i%3],
          kind='Hotel' if i%5 else 'Guesthouse',
          room='Private' if i%7 else 'Shared',
          nightly_cu=round(max(1,base+rng.normal(0,9)),2),
          cleaning_cu=float([0,12,24][i%3]),tax_rate=.08,
          refundable=bool(i%2),rating=[2,3,4,5][i%4]))
raw=pd.DataFrame(records)
raw.loc[9,'nightly_cu']=np.nan
raw.loc[22,'nightly_cu']=np.nan
raw.loc[35,'nightly_cu']=-15.0
raw=pd.concat([raw,raw.iloc[[4]]],ignore_index=True) # known ingestion duplicate
# Keep defects visible: exact duplicates can be removed, but no price is imputed.
unique=raw.drop_duplicates().copy()
invalid=unique.nightly_cu.le(0)
unique.loc[invalid,'nightly_cu']=np.nan
scoped=unique.loc[unique.kind.eq('Hotel') & unique.room.eq('Private')].copy()
complete=scoped.dropna(subset=['nightly_cu']).copy()
complete['two_night_total_cu']=(2*complete.nightly_cu+complete.cleaning_cu)*1.08
assert not unique.duplicated(['lodging_id','arrival']).any()
# 2. Key-safe feature join: one dimension row per lodging, many quotes per lodging.
features=pd.DataFrame({'lodging_id':[f'L{i+1:03d}' for i in range(30)],
                       'walk_minutes':rng.integers(4,31,30)})
joined=complete.merge(features,on='lodging_id',validate='many_to_one',indicator=True)
assert joined._merge.eq('both').all() and len(joined)==len(complete)
bad_features=pd.concat([features,features.iloc[[1]]],ignore_index=True)
bad_join=complete.merge(bad_features,on='lodging_id',how='left')
# 3. Wide/long layouts: the missing Juniper-Q3 cell means unrecorded, not zero.
service=pd.DataFrame({'town':['Willow Bay','Cedar Reach','Juniper Vale'],
                     'Q1':rng.integers(70,130,3),'Q2':rng.integers(70,130,3),
                     'Q3':[int(rng.integers(70,130)),int(rng.integers(70,130)),np.nan]})
long=service.melt(id_vars='town',var_name='quarter',value_name='requests')
assert not long.duplicated(['town','quarter']).any()
wide=long.pivot(index='town',columns='quarter',values='requests')
# 4. Fixtures are events. Turn each into two team-level observations before grouping.
# Draw goals independently with Poisson mean 1.4. No real fixture is represented.
teams=['Aster','Bracken','Clover','Dahlia']
fixtures=[]
for week in range(12):
    pairs=[(0,1),(2,3)] if week%3==0 else ([(0,2),(1,3)] if week%3==1 else [(0,3),(1,2)])
    for a,b in pairs:
        ga,gb=map(int,rng.poisson(1.4,2))
        fixtures.append(dict(date=(pd.Timestamp('2030-01-05')+pd.Timedelta(days=7*week)).strftime('%Y-%m-%d'),home=teams[a],away=teams[b],hg=ga,ag=gb))
fixtures=pd.DataFrame(fixtures)
team_rows=[]
for j,r in fixtures.iterrows():
    for team,goals,against in [(r.home,r.hg,r.ag),(r.away,r.ag,r.hg)]:
        team_rows.append(dict(fixture_id=f'F{j+1:02d}',date=r.date,team=team,
                              points=3 if goals>against else 1 if goals==against else 0))
games=pd.DataFrame(team_rows)
# Half-open tenures [start,end): the new manager owns the boundary date.
tenures=[]
for i,team in enumerate(teams):
    tenures.extend([dict(team=team,manager=f'{team} North',start='2030-01-01',end='2030-02-16'),
                    dict(team=team,manager=f'{team} South',start='2030-02-16',end='2031-01-01')])
tenures=pd.DataFrame(tenures)
candidates=games.merge(tenures,on='team')
assigned=candidates.loc[(candidates.date>=candidates.start)&(candidates.date<candidates.end)].copy()
assert len(assigned)==len(games) and not assigned.duplicated(['fixture_id','team']).any()
summary=assigned.groupby(['team','manager']).agg(games=('points','size'),observed=('points','count'),total=('points','sum'),ppg=('points','mean')).reset_index()
# Weighted and unweighted summaries differ when groups have unequal exposure.
summary=summary.sort_values(['ppg','manager'],ascending=[False,True])
# A deliberately unbalanced toy comparison makes denominator logic transparent.
toy_n=np.array([2,8]);toy_total=np.array([6,8]);toy_means=toy_total/toy_n

def clean_records(df): return json.loads(df.to_json(orient='records'))
out={'seed':41021,'synthetic':True,
 'assumptions':['Fictional currency CU','Two nights, one room, tax applied to room plus cleaning','Poisson fixture goals with mean 1.4','No empirical calibration'],
 'quality':{'raw':len(raw),'deduplicated':len(unique),'duplicates_removed':len(raw)-len(unique),'initial_missing':int(raw.nightly_cu.isna().sum()),'invalid_nonpositive':int(invalid.sum()),'scoped':len(scoped),'complete':len(complete),'excluded_missing_in_scope':len(scoped)-len(complete),'unsafe_join_rows':len(bad_join),'safe_join_rows':len(joined)},
 'raw_excerpt':clean_records(raw.iloc[[1,4,9,22,35,60]]),
 'offers':clean_records(joined.drop(columns='_merge').sort_values('two_night_total_cu').head(6)),
 'town_summary':clean_records(complete.groupby('town').agg(n=('two_night_total_cu','size'),mean=('two_night_total_cu','mean'),median=('two_night_total_cu','median')).reset_index()),
 'service_wide':clean_records(service),'service_long':clean_records(long),
 'trace':int(service.loc[service.town.eq('Willow Bay'),'Q2'].iloc[0]),
 'fixtures':clean_records(fixtures.head(2)),'assigned_excerpt':clean_records(assigned[(assigned.team=='Aster') & assigned.date.isin(['2030-02-09','2030-02-16'])][['fixture_id','date','team','manager','points']]),
 'fixtures_n':len(fixtures),'team_rows_n':len(games),'candidate_rows_n':len(candidates),
 'manager_summary':clean_records(summary),'eligible':clean_records(summary.loc[summary.games.ge(6)]),
 'toy':{'n':toy_n.tolist(),'totals':toy_total.tolist(),'means':toy_means.tolist(),'weighted':float(toy_total.sum()/toy_n.sum()),'unweighted':float(toy_means.mean())}}
print(json.dumps(out,allow_nan=False))
'''

LAB2=r'''"""Original synthetic distribution and association lab. Seed 42022.
Fictional towns, quotes and firms; currency is CU. Authored parameters are not
estimates from external observations. Dependencies: numpy, pandas, scipy.
No files or network are required. All exported numbers are computed below.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats
rng=np.random.default_rng(42022)
# 1. Unequal-size, positive, right-skewed quote groups. This is a model assumption.
rows=[]
for town,n,median,sigma in [('Willow Bay',180,105,.30),('Cedar Reach',110,135,.36),('Juniper Vale',70,120,.26)]:
    price=np.round(rng.lognormal(np.log(median),sigma,n),2)
    refund=rng.random(n)<.60
    for v,r in zip(price,refund): rows.append((town,float(v),bool(r)))
df=pd.DataFrame(rows,columns=['town','price_cu','refundable'])
x=df.price_cu.to_numpy();n=len(x);cap=140.
# Histogram counts and density: the latter integrates to one across all bins.
upper=float(np.ceil(x.max()/50)*50)
edges=np.unique(np.r_[0.,80.,120.,180.,upper])
counts,_=np.histogram(x,bins=edges)
density=counts/(n*np.diff(edges))
assert np.isclose(np.sum(density*np.diff(edges)),1)
fine_edges=np.linspace(0,upper,13);fine_counts,_=np.histogram(x,fine_edges)
coarse_edges=np.linspace(0,upper,7);coarse_counts,_=np.histogram(x,coarse_edges)
q=np.quantile(x,[.25,.5,.75]);iqr=q[2]-q[0];fences=[q[0]-1.5*iqr,q[2]+1.5*iqr]
inside=x[(x>=fences[0])&(x<=fences[1])]
kgrid=np.linspace(0,upper,25)
kde=stats.gaussian_kde(x)
# Explicit five-point arithmetic example: change only one observation.
toy=np.array([50.,60.,70.,80.,90.]);toy_shift=toy.copy();toy_shift[-1]=250.
# Group summaries include denominators, not raw count comparisons alone.
groups=[]
for town,g in df.groupby('town',sort=False):
    z=g.price_cu.to_numpy()
    groups.append(dict(town=town,n=len(z),mean=float(z.mean()),median=float(np.median(z)),q1=float(np.quantile(z,.25)),q3=float(np.quantile(z,.75)),under=int((z<=cap).sum()),proportion=float((z<=cap).mean())))
# 2. Events, conditional probabilities and Bayes: all from the same table.
under=x<=cap;refund=df.refundable.to_numpy()
a=int((under&refund).sum());b=int((~under&refund).sum());c=int((under&~refund).sum());d=int((~under&~refund).sum())
# Known probability model for net reward, distinct from observed sample frequencies.
reward=np.array([-4.,6.,18.]);prob=np.array([.55,.30,.15]);expected=float(reward@prob)
variance=float(((reward-expected)**2)@prob)
model_k=np.arange(11);binom=stats.binom.pmf(model_k,10,.25)
# Fixed model calculations illustrate support and tail assumptions.
models={'binom_p_ge_4':float(stats.binom.sf(3,10,.25)),
        'poisson_p_zero':float(stats.poisson.pmf(0,2)),
        'exp_p_gt_10':float(stats.expon.sf(10,scale=5)),
        'normal_within_1sd':float(stats.norm.cdf(1)-stats.norm.cdf(-1)),
        'lognormal_median':float(np.exp(4.7)),
        'lognormal_mean':float(np.exp(4.7+.5*.4**2)),
        'pareto_mean_alpha_15':float(1.5*50/(1.5-1)),
        'pareto_tail_200':float((50/200)**1.5)}
# 3. A separate firm case. The latent trait is deliberately unobserved to an analyst.
# It drives both size and a noisy score: association is built in, not estimated
# from real management data. This simulation does not prove score interventions work.
N=240;latent=rng.normal(0,1,N);sector=rng.integers(0,3,N)
score=np.clip(3+.65*latent+rng.normal(0,.40,N),1,5)
employees=np.maximum(1,np.round(np.exp(3.6+.45*latent+.20*sector+rng.normal(0,.55,N)))).astype(int)
firms=pd.DataFrame({'score':score,'employees':employees,'sector':sector})
firms['score_band']=pd.cut(score,[0,2.5,3.5,5.01],labels=['Lower','Middle','Higher'],right=False)
band=[]
for name,g in firms.groupby('score_band',observed=True):
    band.append(dict(band=str(name),n=len(g),mean_size=float(g.employees.mean()),median_size=float(g.employees.median()),large=int(g.employees.ge(60).sum()),large_share=float(g.employees.ge(60).mean())))
firms['bin']=pd.qcut(firms.score,10,labels=False)
bins=firms.groupby('bin').agg(score=('score','mean'),size=('employees','mean'),n=('score','size')).reset_index()
cov=float(np.cov(score,employees,ddof=1)[0,1]);r=float(np.corrcoef(score,employees)[0,1])
# A symmetric nonlinear example has Pearson r approximately zero despite y=x^2.
nx=np.linspace(-3,3,31);ny=nx**2
# Paired-deviation hand calculation uses explicitly authored three observations.
tx=np.array([1.,2.,3.]);ty=np.array([2.,2.,5.])
# Simpson-style example: authored counts expose a composition reversal.
# Within each sector, training group has larger success share; pooled reverses.
simpson=[{'sector':'Simple','group':'Training','success':18,'n':20},
         {'sector':'Simple','group':'Comparison','success':72,'n':90},
         {'sector':'Complex','group':'Training','success':24,'n':80},
         {'sector':'Complex','group':'Comparison','success':2,'n':10}]
pooled={g:sum(z['success'] for z in simpson if z['group']==g)/sum(z['n'] for z in simpson if z['group']==g) for g in ['Training','Comparison']}
out={'seed':42022,'synthetic':True,'n':n,'cap':cap,'summary':{'min':float(x.min()),'max':float(x.max()),'mean':float(x.mean()),'median':float(np.median(x)),'sd':float(x.std(ddof=1)),'q1':float(q[0]),'q3':float(q[2]),'iqr':float(iqr),'fences':fences,'whiskers':[float(inside.min()),float(inside.max())],'outside':int(((x<fences[0])|(x>fences[1])).sum()),'skew':float(stats.skew(x,bias=False))},
 'hist':{'edges':edges.tolist(),'counts':counts.tolist(),'density':density.tolist(),'fine_edges':fine_edges.tolist(),'fine_counts':fine_counts.tolist(),'coarse_edges':coarse_edges.tolist(),'coarse_counts':coarse_counts.tolist()},
 'kde':{'x':kgrid.tolist(),'density':kde(kgrid).tolist(),'bandwidth_cu':float(kde.factor*x.std(ddof=1))},
 'toy':{'before':toy.tolist(),'after':toy_shift.tolist(),'mean_before':float(toy.mean()),'mean_after':float(toy_shift.mean()),'median_before':float(np.median(toy)),'median_after':float(np.median(toy_shift))},'groups':groups,
 'events':{'table':[[a,b],[c,d]],'under_n':int(under.sum()),'refund_n':int(refund.sum()),'p_under':float(under.mean()),'p_refund':float(refund.mean()),'p_joint':a/n,'p_under_given_refund':a/(a+b),'p_refund_given_under':a/(a+c),'conditional_mean_refund':float(x[refund].mean()),'conditional_mean_nonrefund':float(x[~refund].mean())},
 'reward':{'values':reward.tolist(),'probabilities':prob.tolist(),'mean':expected,'variance':variance,'sd':float(np.sqrt(variance))},
 'models':models,'binom':{'k':model_k.tolist(),'prob':binom.tolist()},
 'firms':{'n':N,'bands':band,'bins':json.loads(bins.to_json(orient='records')),'r':r,'cov':cov,'sd_score':float(score.std(ddof=1)),'sd_size':float(employees.std(ddof=1)),'r_log_size':float(np.corrcoef(score,np.log(employees))[0,1]),'points':np.column_stack([score,employees]).tolist(),'nonlinear_points':np.column_stack([nx,ny]).tolist(),'nonlinear_r':float(np.corrcoef(nx,ny)[0,1]),'toy_pairs':np.column_stack([tx,ty]).tolist(),'toy_cov':float(np.cov(tx,ty,ddof=1)[0,1]),'toy_r':float(np.corrcoef(tx,ty)[0,1])},
 'simpson':simpson,'simpson_pooled':pooled}
print(json.dumps(out,allow_nan=False))
'''

LAB3=r'''"""Original synthetic inference lab. Seed 43023. No network or input files.
The fictional Lumen index has IID normal log changes with mean .0003, SD .011.
A separate waiting-time population is shifted exponential (mean 12, SD 8).
Paired retail quotes and independent queue samples are invented. Parameters are
chosen for teaching, never calibrated to historical records. numpy/pandas/scipy.
"""
import json
import numpy as np
import pandas as pd
from scipy import stats
rng=np.random.default_rng(43023)
def ci_mean(x,level=.95):
    x=np.asarray(x);n=len(x);mean=x.mean();sd=x.std(ddof=1);se=sd/np.sqrt(n)
    q=stats.t.ppf((1+level)/2,n-1)
    return dict(n=n,mean=float(mean),sd=float(sd),se=float(se),critical=float(q),low=float(mean-q*se),high=float(mean+q*se))
def wilson(k,n,level=.95):
    z=stats.norm.ppf((1+level)/2);ph=k/n;den=1+z*z/n
    center=(ph+z*z/(2*n))/den;half=z*np.sqrt(ph*(1-ph)/n+z*z/(4*n*n))/den
    return [float(center-half),float(center+half)]
# 1. A planned session calendar, not every date. Do not fabricate closed-day prices.
calendar=pd.date_range('2030-01-01',periods=370,freq='D')
sessions=calendar[calendar.dayofweek<5]
sessions=sessions.delete([15,82,140])[:250]
log_change=rng.normal(.0003,.011,len(sessions)-1)
level=100*np.exp(np.r_[0,np.cumsum(log_change)])
change=np.diff(level)/level[:-1] # simple session-to-session changes
loss=change<-.012;n=len(change);k=int(loss.sum());ph=k/n
# IID benchmark calculations are conditional on the authored DGP; transfer to a
# real time series would require dependence, missingness and regime diagnostics.
# 2. Sampling distributions: skewed population, independent draws, fixed seed.
sample_sizes=[5,20,80];sampling=[]
for m in sample_sizes:
    means=(4+rng.exponential(8,size=(4000,m))).mean(axis=1)
    sampling.append(dict(n=m,mean=float(means.mean()),sd=float(means.std(ddof=1)),theory_se=float(8/np.sqrt(m)),skew=float(stats.skew(means,bias=False))))
path=4+rng.exponential(8,size=5000);cum=np.cumsum(path)/np.arange(1,len(path)+1)
path_n=[5,10,20,40,80,160,320,640,1280,2560,5000]
# Small sample calculation separates normal-known-sigma from t-estimated-sigma.
small=np.array([7.,9.,10.,12.,17.]);small_ci=ci_mean(small)
# Repeated interval coverage is measured here for a genuinely normal population.
coverage_draws=rng.normal(12,8,size=(3000,20));means=coverage_draws.mean(axis=1)
ses=coverage_draws.std(axis=1,ddof=1)/np.sqrt(20);q=stats.t.ppf(.975,19)
coverage=float(((means-q*ses<=12)&(means+q*ses>=12)).mean())
# 3. One skewed sample: same-size bootstrap versus smaller subsets without replacement.
wait=4+rng.exponential(8,size=80);wait_ci=ci_mean(wait)
B=4000
boot=rng.choice(wait,size=(B,len(wait)),replace=True).mean(axis=1)
sub=np.array([rng.choice(wait,size=20,replace=False).mean() for _ in range(B)])
# Resampling SDs target different designs. Finite-population adjustment explains
# much of the subset variability: s*sqrt((1-m/n)/m), with small finite correction.
boot_ci=np.quantile(boot,[.025,.975])
# Cluster demonstration: 30 groups x 8 measurements with a shared group shock.
cluster=30;within=8;shock=rng.normal(0,4,cluster);noise=rng.normal(0,3,(cluster,within))
cluster_data=20+shock[:,None]+noise
naive=cluster_data.ravel().std(ddof=1)/np.sqrt(cluster*within)
cluster_se=cluster_data.mean(axis=1).std(ddof=1)/np.sqrt(cluster)
# 4. Exact one-sided binomial test and power use the identical fixed rejection rule.
# H0 p=.10 versus p>.10, n=100, alpha=.05; threshold is selected before data.
ntest=100;p0=.10;alpha=.05
critical=next(c for c in range(ntest+1) if stats.binom.sf(c-1,ntest,p0)<=alpha)
obs=int(rng.binomial(ntest,.18))
pval=float(stats.binom.sf(obs-1,ntest,p0))
power_ps=[.10,.12,.15,.18,.20,.25]
powers=[float(stats.binom.sf(critical-1,ntest,v)) for v in power_ps]
strict=next(c for c in range(ntest+1) if stats.binom.sf(c-1,ntest,p0)<=.01)
# 5. Matched retail quotes: same invented product on two channels, at one time.
# Product base prices create positive pairing correlation. Differences have their
# own distribution; analyzing all prices as independent discards this information.
products=40;base=rng.uniform(25,90,products)
offline=base+rng.normal(0,1.3,products)
delta=rng.normal(.45,1.55,products);online=offline+delta
d=online-offline;pair=ci_mean(d);paired_test=stats.ttest_rel(online,offline)
ci90=ci_mean(d,.90);margin=1.5
# TOST equivalence: reject both H0 mu<=-margin and H0 mu>=margin at alpha .05.
tlower=(pair['mean']+margin)/pair['se'];tupper=(pair['mean']-margin)/pair['se']
tost_p_lower=float(stats.t.sf(tlower,products-1));tost_p_upper=float(stats.t.cdf(tupper,products-1))
# Independent groups: Welch-Satterthwaite rather than a forced common variance.
a=rng.normal(12,2,22);b=rng.normal(13.1,3.4,30)
va=a.var(ddof=1)/len(a);vb=b.var(ddof=1)/len(b);diff=float(a.mean()-b.mean());se=float(np.sqrt(va+vb));df=(va+vb)**2/(va*va/(len(a)-1)+vb*vb/(len(b)-1));wq=stats.t.ppf(.975,df);wt=stats.ttest_ind(a,b,equal_var=False)
# Multiplicity: these are hypothetical p-values, not concealed external tests.
raw_p=np.array([.003,.018,.041,.22,.61]);m=len(raw_p);order=np.argsort(raw_p)
holm_sorted=np.minimum(1,np.maximum.accumulate((m-np.arange(m))*raw_p[order]));holm=np.empty(m);holm[order]=holm_sorted
# Sampling distribution histogram for the original-sample bootstrap means.
binedges=np.linspace(float(boot.min()),float(boot.max()),13);bincounts,_=np.histogram(boot,binedges)
out={'seed':43023,'synthetic':True,'calendar_days':len(calendar),'sessions':len(sessions),'returns_n':n,
 'session_excerpt':[{'date':str(sessions[i].date()),'index':float(level[i]),'change_pct':None if i==0 else float(change[i-1]*100)} for i in range(8)],
 'index_path':{'x':list(range(0,len(level),10)),'level':level[::10].tolist()},
 'risk':{'threshold':-.012,'count':k,'n':n,'proportion':ph,'wilson':wilson(k,n),'quantile_05':float(np.quantile(change,.05)),'sparse_wilson':wilson(1,20)},
 'sampling':sampling,'lln':{'n':path_n,'means':[float(cum[v-1]) for v in path_n]},
 'small':small_ci,'coverage':coverage,
 'wait':wait_ci,'resampling':{'B':B,'bootstrap_se':float(boot.std(ddof=1)),'bootstrap_ci':boot_ci.tolist(),'subset_size':20,'subset_sd':float(sub.std(ddof=1)),'subset_theory':float(wait.std(ddof=1)*np.sqrt((1-20/80)/20)),'edges':binedges.tolist(),'counts':bincounts.tolist()},
 'cluster':{'n':cluster*within,'clusters':cluster,'naive_se':float(naive),'cluster_se':float(cluster_se),'population_icc':16/25,'design_effect':1+7*16/25},
 'test':{'n':ntest,'p0':p0,'alpha':alpha,'critical':critical,'actual_alpha':float(stats.binom.sf(critical-1,ntest,p0)),'observed':obs,'pvalue':pval,'reject':pval<=alpha,'strict_critical':strict,'strict_power_018':float(stats.binom.sf(strict-1,ntest,.18)),'alternatives':power_ps,'power':powers},
 'paired':dict(pair,t=float(paired_test.statistic),p=float(paired_test.pvalue),ci90=[ci90['low'],ci90['high']],margin=margin,tost_p=[tost_p_lower,tost_p_upper],equivalent=max(tost_p_lower,tost_p_upper)<.05,min=float(d.min()),max=float(d.max()),correlation=float(np.corrcoef(online,offline)[0,1]),differences=d.tolist(),points=[] )}
# Add raw pairs and independent-group summaries for reproducible auditing.
out['paired']['points']=np.column_stack([offline,online]).tolist()
out['welch']={'n_a':len(a),'n_b':len(b),'mean_a':float(a.mean()),'mean_b':float(b.mean()),'sd_a':float(a.std(ddof=1)),'sd_b':float(b.std(ddof=1)),'difference':diff,'se':se,'df':float(df),'t':float(wt.statistic),'p':float(wt.pvalue),'ci':[float(diff-wq*se),float(diff+wq*se)]}
out['multiplicity']={'p':raw_p.tolist(),'holm':holm.tolist(),'bonferroni_cutoff':.05/m,'fwer_20_independent':float(1-.95**20)}
print(json.dumps(out,allow_nan=False))
'''

def build1(d):
    q=d['quality']; offers=d['offers']; ts=d['town_summary']; ms=d['manager_summary']; best=ms[0]
    sections=[]
    add=lambda *a: sections.append(sec(*a))
    add('decision-first','Start with a decision and a data passport',
        p('A colleague is comparing two-night stays across the fictional towns of Willow Bay, Cedar Reach and Juniper Vale. The decision is not “find the smallest number.” It is “choose an eligible, comparable offer within a budget.” Evidence must preserve what was observed, for whom, when and under which terms. In this lesson, all quotes and fixtures are newly generated teaching data, not market research.')+
        p('Write a data passport before calculating: decision, target population, observation unit, fields, collection time, selection rules, provenance and known limits. Our target is the generated set of private-room hotel quotes for two specified arrival dates. We cannot infer availability, service quality or actual prices elsewhere.')+
        ul('Decision: shortlist comparable two-night hotel offers.','Observation: one lodging × arrival date quote, for one room.','Source: local simulation, seed 41021, prices in fictional currency units (CU).','Handoff: a comparable table, an audit trail and a bounded recommendation.'),
        'Would “the cheapest hotel in Willow Bay” be supported by this exercise?',
        'No. We observe generated offers for specified dates and terms, not every real hotel or every possible stay. The defensible claim is cheapest among the eligible complete synthetic offers.')
    add('observation-unit','A row is a claim about an observation',
        p('The same lodging appears on two arrival dates. That is not automatically a duplicate: price can vary by date. A cross-section records entities at one time; a time series follows one entity through time; a panel follows multiple entities repeatedly. The unit determines which questions the table can answer and which fields must identify a row.')+
        table(['Structure','One row','Candidate key'],[['Cross-section','One lodging on one fixed date','lodging_id'],['Time series','One lodging on each date','arrival'],['Panel','One lodging × one date','lodging_id + arrival']],'Three observation structures')+
        p('A quote is also not a booking or a guest. Counting quote rows does not count customers, purchases or occupied rooms. Changing the noun in the conclusion silently changes the estimand, the quantity the analysis is meant to describe.'),
        'A lodging appears twice, on April 10 and April 17. Should one row be deleted?',
        'Not on that evidence. The composite key is lodging_id plus arrival. Two different dates represent two legitimate observations.')
    add('trust-six-questions','Check meaning, validity, reliability and coverage',
        p('A clean-looking table can still support the wrong decision. Meaning asks what the field denotes. Validity asks whether it measures the intended concept. Reliability asks whether repeated measurement is stable. Comparability asks whether the same definitions apply across rows. Coverage asks which members of the target population could appear. Selection asks why some actually appear.')+
        table(['Question','Risk in a quote table','Useful response'],[['Meaning','Nightly price mistaken for total','Name currency, nights and inclusions'],['Validity','Star rating treated as service quality','State what the rating measures'],['Reliability','Quotes change between retrievals','Record retrieval time and terms'],['Comparability','Tax or room occupancy differs','Standardize or separate offers'],['Coverage','Only one platform is observed','Limit the population claim'],['Selection','Only promoted listings are visible','Describe the selection mechanism']],'A six-question trust check')+
        p('These are design questions, not defects a prettier chart fixes. A reliable measure can still measure the wrong thing. A complete file can still omit the people or firms the decision concerns.'),
        'Does a larger file repair a coverage gap?',
        'No. More observations from the same incomplete frame can reduce random error while preserving systematic exclusion.')
    add('selection','Data collection changes who is visible',
        p('Administrative records cover activity a system records. Surveys cover those sampled and those who respond. Web listings cover what is published and retrievable. Experiments change an assignment mechanism but still need a recruitment frame. Benchmarking may compare organizations with different definitions. Each source has strengths, but none makes selection disappear.')+
        p('Distinguish coverage from response. If only loyalty members receive a survey, nonmembers have no opportunity to appear. If every guest is invited but dissatisfied guests reply more often, response changes the observed mix. Increasing response among existing invitees does not add missing nonmembers.')+
        p('Our simulation has deliberately complete knowledge of its generating process. That is a teaching advantage, not a claim about operational data. A real collection plan also needs lawful access, proportionate collection, privacy safeguards and documented permission for reuse. Do not store personal information merely because it is technically available.'),
        'What is the first question before scraping a much larger list?',
        'Which population and fields are actually needed, whether access and reuse are permitted, and whether the new source changes the coverage or selection problem.')
    add('measurement','Define comparable quantities and variable types',
        p('Digits do not guarantee arithmetic is meaningful. A lodging identifier is nominal even if it contains numbers. A star rating is ordinal: five is ranked above four, but the difference need not equal the difference between three and two. A price has meaningful differences and ratios when currency and terms match. A date supports ordering and elapsed-time calculations, but not arbitrary ratios.')+
        table(['Field','Type','Defensible operation'],[['lodging_id','Nominal identifier','Match, count distinct values'],['rating','Ordinal category','Order, tabulate category shares'],['nightly_cu','Quantitative ratio scale','Compare sums and ratios under common terms'],['refundable','Binary category','Count and calculate a defined share'],['arrival','Date','Order and calculate elapsed days']],'A compact data dictionary')+
        formula('Two-night total = (2 × nightly price + cleaning fee) × (1 + tax rate)')+
        p('Here tax is assumed to apply to both room and cleaning, and all offers use one room. These are explicit simulation assumptions. If a real jurisdiction taxes them differently, change the definition before computing.'),
        'Can a hotel rated 4 be described as twice as good as a hotel rated 2?',
        'No. The rating is ordinal, not a ratio measure of quality. The numeric labels support order, not that ratio claim.')
    add('keys','Verify identity before removing duplicates',
        p(f'The raw lab has {q["raw"]} rows. One is an exact duplicate introduced to imitate an ingestion retry. Removing that exact repeated record leaves {q["deduplicated"]} distinct quote rows. The candidate key lodging_id + arrival is then unique. We do not delete all repeated lodging IDs, because the dates are part of the observation.')+
        p('A duplicate key with different prices is a conflict, not an automatic invitation to keep the first row. Investigate whether the rows refer to different retrieval times, room types or refund terms. If a newer observation supersedes an older one, retain provenance and state the precedence rule. Entity resolution across misspelled names likewise needs recorded evidence and a reversible mapping.')+
        formula('Key check: number of distinct (lodging_id, arrival) pairs = number of rows')+
        p('Uniqueness is necessary for this table, but not sufficient for truth. A unique row can still have the wrong unit, date or amount.'),
        'Two rows share a key but one costs 80 CU and the other 95 CU. Is drop_duplicates a complete remedy?',
        'No. Exact de-duplication does not resolve conflicting values. Determine whether the observation definition needs another field or whether one value is an error, then document the decision.')
    add('inspect','Inspect values before narrowing the sample',
        p('Start with row count, field types, key uniqueness, missingness and plausible ranges. Preserve the original generated table, then create a working copy. The excerpt below deliberately includes problematic values and an exact repeated row. Missing and invalid values are different findings, even if both prevent a comparable total.')+
        table(['Lodging','Arrival','Kind','Room','Nightly CU'],[[r['lodging_id'],r['arrival'],r['kind'],r['room'],'missing' if r['nightly_cu'] is None else fmt(r['nightly_cu'])] for r in d['raw_excerpt']],'Synthetic raw excerpt, including known defects')+
        p(f'There are {q["initial_missing"]} initially missing prices and {q["invalid_nonpositive"]} nonpositive price. The lab flags the negative value, converts it to missing in the analysis copy, and does not guess a replacement. A zero might be meaningful in another domain, so this is a price-specific validation rule rather than a universal cleaning habit.'),
        'Why keep the raw table after making corrections?',
        'It separates what arrived from what the analyst changed. A colleague can audit each rule, reproduce the analysis and revise a rule without reconstructing lost information.')
    add('scope','A filter changes the population',
        p(f'We keep exact kind = Hotel and room = Private rows after removing the known duplicate. That leaves {q["scoped"]} quote rows. Of these, {q["excluded_missing_in_scope"]} cannot produce a valid total, leaving {q["complete"]} complete comparable quotes. We report both the eligibility filter and the completeness exclusion.')+
        bars(['Raw','Distinct','In scope','Complete'],[q['raw'],q['deduplicated'],q['scoped'],q['complete']],'Synthetic preparation funnel','Quote rows')+
        p('Exact matching is deliberate: a Guesthouse is not silently recoded as a Hotel. Conversely, genuine spelling variants would require a documented normalization rule. This filter does not fix platform coverage, measurement validity or the fact that two arrival dates are a limited window.'),
        'Does the final row count prove the missing quotes are irrelevant?',
        'No. If missingness depends on price or lodging type, the complete-case summary can shift. Report the missingness and investigate its cause before generalizing.')
    add('comparison','Calculate a comparable offer, then qualify the choice',
        p('The following offers are sorted by the same two-night total, with tax and cleaning handled consistently. Sorting by nightly price alone can reverse a comparison when fixed fees differ. Refundability and walking distance remain separate decision attributes; compressing them into a score requires explicit weights.')+
        table(['Lodging','Town','Arrival','Nightly CU','Cleaning CU','Total CU','Refundable'],[[r['lodging_id'],r['town'],r['arrival'],fmt(r['nightly_cu']),fmt(r['cleaning_cu']),fmt(r['two_night_total_cu']),'Yes' if r['refundable'] else 'No'] for r in offers],'Six lowest eligible complete synthetic offers')+
        p('A ranking is conditional on the chosen outcome and eligibility rules. The cheapest complete observation does not establish best service, best overall value or future availability. A defensible shortlist names the price measure and leaves judgment about other attributes visible.'),
        'If the cheapest offer is nonrefundable, must it be selected?',
        'No. The total answers a cost question. Flexibility is another criterion, and its value depends on the traveler’s needs. Apply an explicit constraint or trade-off instead of pretending price captures everything.')
    add('reshape','Change layout without changing meaning',
        p('A second miniature case tracks fictional service requests by town and quarter. In wide form, quarters occupy columns. In long form, quarter becomes a variable and requests becomes the value. A reshape changes representation, not the underlying observation unit: one town-quarter remains one observation.')+
        table(['Town','Q1','Q2','Q3'],[[r['town'],r['Q1'],r['Q2'],'missing' if r['Q3'] is None else r['Q3']] for r in d['service_wide']],'Synthetic service requests, wide layout')+
        p(f'Willow Bay, Q2 equals {d["trace"]} requests in both layouts. Juniper Vale, Q3 is unrecorded. It is not zero requests. A total over observed quarters answers a different question from a full-year total, so a skip-missing default must not be interpreted as complete coverage.'),
        'What must remain attached to a value after reshaping?',
        'Its identifying fields, unit and missingness status. The value alone is not enough: town and quarter tell us which observation it describes.')
    add('pivot','Melt, pivot and join are different operations',
        p('Melt collects selected value columns into a variable/value pair. Pivot spreads a variable into columns and requires one value per output cell. A join attaches fields using matching keys. These operations are easy to confuse because each changes the visible table, but they preserve different relationships.')+
        table(['Town','Quarter','Requests'],[[r['town'],r['quarter'],'missing' if r['requests'] is None else r['requests']] for r in d['service_long']],'Synthetic service requests after melt')+
        p('Before pivoting, verify town + quarter uniqueness. If two source rows map to one cell, an aggregation such as mean or sum is a substantive decision, not a neutral reshape. A pivot table may silently aggregate where a strict pivot would correctly expose a conflict.'),
        'Two records map to Willow Bay, Q2. Why not average them automatically?',
        'They may be duplicates, different service categories or revised observations. Averaging could erase the actual observation definition. Resolve the key or justify a specific aggregation first.')
    add('join','A join can multiply the evidence',
        p(f'Each quote needs one walking-distance attribute from a lodging dimension. The safe many-to-one join keeps {q["safe_join_rows"]} rows and verifies every key matched. Deliberately duplicating one dimension key creates {q["unsafe_join_rows"]} rows in the unsafe join. A duplicated quote then receives extra weight in later averages.')+
        table(['Relationship','Expected key pattern','Typical safeguard'],[['One-to-one','Both sides unique','Validate both keys'],['Many-to-one','Repeated left keys, unique right keys','Validate right key and row-count stability'],['Many-to-many','Both sides repeat','Explain intended combinations or redesign keys']],'Join cardinality is part of the analysis')+
        p('Record unmatched keys as well as row growth. An inner join can shrink the sample by dropping unmatched observations; a left join preserves them but may introduce missing attributes. Validate cardinality, compare row counts and inspect the match indicator before calculating.'),
        'A join succeeds without an error. Does that prove it is correct?',
        'No. Unless cardinality and coverage were explicitly checked, a syntactically valid join may duplicate or drop observations and change the analysis population.')
    add('events','An event can produce multiple observations',
        p(f'The next case contains {d["fixtures_n"]} fictional fixtures among Aster, Bracken, Clover and Dahlia. A fixture is one event, but team performance needs one observation per team per fixture. Transforming each event into home-team and away-team records gives {d["team_rows_n"]} team-game rows.')+
        table(['Date','Home','Away','Home goals','Away goals'],[[r['date'],r['home'],r['away'],r['hg'],r['ag']] for r in d['fixtures']],'Two freshly simulated fixtures')+
        formula('Team points = 3 for a win; 1 for a draw; 0 for a loss')+
        p('The two rows from a fixture are linked: one team’s win implies the other team’s loss. This dependence matters for later inference even though row expansion is correct for descriptive grouping. Distinguish the reporting unit from the independent unit.'),
        'Does expanding 24 events to 48 team rows create 48 independent games?',
        'No. It creates two perspectives on each event, not twice as much independent evidence. Both the event ID and team ID should be retained.')
    add('date-join','Assign time-varying attributes with date boundaries',
        p(f'Each fictional team changes manager on February 16. Joining by team alone gives {d["candidate_rows_n"]} candidate rows because every game matches both managers. We retain the match whose date falls inside its tenure. A half-open interval includes the start and excludes the end: start ≤ date &lt; end.')+
        table(['Fixture','Date','Team','Assigned manager','Points'],[[r['fixture_id'],r['date'],r['team'],r['manager'],r['points']] for r in d['assigned_excerpt']],'A synthetic boundary-date assignment')+
        p('The new manager owns February 16; the previous tenure ends immediately before it. Verify that each team-game has exactly one match. Zero matches signal a gap. Multiple matches signal overlapping tenures or a duplicate definition. Both require investigation before a summary is credible.'),
        'If both tenures include their end date, what goes wrong on February 16?',
        'The boundary game can match both managers and be counted twice. A consistent half-open interval avoids that ambiguity.')
    add('aggregation','The group and denominator define the result',
        p('Group by team and manager together, then calculate games, observed point values, total points and points per game. The distinction between row count and nonmissing count is important: a mean can silently ignore missing outcomes while a game count includes them. Our generated outcome fields are complete, and the lab checks that explicitly.')+
        table(['Team','Manager','Games','Observed','Total points','Points/game'],[[r['team'],r['manager'],r['games'],r['observed'],r['total'],fmt(r['ppg'],3)] for r in ms],'Synthetic team-manager summaries')+
        formula('Points per game = total recorded points / games with recorded points')+
        p('When all outcomes are complete, that denominator equals games played. Otherwise report the gap and avoid labeling a partial-outcome average as a complete performance rate. An aggregation discards within-group detail, so retain the prepared event table for audit.'),
        'A group has 10 game rows but only 8 recorded point values. What does its default mean use?',
        'Usually the 8 nonmissing values. Dividing their sum by 10 instead answers a different question and implicitly treats missing outcomes as zero. Investigate and disclose the gap.')
    add('weights','Weight rates by their actual exposure',
        p('Averaging group averages gives each group equal influence. Pooling observations weights each group by its number of observations. Neither is automatically wrong; they answer different questions. Name whether the target is the average group or the average observation.')+
        table(['Group','Games','Points','Points/game'],[['Short tenure',2,6,3],['Long tenure',8,8,1]],'An explicitly authored synthetic denominator example')+
        formula(f'Pooled rate = (6 + 8) / (2 + 8) = {fmt(d["toy"]["weighted"])}; equal-group mean = (3 + 1) / 2 = {fmt(d["toy"]["unweighted"])}')+
        bars([r['town'] for r in ts],[r['mean'] for r in ts],'Mean comparable two-night total by fictional town','CU')+
        p('The lodging chart is descriptive of complete in-scope quote rows. Town means can also reflect room mix, dates and selection. A group comparison is not an explanation of why the groups differ.'),
        'Which rate describes a randomly selected game from the ten-game toy dataset?',
        f'The pooled rate, {fmt(d["toy"]["weighted"])} points per game. The equal-group average describes selecting a tenure uniformly and then using its average.')
    add('ranking','A ranking is a conditional description',
        p(f'In this simulation, the highest team-manager average is {best["manager"]} with {fmt(best["ppg"],3)} points per game across {best["games"]} games. The illustration uses an eligibility threshold of at least six games, stated before ranking. All qualifying groups remain visible, including ties.')+
        p('Eligibility controls which comparisons are reported; it does not create causal comparability. Manager assignments, team quality, opponents, injuries and timing can differ. A short-tenure threshold also is not a reliable label for caretaker status. Do not infer a job category from a duration filter alone.')+
        ul('Supported: this group has the highest observed rate among eligible groups in this generated schedule.','Unsupported: this manager caused the highest performance or would improve every team.','Useful next step: inspect schedule balance, uncertainty and the assignment process before a consequential decision.'),
        'Why is “best manager” stronger than the calculation supports?',
        'The calculation ranks observed outcomes under specific teams and schedules. It does not isolate managerial contribution from the other causes of those outcomes.')
    add('handoff','Leave an audit trail and a bounded recommendation',
        p('Use a repeatable sequence: detect, decide, correct and document. Checks should cover identity, scope, values and relationships. Every correction should have a reason, a reversible transformation and a measurable consequence such as rows affected. Missingness is an investigation prompt, not an automatic deletion instruction.')+
        table(['Audit field','What this lab records'],[['Identity','Composite quote key; fixture + team key'],['Scope','Private-room Hotel quotes on two arrival dates'],['Values','Missing prices, nonpositive-price flag, explicit tax formula'],['Relationships','Many-to-one lodging join; date-aware manager assignment'],['Reproduction','Seed 41021, standalone code, calculated JSON and notebook'],['Limit','Synthetic exercise, no evidence about actual markets or managers']],'A defensible handoff checklist')+
        p(f'Management handoff: “I compared {q["complete"]} complete synthetic quotes under a common two-night price definition. I removed one known ingestion duplicate, flagged invalid prices and verified key-safe joins. The shortlist is conditional on eligibility and completeness. Review refundability and trip requirements before selecting an offer.”')+
        p('Next, Lesson 2 asks what the remaining observations look like. Distributional analysis begins only after the observation, population and preparation choices are defensible.'),
        'What should a colleague be able to do with the handoff?',
        'Rebuild the result from the standalone lab, explain every denominator and exclusion, identify its main limitation, and understand the action the evidence can support.')
    assert len(sections)==18
    render_lesson(1,'Build evidence you can trust','Define observations, prepare comparable tables and preserve meaning through reshapes, joins and summaries.',sections)
    (ROOT/'content'/'lesson1-outline.json').write_text(json.dumps([s['title'] for s in sections],indent=2)+'\n')

def build2(d):
    s=d['summary'];h=d['hist'];g=d['groups'];e=d['events'];f=d['firms'];m=d['models'];t=d['toy'];rw=d['reward'];a,b=e['table'][0];c,z=e['table'][1]
    sections=[];add=lambda *args:sections.append(sec(*args))
    add('distribution','Read one observation before reading the distribution',
        p(f'This lesson generates {d["n"]} independent fictional lodging quotes from explicitly chosen lognormal models. Willow Bay contributes 180, Cedar Reach 110 and Juniper Vale 70. Each row is one quoted nightly price in fictional CU under a common assumed room specification. These are new observations, separate from Lesson 1’s preparation example.')+
        p('A distribution describes which values occur and how frequently. Start with support, units, missingness and the observation definition before interpreting shape. A high price may be legitimate, a unit error or a different product. A histogram alone cannot distinguish these explanations.')+
        ul(f'Observed range: {fmt(s["min"])} to {fmt(s["max"])} CU.','Target here: the generated quote population under the stated mechanism.','Not observed: actual availability, guest experiences, purchases or real-market prices.'),
        'What does one price observation say about what a customer paid?',
        'Only what was quoted in this synthetic case. A quote is not an accepted booking or a realized payment.')
    add('density','Count, proportion and density use different scales',
        p('A count is the number of observations in a bin. A proportion divides that count by the sample size. A density also divides by bin width, so probability is represented by rectangle area. This matters when widths differ: a wider bin can contain more observations simply because it covers a larger interval.')+
        formula('Bin density = count / (sample size × bin width); bin probability = density × width')+
        histogram(h['edges'],h['density'],'Unequal-width density histogram of synthetic nightly prices','Probability per CU')+
        p('The areas sum to one over the displayed full range. Heights do not. The final interval includes its upper endpoint; other intervals include the lower endpoint and exclude the upper. With continuous measurements, boundary conventions rarely change much, but the implementation still needs one.'),
        'A width-40 bin has density 0.005 per CU. What share does it contain?',
        'Its area is 40 × 0.005 = 0.20, or 20%. Density has inverse-price units; it is not itself a probability at a point.')
    add('bin-width','Change bins and look for stable features',
        p('Bin width is an analytical choice, not a feature of the underlying observations. Very narrow bins show noisy local fluctuations; very wide bins can hide modes or gaps. Shift the origin or change width and ask which conclusions survive. Keep the observations and denominator fixed while changing the view.')+
        histogram(h['coarse_edges'],h['coarse_counts'],'Six-bin view of the same synthetic prices','Quote count')+
        histogram(h['fine_edges'],h['fine_counts'],'Twelve-bin view of the same synthetic prices','Quote count')+
        p('Both views summarize exactly the same generated rows and full range. The right tail is more defensible than a story about a particular small peak. If a decision hinges on a threshold, calculate the exact threshold share rather than estimating it from whichever bin happens to contain the cutoff.'),
        'If one binning looks bimodal and another does not, what should you report?',
        'The apparent second mode is sensitive to bin choices. Inspect finer evidence and the collection process rather than presenting one histogram as conclusive.')
    add('denominator','Name the denominator before comparing a percentage',
        p('A percentage is incomplete without the event and the population. “Under budget” here means price ≤ 140 CU, among all generated quotes in the relevant town. A percentage among hotels, among complete quotes or among refundable offers can differ because each uses a different denominator.')+
        table(['Fictional town','Quotes','At most 140 CU','Within-town share'],[[r['town'],r['n'],r['under'],f'{100*r["proportion"]:.1f}%'] for r in g],'Synthetic budget shares with denominators')+
        p('Raw counts can make a large group look better even when its share is lower. A location filter changes the target population, so document it before recomputing the percentage. A histogram cropped to central values also needs disclosure: if counts outside the view disappear, readers may mistake a conditional distribution for the full one.'),
        'Can 60 affordable quotes out of 100 be compared with 80 out of 200 using counts alone?',
        'Not to compare affordability rates. The shares are 60% and 40%. Counts answer inventory volume; shares answer the within-group frequency.')
    add('centers','Mean, median and mode answer different questions',
        p(f'The overall synthetic mean is {fmt(s["mean"])} CU and the median is {fmt(s["median"])} CU. The mean uses every value and is relevant to expected total spending under random sampling from this mix. The median splits observations into halves and describes a typical central quote. A mode identifies a most frequent value or region, but continuous-price modes depend on rounding, bins or smoothing.')+
        table(['Toy dataset','Values','Mean','Median'],[['Original',', '.join(f'{v:g}' for v in t['before']),fmt(t['mean_before']),fmt(t['median_before'])],['One changed value',', '.join(f'{v:g}' for v in t['after']),fmt(t['mean_after']),fmt(t['median_after'])]],'Synthetic sensitivity of mean and median')+
        p('The mean moves sharply when one large value changes because its contribution is linear in the total. The median does not move here because the middle order statistic is unchanged. Robustness is useful, but neither summary is universally superior: choose the statistic that matches the decision.'),
        'Which summary is more directly connected to the total cost of many randomly selected stays?',
        'The mean, multiplied by the number of stays, under a stable and relevant sampling mix. The median is not generally additive.')
    add('spread','Use quantiles and deviations to describe variability',
        p(f'The first quartile is {fmt(s["q1"])} CU, the third quartile is {fmt(s["q3"])} CU and the interquartile range is {fmt(s["iqr"])} CU. The sample SD is {fmt(s["sd"])} CU. Quantiles locate positions in the ordered sample; SD describes squared deviations around the mean. They answer different questions and react differently to extremes.')+
        formula('Sample variance s² = Σ(xᵢ − x̄)² / (n − 1); sample SD s = √s²')+
        p('The n − 1 denominator makes sample variance unbiased for population variance under IID sampling with finite variance. It does not make SD itself exactly unbiased. Squaring deviations gives distant observations more influence. The IQR is resistant to a small number of extremes but omits tail magnitude.')+
        p('The lab uses NumPy’s linear-interpolation quantiles. A quartile can fall between observed prices; it need not be a price actually quoted. Different documented quantile conventions can produce small differences, especially in tiny samples.'),
        'If all prices are multiplied by 1.1, what happens to variance and SD?',
        'SD is multiplied by 1.1, while variance is multiplied by 1.1² = 1.21. Both the location and units must be considered when comparing variability.')
    add('shape','Describe shape, then investigate unusual values',
        p(f'The generated price distribution is right-skewed, with sample skewness {fmt(s["skew"],3)}. Its Tukey fences are {fmt(s["fences"][0])} and {fmt(s["fences"][1])} CU. There are {s["outside"]} observations beyond those fences. These are screening flags, not proof of error.')+
        table(['Feature','Synthetic value'],[['Lower whisker',fmt(s['whiskers'][0])],['Q1',fmt(s['q1'])],['Median',fmt(s['median'])],['Q3',fmt(s['q3'])],['Upper whisker',fmt(s['whiskers'][1])]],'Five-number boxplot components using Tukey whiskers')+
        p('Whiskers extend to the most extreme observed values still within the fences, not automatically to the fence values themselves. The range records the full observed extremes. Investigate unusual records in their original context: currency conversion, room mix, premium products and data-entry errors can produce similar visual signals.')+
        p('Deleting observations because they make the result inconvenient changes the estimand. If an exclusion is justified, state the rule, its reason and a sensitivity comparison retaining the flagged records.'),
        'Is an observation beyond Q3 + 1.5 × IQR necessarily invalid?',
        'No. The rule identifies unusual values relative to the sample’s central spread. A legitimate premium offer may belong in the population.')
    add('kde','A smooth curve adds assumptions',
        p('A kernel density estimate places a small smooth bump around each observed value and averages the bumps. Its bandwidth controls smoothing: a small bandwidth can chase noise; a large one can erase structure. A violin plot mirrors a smoothed density, so its width is not a direct count of observations.')+
        line_chart(d['kde']['x'],{'Gaussian KDE':d['kde']['density']},'Smoothed synthetic price distribution','Nightly price (CU)','Density per CU')+
        p(f'The lab’s Gaussian KDE uses its default Scott bandwidth, corresponding to a kernel SD of {fmt(d["kde"]["bandwidth_cu"])} CU. The displayed grid is only a sampled curve, not the calculation used for exact event shares. Gaussian kernels can assign density below zero, which is outside the support of prices. A log-scale model or boundary correction may be more appropriate near a hard boundary.'),
        'Does a violin with the same displayed width mean two groups have the same number of rows?',
        'Not generally. Many plotting tools normalize each group’s density separately. Show sample sizes and state the width convention.')
    add('attach-features','Attach group labels without duplicating observations',
        p('Before comparing towns or refund policies, attach attributes at the correct level. If several price observations belong to one lodging, a lodging dimension should have one row per lodging. A many-to-one join is appropriate only if the attribute is stable across the quoted dates; otherwise the key also needs time.')+
        p('The current lab generates each quote with its group label directly, so no external join is needed. In an operational workflow, validate the dimension key, check unmatched rows and compare counts before and after joining. A duplicate feature record would give some prices extra weight and distort both the distribution and the group mean.')+
        ul('Verify common currency, stay length and room specification.','Hold the time window and eligibility rules constant.','Report missing attribute matches rather than silently dropping them.','Retain row IDs so an apparent group difference can be traced back to observations.'),
        'A duplicate feature row only repeats information. Why can it still change the result?',
        'The join repeats the associated price observations too, increasing their statistical weight. Repeated values are not harmless if later counts and averages include them.')
    add('fair-groups','Compare unequal groups on a common basis',
        p('Use common axes and common definitions. Count histograms answer how many observations occur; normalized histograms answer where a group’s probability mass lies. Equal visual area can make unequal-size groups easier to compare, but the sample size must remain visible. Otherwise the more uncertain small group can appear equally well supported.')+
        table(['Town','n','Mean CU','Median CU','Q1 CU','Q3 CU'],[[r['town'],r['n'],fmt(r['mean']),fmt(r['median']),fmt(r['q1']),fmt(r['q3'])] for r in g],'Comparable synthetic group summaries')+
        bars([r['town'] for r in g],[100*r['proportion'] for r in g],'Synthetic quote shares at or below 140 CU','Percent within town')+
        p('A mean difference can arise from group composition rather than a uniform shift affecting every offer. Compare central spread and tails as well as centers. None of these descriptive summaries includes sampling uncertainty yet; Lesson 3 adds that layer.'),
        'Why keep the same price axis for every town?',
        'Changing axes can exaggerate or conceal differences. Common units, limits and bin definitions make visual comparisons interpretable.')
    add('budget-decision','Turn a distribution into a bounded budget statement',
        p('A budget needs a tolerance for overruns, not just a central value. Ask whether the decision is about expected spending, the share under a cap, or a high quantile that protects against expensive cases. These lead to different summaries. A mean can sit below a cap while many individual quotes exceed it.')+
        p(f'Across this synthetic mix, {100*e["p_under"]:.1f}% of quotes are at most 140 CU. The overall median is {fmt(s["median"])} CU, and the middle half spans {fmt(s["q1"])}–{fmt(s["q3"])} CU. Those numbers describe the generated mix; they are not a guarantee about the next real trip.')+
        ul('For expected total cost: use a relevant mean and state the volume assumption.','For a booking cap: report the event definition and the within-group share.','For unusually costly cases: inspect upper quantiles and the process generating the tail.','For a recommendation: state which costs and constraints remain unmeasured.'),
        'What is missing from “the average is below budget, so the budget is sufficient”?',
        'The variability, probability of exceeding the cap, relevant population mix and the decision-maker’s tolerance for an overrun.')
    add('events','A probability needs a defined event and sample space',
        p('An empirical proportion describes observed rows. A probability model describes possible outcomes under assumptions. They connect through sampling, but they are not interchangeable. Define A = quote ≤ 140 CU and R = refundable. The table below is the full synthetic sample space for these two binary events.')+
        table(['Refund terms','A: ≤140 CU','Not A: >140 CU','Total'],[['Refundable',a,b,a+b],['Not refundable',c,z,c+z],['Total',a+c,b+z,d['n']]],'Synthetic event counts')+
        formula('P(A ∪ R) = P(A) + P(R) − P(A ∩ R)')+
        p('Mutually exclusive events cannot occur together. Independent events satisfy P(A ∩ R) = P(A)P(R). Nontrivial mutually exclusive events are not independent: learning that one occurred rules out the other. For a continuous model, probability at one exact point is zero even when its density is high.'),
        'Are “refundable” and “at most 140 CU” mutually exclusive?',
        f'No. Their intersection contains {a} generated quotes. A row can have both properties.')
    add('conditional','Conditioning changes the denominator; Bayes reverses it',
        p(f'Among refundable offers, {100*e["p_under_given_refund"]:.1f}% cost at most 140 CU. Among offers at most 140 CU, {100*e["p_refund_given_under"]:.1f}% are refundable. These are different conditional probabilities because they condition on different groups.')+
        formula('P(A | R) = P(A ∩ R) / P(R); P(R | A) = P(A | R)P(R) / P(A)')+
        p(f'For the first probability the denominator is {a+b}; for the reverse it is {a+c}. Bayes’ rule connects them through the base rates. The same conditioning logic applies to means: the average refundable quote is {fmt(e["conditional_mean_refund"])} CU, compared with {fmt(e["conditional_mean_nonrefund"])} CU among nonrefundable quotes.')+
        p('The generator makes refund status independent of price within every town. Finite samples will still show accidental differences. An observed conditional difference is not automatically proof that the population probabilities differ, and neither conditional probability alone describes a causal effect of refund terms.'),
        'If P(A | R) is high, must P(R | A) also be high?',
        'No. The reverse probability also depends on how common refundable offers are. Confusing the two drops the base-rate information.')
    add('expectation','Expected value is a probability-weighted average',
        p('A separate authored service-reward model has three possible net rewards. Unlike the quote sample, these probabilities are stipulated, not estimated. Multiply each reward by its probability and sum. An expected value can lie between outcomes and need not be possible in any single trial.')+
        table(['Net reward CU','Probability','Contribution to E[X]'],[[v,pr,fmt(v*pr)] for v,pr in zip(rw['values'],rw['probabilities'])],'Synthetic service-reward model')+
        formula(f'E[X] = Σ x p(x) = {fmt(rw["mean"])} CU; Var(X) = E[(X − E[X])²] = {fmt(rw["variance"])} CU²')+
        p(f'The SD is {fmt(rw["sd"])} CU. For n independent repetitions, the expected total is nE[X] and its variance is nVar(X). Expected values add even without independence, but variances then need covariance terms. A favorable expectation does not eliminate loss risk, cash-flow constraints or dislike of volatility.'),
        'Could the model’s expected reward be received in a single trial?',
        f'Not here: {fmt(rw["mean"])} CU is not one of the three outcomes. It is a long-run probability-weighted average under the model.')
    add('families','Choose a distribution from the mechanism and support',
        p('A distribution family is a claim about a process. A binomial model counts successes in a fixed number of independent trials with one success probability. A Poisson model counts events over exposure under a stable rate and appropriate independence. A normal model describes an unbounded continuous quantity; an exponential model describes nonnegative waiting times under a constant hazard.')+
        table(['Model and assumption','Calculated model probability'],[['Binomial: 10 trials, p = 0.25; at least 4 successes',fmt(m['binom_p_ge_4'],4)],['Poisson: mean count 2; zero events',fmt(m['poisson_p_zero'],4)],['Exponential: mean wait 5; wait above 10',fmt(m['exp_p_gt_10'],4)],['Normal: within one population SD of its mean',fmt(m['normal_within_1sd'],4)]],'Fresh calculations under stated synthetic probability models')+
        bars(d['binom']['k'],d['binom']['prob'],'Binomial model: n = 10 and p = 0.25','Probability mass')+
        p('The binomial bars are probability masses at integers, not a continuous density. Check support before shape: a normal approximation can assign impossible negative counts or prices. Dependence and changing rates can invalidate a family even when a histogram looks plausible.'),
        'Would a binomial model automatically fit repeated outcomes from the same customer?',
        'No. Repeated behavior can be dependent, and customers can have different success probabilities. The mechanism needs examination before using the formula.')
    add('tails','Positive skew and tail risk need separate attention',
        p('A lognormal variable is the exponential of a normal variable. It is positive and right-skewed. Multiplicative variation makes it a useful teaching model for prices and sizes, but shape alone does not establish that it is correct. Its mean is larger than its median when the log variance is positive.')+
        formula(f'If log X ~ Normal(4.7, 0.4²), median(X) = exp(4.7) = {fmt(m["lognormal_median"])}; E[X] = exp(4.7 + 0.4²/2) = {fmt(m["lognormal_mean"])}')+
        p(f'A Pareto model with minimum 50 and shape α = 1.5 has mean {fmt(m["pareto_mean_alpha_15"])} and P(X &gt; 200) = {fmt(m["pareto_tail_200"] ,4)}. Its variance is infinite. A Pareto mean exists only for α &gt; 1; its variance exists only for α &gt; 2. Thus the usual finite-variance CLT and familiar standard-error formulas do not automatically apply.')+
        p('Large extremes can dominate averages even when the central histogram appears stable. Investigate tail mechanisms, aggregation and top-coding. Do not fit a tail model merely to obtain a dramatic story, and do not apply “normal because n is large” without checking the assumptions relevant to the estimator.'),
        'Does a finite sample SD prove the population variance is finite?',
        'No. Every finite dataset can have a finite calculated SD even when the assumed population model has infinite variance.')
    add('firm-unit','Introduce a new case without switching indicators silently',
        p(f'We now move to {f["n"]} fictional firms. Each row has a noisy practice score between 1 and 5, a simulated employee count and a sector label. A latent trait influences both score and size, while independent noise and sector composition add variation. Those assumptions deliberately create association; they are not evidence from real firms.')+
        p('The practice score is a proxy, not the latent concept itself. Measurement error can attenuate or otherwise distort associations. Employee count measures scale, not profit, productivity or performance. Renaming it “success” would make an unsupported conceptual substitution.')+
        scatter(f['points'],'Synthetic firms: practice score and employees','Practice score','Employee count')+
        p('Inspect each variable’s support and the joint pattern before calculating one coefficient. Notice the fan of individual outcomes and the long size tail; a single high-scoring firm need not be larger than every low-scoring firm.'),
        'Does a practice score directly measure the quality of every management decision?',
        'No. It is a noisy, limited proxy. Interpretation must stay with what the score actually captures and acknowledge the measurement process.')
    add('within-group','Compare each group on its own denominator',
        p('Define a “large firm” as employee count ≥ 60, then calculate the share within each score band. The band boundaries are lower: score &lt; 2.5; middle: 2.5 ≤ score &lt; 3.5; higher: score ≥ 3.5. A threshold is a chosen definition, not a natural law.')+
        table(['Score band','Firms','At least 60 staff','Within-band share'],[[r['band'],r['n'],r['large'],f'{r["large_share"]*100:.1f}%'] for r in f['bands']],'Synthetic firm sizes by practice-score band')+
        bars([r['band'] for r in f['bands']],[r['large_share']*100 for r in f['bands']],'Share with at least 60 employees, by synthetic score band','Percent of firms in band')+
        p('P(large | higher score) differs from P(higher score | large). Use the row or column denominator appropriate to the question. Check sensitivity to reasonable thresholds, but disclose exploratory choices rather than selecting whichever boundary produces the strongest narrative.'),
        'What changes if “large” is redefined from 60 to 80 employees?',
        'The event changes, so its counts and probabilities must be recalculated. The old percentages no longer answer the new question.')
    add('composition','Group averages can hide overlap and composition',
        p('A higher group mean does not mean every observation in that group exceeds every observation in another. It can coexist with substantial overlap. A pooled association can even reverse within strata if groups have different compositions. The authored counts below make that reversal visible without relying on a real-world dataset.')+
        table(['Sector','Group','Successes','Trials','Share'],[[r['sector'],r['group'],r['success'],r['n'],f'{100*r["success"]/r["n"]:.1f}%'] for r in d['simpson']],'Synthetic composition example')+
        p(f'Training has the higher share within both sectors. Pooled across sectors, Training is {100*d["simpson_pooled"]["Training"]:.1f}% and Comparison is {100*d["simpson_pooled"]["Comparison"]:.1f}%. Training contains many more difficult-sector cases. The pooled groups do not compare the same mix.')+
        p('This is a descriptive warning, not a rule that every adjustment is correct. The decision and causal structure determine which variables should be conditioned on. Automatically controlling for every available variable can introduce other biases.'),
        'Do these counts prove training causes improvement?',
        'No. They illustrate composition reversal. Causal interpretation also requires a defensible assignment mechanism and appropriate adjustment choices.')
    add('binned-scatter','A binned mean is not an individual firm',
        p('Divide score into ten equal-count groups and plot the mean score against mean employee count in each group. This binned scatter clarifies the average pattern but hides within-bin variation and can make a noisy individual relationship look tight. Equal-count groups need not have equal score widths.')+
        scatter([[r['score'],r['size']] for r in f['bins']],'Ten binned means from 240 synthetic firms','Mean score in bin','Mean employees in bin')+
        p('Each plotted point summarizes 24 firms. Compare it with the individual scatter before drawing conclusions about prediction. Binning can also move boundaries or conceal nonlinear features. Report the binning rule and do not calculate an individual-level correlation from the ten averages as if they were the original observations.'),
        'Why might the correlation of binned averages be larger than the individual correlation?',
        'Averaging suppresses within-bin noise. The resulting coefficient describes an aggregated relationship, not the precision of predictions for individual firms.')
    add('covariance','Keep paired deviations together',
        p('Covariance asks whether observations above their own variable’s mean also tend to be above the other variable’s mean. Keep the original pairs: separately sorting the two columns creates a different relationship. Positive products contribute positive covariance, while opposite-signed deviations contribute negative covariance.')+
        formula('Sample covariance sₓᵧ = Σ[(xᵢ − x̄)(yᵢ − ȳ)] / (n − 1)')+
        table(['x','y','x − mean(x)','y − mean(y)','Product'],[[1,2,-1,-1,1],[2,2,0,-1,0],[3,5,1,2,2]],'Authored synthetic paired-deviation calculation')+
        p(f'The three-pair example has covariance {fmt(f["toy_cov"])}. In the firm sample, covariance is {fmt(f["cov"])} score-unit × employees. Covariance changes if either variable’s scale changes, so its magnitude is difficult to compare across differently measured relationships.'),
        'What would happen if you sorted the employee column but left scores in their original order?',
        'You would destroy the original pairing and calculate an association for fabricated pairs. The rows, not the separate marginal distributions, define covariance.')
    add('correlation','Correlation removes units, not complexity',
        p(f'Pearson correlation is covariance divided by the product of sample SDs. The synthetic score–employee correlation is {fmt(f["r"],3)}. Using log employee count changes it to {fmt(f["r_log_size"],3)} because a nonlinear transformation changes the relationship being summarized. Positive rescaling alone would not change correlation.')+
        formula('r = sₓᵧ / (sₓ sᵧ), with −1 ≤ r ≤ 1 when both variables vary')+
        scatter(f['nonlinear_points'],'Synthetic counterexample: y = x²','x','y')+
        p(f'This symmetric U-shaped example has r = {f["nonlinear_r"]:.3f}, up to floating-point rounding, despite a deterministic relationship. Zero correlation rules out neither dependence nor useful prediction. Pearson r describes linear association and can be sensitive to extreme points and restricted ranges. A correlation matrix still needs scatterplots, sample sizes and missing-data rules.'),
        'If two variables have correlation zero, can one help predict the other?',
        'Yes. Here y = x² predicts y exactly, while the positive and negative linear contributions cancel.')
    add('causality','Description, prediction and intervention are different tasks',
        p('Description summarizes the observed joint distribution. Prediction uses available features to forecast outcomes in new observations and requires out-of-sample validation. Causal inference asks what would change if an intervention altered one factor while the relevant alternatives were held appropriately comparable.')+
        p('The firm generator includes a common latent cause of score and size. Therefore an association is built in even though the script specifies no causal arrow from the measured score to employee count. The simulation exposes a general risk: raising a reported score does not necessarily change the underlying process.')+
        ul('Confounding: another factor influences both variables.','Reverse direction: size can influence resources available for practices.','Selection: the observed firms differ from the population of interest.','Measurement: scores and scale measures imperfectly represent the intended concepts.')+
        p('A large coefficient can also be operationally unimportant, while a modest association may be useful for a specific forecast. Evaluate the decision, cost of errors and stability across populations rather than ranking importance by correlation alone.'),
        'What additional evidence would support a claim about changing management practice?',
        'A credible intervention or quasi-experimental design, clear treatment and outcome definitions, defensible assumptions and a relevant target population. Correlation alone is insufficient.')
    add('distribution-handoff','Deliver a distribution-aware decision brief',
        p('A useful brief starts with the population and observation, then reports a small set of summaries selected for the decision. Name the event and denominator for every percentage. Show at least one view of shape and one view of variation. Distinguish an observed frequency from a stipulated probability model.')+
        table(['Claim type','What to include'],[['Budget description','Price definition, mean/median, spread, cap share and n'],['Group comparison','Common scope, within-group denominators and composition'],['Probability model','Support, mechanism, parameters and calculated event'],['Association','Paired unit, scatterplot, coefficient and noncausal limitation']],'A reusable Lesson 2 handoff structure')+
        p(f'Example: “In {d["n"]} simulated quotes, {100*e["p_under"]:.1f}% are at most 140 CU. The median is {fmt(s["median"])} CU, with a right tail and meaningful town differences. These results describe the authored scenario, not current hotel prices. For a real budget, validate the market frame and quantify uncertainty.”')+
        p('Next, Lesson 3 separates variation among observations from uncertainty in an estimate, and asks which population claims a sampling design can support.'),
        'What should you avoid adding to this descriptive brief?',
        'A causal explanation, a population certainty claim or a real-market recommendation that the synthetic design and analysis do not support.')
    assert len(sections)==24
    render_lesson(2,'Read patterns without overclaiming','Explore distributions, probability models and associations while keeping units, denominators and assumptions visible.',sections)
    (ROOT/'content'/'lesson2-outline.json').write_text(json.dumps([x['title'] for x in sections],indent=2)+'\n')

def build3(d):
    r=d['risk'];sm=d['small'];w=d['wait'];rs=d['resampling'];cl=d['cluster'];t=d['test'];pa=d['paired'];we=d['welch'];mp=d['multiplicity']
    sections=[];add=lambda *args:sections.append(sec(*args))
    add('population','An observed pattern is not yet a population claim',
        p('Inference connects an observed sample to a target quantity under a sampling or assignment model. The quantity might be a mean waiting time, an event probability or a mean paired price difference. Name it before choosing a formula. Distinguish uncertainty due to sampling from bias due to coverage, measurement or selection.')+
        p('This lesson uses several separate synthetic cases: a fictional Lumen activity index, waiting times, a binomial quality check and paired retail quotes. Their generators are fully specified, so assumptions can be tested against known mechanisms. They do not describe actual financial markets, customers or retailers.')+
        ul('Independent: one observation does not carry extra information about another under the model.','Identically distributed: observations share the relevant distribution.','Representative: the design supports the intended population claim.','IID does not automatically establish representativeness, and representativeness does not imply independence.'),
        'If a million observations all come from one unrepresentative location, what does a tiny standard error omit?',
        'The systematic difference between that location and the target population. A sampling-error calculation does not measure every source of error.')
    add('sessions','A calendar row is not automatically an observation',
        p(f'The Lumen index generator starts from a {d["calendar_days"]}-day calendar, retains weekdays, removes three planned closures and uses the first {d["sessions"]} sessions. Closed days have no index observation. We do not fill them with repeated values or zeros merely to make the calendar rectangular.')+
        table(['Session date','Synthetic index','Change from prior session (%)'],[[z['date'],fmt(z['index'],3),'not defined' if z['change_pct'] is None else fmt(z['change_pct'],3)] for z in d['session_excerpt']],'First eight generated Lumen sessions')+
        p('The unit is a session-to-session change. A Monday change can span more elapsed calendar time than a Tuesday change. In this authored model, every session change has the same distribution by construction. A real application would need to justify or revise that assumption for gaps and closures.')+
        p('Forward-filling creates artificial zero changes on closed days and changes the denominator. Interpolation invents intermediate observations. Either can be useful for a clearly stated engineering purpose, but neither is neutral for inference.'),
        'Why is the first change missing rather than zero?',
        'There is no preceding observed index level in this dataset. Zero would assert a known absence of change, which is different from an undefined comparison.')
    add('changes','Convert levels into a consistently defined change',
        p('A difference in index points depends on the starting level. A simple proportional change divides by that starting level. A log change is the difference of log levels and is additive across time. These are related measures, but they are not numerically identical.')+
        formula('Simple change Rₜ = (Pₜ − Pₜ₋₁)/Pₜ₋₁; log change gₜ = log(Pₜ/Pₜ₋₁); Rₜ = exp(gₜ) − 1')+
        line_chart(d['index_path']['x'],{'Lumen index':d['index_path']['level']},'Every tenth synthetic Lumen index observation','Session number','Index units')+
        p('The generator draws IID normal log changes with mean 0.0003 and SD 0.011, then compounds them from an index of 100. The event analysis uses simple changes, not log changes. Percent values multiply proportions by 100; mixing those units would move a threshold by a factor of 100.'),
        'Does a 10% rise followed by a 10% fall return an index to its starting level?',
        'No. The compound factor is 1.10 × 0.90 = 0.99, a net 1% fall. Simple percentage changes do not generally add over time.')
    add('threshold','A threshold probability and a quantile reverse the question',
        p(f'Define an event before counting: a simple session change below −1.2%. There are {r["count"]} such events among {r["n"]} changes, giving an observed share of {100*r["proportion"]:.2f}%. The unknown model probability p is not identical to that one sample proportion.')+
        formula('Fixed threshold: estimate p = P(R &lt; −0.012). Fixed tail probability: find q such that P(R ≤ q) = 0.05.')+
        p(f'The sample fifth percentile is {100*r["quantile_05"]:.3f}%. It answers a different question from the event share. A lower-tail quantile can be converted to a positive loss magnitude under an explicit sign convention, but it is not a worst-case bound. Outcomes beyond the quantile can be much worse.')+
        p('Choose the threshold from the decision, not by scanning for the most striking result. Report strict versus inclusive comparisons and the quantile convention. The lab uses linear interpolation for sample quantiles.'),
        'Is the proportion below −1.2% the same as the fifth-percentile change?',
        'No. One fixes a change threshold and estimates probability; the other fixes probability and estimates a change threshold. They have different units.')
    add('sampling','One sample, many possible estimates',
        p('A sampling distribution describes an estimator across repeated hypothetical samples. It is not the distribution of individual observations. The waiting-time model here is 4 + Exponential(mean 8), so its population mean is 12 and population SD is 8. It is strongly right-skewed, but averages become more stable as sample size grows.')+
        table(['Sample size','Mean of 4,000 sample means','SD of sample means','Theory: 8/√n','Skewness of sample means'],[[v['n'],fmt(v['mean'],3),fmt(v['sd'],3),fmt(v['theory_se'],3),fmt(v['skew'],3)] for v in d['sampling']],'Fresh Monte Carlo sampling distributions from a synthetic population')+
        bars([str(v['n']) for v in d['sampling']],[v['sd'] for v in d['sampling']],'Variability of synthetic sample means falls with n','SD of sample mean')+
        p('The Monte Carlo values do not exactly equal theory because the simulation itself uses a finite number of repetitions. That difference is computational sampling variation, not evidence against the formulas.'),
        'When plotting 4,000 sample means, what does one point on the horizontal axis represent?',
        'A mean from one whole simulated sample, not one individual waiting time. The unit of analysis on that plot is the estimator.')
    add('standard-error','Separate variability in observations from precision in a mean',
        p('The SD measures spread among observations. The SE measures spread of an estimator across repeated samples under a design. Under IID sampling with finite variance, the sample mean has SE estimated by s/√n. More observations can stabilize the mean without making individuals more similar.')+
        table(['Calculation','Five-value example: 7, 9, 10, 12, 17'],[['n',sm['n']],['Mean',fmt(sm['mean'])],['Sample SD, denominator n−1',fmt(sm['sd'],4)],['SE = SD/√n',fmt(sm['se'],4)]],'Fresh arithmetic for a synthetic small sample')+
        formula('For Bernoulli outcomes: p̂ = k/n; approximate SE(p̂) = √[p̂(1−p̂)/n]')+
        p('The two divisions serve different purposes. Dividing squared deviations by n − 1 estimates observation variance; dividing that variance by n estimates variance of the mean under independence. If observations are clustered or serially correlated, the second step is generally wrong without covariance terms.'),
        'To halve an IID mean’s SE while holding population spread fixed, how much data is needed?',
        'About four times the sample size, because SE scales as 1/√n. This improves random precision, not representativeness or measurement quality.')
    add('interval','Build a confidence interval with the right multiplier',
        p(f'For the five-value sample, the 95% t multiplier with four degrees of freedom is {fmt(sm["critical"],4)}. The interval is {fmt(sm["low"],3)} to {fmt(sm["high"],3)}. A normal 1.96 multiplier would ignore uncertainty from estimating the SD in this small sample.')+
        formula('Mean CI = x̄ ± t₁₋α/₂,ₙ₋₁ × s/√n; use z only when its assumptions are justified')+
        p('The exact t result assumes IID normal observations. Approximate use for large samples requires appropriate regularity and is not guaranteed by a universal n threshold. A 95% confidence procedure covers the fixed population mean in 95% of repeated samples under its assumptions; it does not assign 95% probability to a fixed parameter after seeing one interval.')+
        p(f'In 3,000 fresh normal-population simulations, this lab’s t intervals covered the true mean in {100*d["coverage"]:.1f}% of repetitions. For the Lumen event share, a Wilson 95% interval is {100*r["wilson"][0]:.2f}% to {100*r["wilson"][1]:.2f}%. Wilson intervals handle boundaries better than a symmetric Wald interval; with only 1 event in 20 trials, the Wilson interval is {100*r["sparse_wilson"][0]:.2f}% to {100*r["sparse_wilson"][1]:.2f}%.'),
        'Does a 95% CI mean 95% of individual observations lie inside it?',
        'No. It is an interval for the population parameter, not an individual prediction interval. Individual outcomes are usually much more variable.')
    add('lln-clt','Keep convergence, normality and bias separate',
        p('The law of large numbers concerns convergence of an average toward an expectation under suitable conditions. It does not say every next observation moves the average closer. The central limit theorem describes the limiting shape of the centered, scaled mean, usually requiring finite variance in its elementary IID form. It does not make the underlying observations normal.')+
        formula('LLN: x̄ₙ → μ. IID finite-variance CLT: √n(x̄ₙ − μ)/σ → Normal(0,1).')+
        line_chart(d['lln']['n'],{'Running mean':d['lln']['means'],'Population mean':[12]*len(d['lln']['n'])},'One fresh synthetic running-mean path','Number of observations','Waiting-time units')+
        p('Unbiasedness is an expectation property at a given sample size. Consistency is a large-sample convergence property. Efficiency compares uncertainty among estimators under a model. None of these eliminates coverage or measurement bias. An estimator can converge precisely to the wrong target if the data-generating population is wrong.'),
        'Does the CLT imply a skewed waiting-time histogram becomes normal when you collect more rows?',
        'No. It concerns the standardized sampling distribution of averages. More data can reveal the original skewed population more clearly.')
    add('subsamples','Smaller subsets answer a different stability question',
        p(f'We generate one sample of {w["n"]} waiting times and repeatedly select {rs["subset_size"]} distinct observations without replacement. Across {rs["B"]:,} subsets, the SD of the means is {fmt(rs["subset_sd"],3)}. This measures variability of a smaller-sample statistic conditional on the observed finite set, not the original 80-observation mean’s SE.')+
        formula('For simple random subsets of size m from n fixed observed values: SD(subset mean) = s × √[(1 − m/n)/m]')+
        p(f'The finite-population formula gives {fmt(rs["subset_theory"],3)} here. The finite correction matters because each subset uses a substantial share of the observed pool. A subsample without replacement differs from a bootstrap sample both in size and in whether observations may repeat.')+
        p('Subsampling can reveal sensitivity to which records are retained. It is not automatically a confidence-interval procedure for the original estimator. Some formal subsampling methods rescale carefully, but that is a separate design requiring explicit theory.'),
        'Can the central 95% of these 20-row subset means be labeled a 95% CI for the original 80-row mean?',
        'Not without additional justification and scaling. The subset distribution targets a different sampling design and sample size.')
    add('bootstrap','Resample at the original size with replacement',
        p(f'The ordinary bootstrap draws {w["n"]} rows with replacement from the observed sample, computes the statistic and repeats {rs["B"]:,} times. A row may appear several times or not at all. Treating the empirical distribution as an approximation to the population lets the resampled statistics approximate sampling variation under IID conditions.')+
        histogram(rs['edges'],rs['counts'],'Bootstrap means from one synthetic waiting-time sample','Bootstrap replicate count')+
        p(f'The bootstrap SE is {fmt(rs["bootstrap_se"],3)}. The percentile interval uses the 2.5th and 97.5th percentiles of bootstrap means: {fmt(rs["bootstrap_ci"][0],3)} to {fmt(rs["bootstrap_ci"][1],3)}. A standard-error interval uses the bootstrap SD with an appropriate multiplier instead. Those are distinct methods, not interchangeable labels.')+
        p('More bootstrap repetitions reduce Monte Carlo noise in the approximation; they do not add original observations or repair selection bias. Ordinary bootstrap performance can be poor for small samples, extreme quantiles, boundaries or heavy-tailed statistics.'),
        'Why sample with replacement rather than merely shuffle the original 80 rows?',
        'A shuffle preserves the mean exactly. Replacement changes the empirical weights, producing variation in the resampled statistic.')
    add('dependence','Match resampling and standard errors to dependence',
        p('If observations share a site, household, day or product, resampling individual rows can break the dependence structure. Use a design that preserves the relevant unit, such as resampling independent clusters or appropriately chosen time blocks. The method must match the claim and the actual collection process.')+
        table(['Quantity','Calculated synthetic value'],[['Measurements',cl['n']],['Independent groups',cl['clusters']],['Naive row-level mean SE',fmt(cl['naive_se'],3)],['SE from group means',fmt(cl['cluster_se'],3)],['Authored within-group ICC',fmt(cl['population_icc'],2)],['Equal-size design effect 1 + (8−1)ICC',fmt(cl['design_effect'],2)]],'Synthetic clustered measurements: 30 groups of eight')+
        p('The cluster example uses a shared normal shock with SD 4 and individual noise with SD 3. Its population ICC is 16/(16+9). The group-mean SE estimates variability across 30 independent groups. Equal group sizes make the average of group means equal the overall mean; unequal sizes require more care about weighting and the estimand.')+
        p(f'For the separate IID waiting sample, analytic SE is {fmt(w["se"],3)}, bootstrap SE is {fmt(rs["bootstrap_se"],3)} and smaller-subset SD is {fmt(rs["subset_sd"],3)}. Their differences should be explained by designs, not hidden by selecting whichever looks most reassuring.'),
        'Why can 240 clustered measurements carry much less information than 240 independent ones?',
        'Measurements within a group share a shock. Repeated information does not reduce uncertainty at the IID rate, so the independent group count and within-group dependence matter.')
    add('representativeness','Precision cannot make the wrong period representative',
        p('A confidence interval describes uncertainty under a model and design. It does not cover every possible discrepancy between the sample and the decision setting. A stable historical mean can be irrelevant after a change in technology, customer mix, regulation or economic conditions. A narrow interval from an obsolete period can therefore be precisely misleading.')+
        p('In the Lumen simulation, the log-change mechanism is constant by construction, so IID inference is a conditional teaching calculation. In an applied time series, examine serial correlation, changing variance, structural breaks and the sampling window. Independence of levels is especially implausible when levels are cumulative; the modeled changes, not the levels, are the potential IID objects.')+
        ul('Name the population and period the data represent.','Separate sampling error from measurement, selection and model uncertainty.','State whether stationarity or exchangeability is being assumed.','Describe what new evidence would change the recommendation.'),
        'What should accompany a precise estimate from an old sample?',
        'An explicit transportability limitation and evidence about whether the current decision setting shares the relevant mechanism and population.')
    add('hypotheses','Turn a benchmark into a testable population claim',
        p('A new quality-check scenario asks whether the long-run defect probability exceeds 10%. Specify H₀: p = 0.10 versus H₁: p &gt; 0.10, use 100 independent trials and fix α = 0.05 before seeing the count. For the composite null p ≤ 0.10, the largest rejection probability occurs at the boundary 0.10 under this monotone rule.')+
        formula(f'Rejection rule: reject H₀ when K ≥ {t["critical"]}, for K ~ Binomial(100, 0.10) under the boundary null')+
        p('The statistic is the defect count, with the sample size held fixed. The direction reflects the decision: an unusually high rate matters here. A two-sided question would have a different rejection region. Optional stopping, changing the threshold after inspection or testing several definitions alters the error guarantees.')+
        p('A test needs a sampling or assignment model. A spreadsheet containing 100 rows does not by itself establish independent Bernoulli trials with a common probability.'),
        'Can the alternative be changed to one-sided after seeing that the estimate is high?',
        'Not while claiming the original prespecified error control. Direction chosen after inspection is part of an adaptive procedure and must be accounted for.')
    add('errors','Choose which mistakes the rule controls',
        p('A Type I error rejects a true null. A Type II error fails to reject at a specified alternative. Power is one minus the Type II error probability at that alternative. There is no single power value without an effect size, sample size, variability and rejection rule.')+
        table(['Rule','Reject at count','False-alarm probability under p=0.10','Power under p=0.18'],[['Nominal α=0.05',t['critical'],fmt(t['actual_alpha'],4),fmt(t['power'][3],4)],['Nominal α=0.01',t['strict_critical'],'At most 0.01',fmt(t['strict_power_018'],4)]],'Exact synthetic binomial rejection rules')+
        p(f'The 5% rule’s actual null rejection probability is {100*t["actual_alpha"]:.2f}%, below the nominal cutoff because counts are discrete. Making the rule stricter reduces false alarms but also lowers detection at p = 0.18 for the same n. Increasing sample size can improve power without increasing the nominal Type I error.')+
        p('Which error is more costly depends on the decision. A safety screen, a product rollout and a scientific replication may require different thresholds and follow-up actions. Statistical error rates are design inputs, not moral guarantees.'),
        'Does α = 0.05 mean there is a 5% chance a particular rejection is wrong?',
        'No. It controls the long-run probability of rejection when the null model is true, not the posterior probability that the null is true after observing data.')
    add('pvalue','Follow the tail probability to the decision',
        p(f'The generated quality-check sample has {t["observed"]} defects out of {t["n"]}. Its one-sided exact p-value is {fmt(t["pvalue"],6)}: the null probability of observing at least that many defects. At α = 0.05, the prespecified rule {"rejects" if t["reject"] else "does not reject"} the boundary null.')+
        formula('p-value = P₀(K ≥ k observed), calculated under K ~ Binomial(100, 0.10)')+
        p('The p-value conditions on the null and model assumptions. It is not P(H₀ | data), the probability the result was “due to chance,” or the size of the practical effect. A small value indicates incompatibility with this null model; it does not diagnose which assumption is wrong.')+
        p('Failing to reject is also not proof of equality. A weak design may be unable to distinguish a useful range of alternatives. Report the observed effect and uncertainty alongside the decision rule, especially when operational costs depend on the magnitude.'),
        'Why must “equally or more extreme” follow the chosen alternative?',
        'A one-sided high-rate alternative counts the upper tail. A two-sided alternative must account for departures in both directions using a specified test definition.')
    add('power','Plan for the effect that would change the decision',
        p('Power is a property of the design evaluated at a specific true effect. Calculate it before collecting data for an effect large enough to matter. Post hoc “observed power” largely restates the p-value and is usually less useful than an effect estimate with an interval.')+
        line_chart(t['alternatives'],{'Power of fixed count rule':t['power']},'Exact power of the synthetic 100-trial test','True defect probability','Rejection probability')+
        p(f'The graph uses the same rejection threshold, K ≥ {t["critical"]}, at every alternative. Under p = 0.10 its rejection rate is the test’s actual size. At p = 0.18 its power is {100*t["power"][3]:.1f}%. The x-axis is a possible population probability, not a series of observed sample estimates.')+
        p('For a mean comparison, power depends on an effect in business units relative to variability, sample sizes, allocation and dependence. Decide what effect justifies action, then budget the data needed. Do not invent a “meaningful” effect merely to make the available sample appear adequate.'),
        'If power is 70% at a particular alternative, is every nonsignificant result proof the effect is absent?',
        'No. Even when that alternative is true, the design fails to reject about 30% of the time under its assumptions.')
    add('paired-data','A new case: compare the same products across channels',
        p(f'The retail case generates {pa["n"]} fictional products with an offline and online quote for each product at the same time and under the same assumed quantity and tax definition. Product base prices vary widely. Pairing uses the product, not arbitrary row order.')+
        table(['Product','Offline CU','Online CU','Online minus offline CU'],[[f'P{i+1:02d}',fmt(x),fmt(y),fmt(y-x)] for i,(x,y) in enumerate(pa['points'][:8])],'First eight newly generated matched product quotes')+
        p('The analysis unit is one matched product difference. Before pairing real data, verify exact product identity, package size, currency, availability, observation time and missing matches. Preserve exclusions and the unmatched count. A shared name alone may not identify the same product.')+
        p('The synthetic generator creates independent product differences, normally distributed with authored mean 0.45 and SD 1.55 CU. Product base prices create strong dependence between channels within a pair. Treating the two channel columns as independent would discard that design.'),
        'What is the independent unit for the paired test in this example?',
        'The product-level difference. The two prices within a product are deliberately related and must remain paired.')
    add('paired-spread','A small mean can hide a wide range of differences',
        p(f'Observed product differences range from {fmt(pa["min"])} to {fmt(pa["max"])} CU, while their mean is {fmt(pa["mean"] ,3)} CU. A mean near zero could conceal offsetting positive and negative differences. Inspect the paired difference distribution, not only the two marginal price distributions.')+
        scatter([[i+1,v] for i,v in enumerate(pa['differences'])],'Synthetic product-level online-minus-offline differences','Product index','Difference (CU)')+
        p('The plot keeps every generated product. A central zoom can be useful, but it must preserve the original sample definition and disclose what lies outside the view. Do not discard large differences simply because a zoom makes them inconvenient. Investigate whether they reflect package mismatch, promotions, timing or a genuine tail.')+
        p('Product order is arbitrary here; no time trend should be inferred from left-to-right position. For a paired t procedure, normality concerns the differences, not a requirement that both original price columns be separately normal.'),
        'Does a mean difference of zero imply every product has equal prices?',
        'No. Positive and negative product differences can cancel. The mean is one summary of the difference distribution, not an equality statement for every pair.')
    add('paired-test','Measure the mean difference in standard errors',
        p('A paired t test is a one-sample t test on dᵢ = onlineᵢ − offlineᵢ. Under a zero-mean null, divide the sample mean difference by its SE. With independent normally distributed differences, the statistic follows a t distribution with n − 1 degrees of freedom under the null.')+
        formula('t = (d̄ − 0)/(s_d/√n); paired 95% CI = d̄ ± t₀.₉₇₅,ₙ₋₁ × s_d/√n')+
        table(['Quantity','Computed synthetic result'],[['Pairs',pa['n']],['Mean difference CU',fmt(pa['mean'],6)],['SD of differences CU',fmt(pa['sd'],6)],['SE CU',fmt(pa['se'],6)],['t statistic',fmt(pa['t'],6)],['Degrees of freedom',pa['n']-1],['Two-sided p-value',fmt(pa['p'],7)],['95% CI CU',f'{fmt(pa["low"],6)} to {fmt(pa["high"],6)}']],'Paired test calculated from the generated raw pairs')+
        p('The p-value compares the magnitude |t| with both tails of the null t distribution. Pairing can improve precision because stable product-level differences in price level cancel. That benefit depends on preserving correct matches and a defensible independence structure across products.'),
        'What error results from pairing one product’s online quote with another product’s offline quote?',
        'The differences no longer represent the intended matched comparison. Both the estimand and the uncertainty calculation become misleading.')
    add('paired-meaning','A significant average difference is not a universal price claim',
        p(f'The paired 95% interval, {fmt(pa["low"],3)} to {fmt(pa["high"],3)} CU, excludes zero. Under the authored paired model, that supports a nonzero average channel difference. It does not say every online quote is higher, that the gap is important, or that switching channels causes this difference in a real population.')+
        p('An interval makes the magnitude visible. Compare its range with a decision-relevant tolerance established before inspecting results. Also separate uncertainty about the population average from variability across individual products. A narrow mean interval can coexist with large positive and negative individual differences.')+
        p('For a real operational recommendation, consider transaction fees, travel or delivery costs, availability, timing and the relevant product mix. These can dominate a small average quote difference. The synthetic exercise deliberately excludes those complications so the statistical distinction stays visible.'),
        'Can a statistically detectable difference still be too small to matter operationally?',
        'Yes. A test against exactly zero can reject even when the plausible mean differences all lie within a prespecified practically negligible range.')
    add('welch','Use an independent-groups method when pairing is absent',
        p('A separate queue example has two independent groups, with different sample sizes and variances. No natural one-to-one match exists. Welch’s t method estimates uncertainty without forcing equal population variances. A paired test would invent relationships that the design does not contain.')+
        formula('SE(x̄_A − x̄_B) = √(s_A²/n_A + s_B²/n_B); use Welch–Satterthwaite degrees of freedom')+
        table(['Quantity','Group A','Group B'],[['n',we['n_a'],we['n_b']],['Mean',fmt(we['mean_a'],4),fmt(we['mean_b'],4)],['SD',fmt(we['sd_a'],4),fmt(we['sd_b'],4)]],'Independent synthetic queue samples')+
        p(f'The estimated A − B difference is {fmt(we["difference"],4)}, SE {fmt(we["se"],4)}, with {fmt(we["df"],3)} approximate degrees of freedom. The t statistic is {fmt(we["t"],4)}, two-sided p-value {fmt(we["p"],5)}, and 95% CI {fmt(we["ci"][0],4)} to {fmt(we["ci"][1],4)}. The full formula and raw sample generation are in the lab.')+
        p('Welch’s method allows unequal variances; it does not repair dependence, severe distributional problems or a biased comparison. Noninteger degrees of freedom are expected from the approximation.'),
        'Should two groups be paired just because both have measurements in the same units?',
        'No. Pairing comes from the collection design or a justified matching process, not shared units or a convenient spreadsheet layout.')
    add('equivalence','Set direction and a practical-equivalence margin in advance',
        p('Testing “different from zero” is not the same as testing “small enough to treat as practically equivalent.” Equivalence uses a prespecified margin ±Δ. The two one-sided tests (TOST) reject mean ≤ −Δ and mean ≥ +Δ. At α = 0.05, both must reject; equivalently, a compatible 90% two-sided CI must lie strictly within the margin.')+
        formula(f'Practical margin: −{fmt(pa["margin"])} &lt; μ_difference &lt; +{fmt(pa["margin"])} CU; 90% CI: [{fmt(pa["ci90"][0],3)}, {fmt(pa["ci90"][1],3)}]')+
        p(f'For the synthetic paired case, the two one-sided p-values are {pa["tost_p"][0]:.3g} and {pa["tost_p"][1]:.4g}. Both are below 0.05, and the 90% CI is inside ±{fmt(pa["margin"])} CU. This supports equivalence of the average under the declared margin, while the 95% CI still excludes zero. There is no contradiction: “nonzero” and “practically small” can both be true.')+
        p('The margin is an authored teaching choice, not a discovered business standard. In practice it must come from consequences, measurement resolution or an accepted policy before the data are inspected. Equivalence of the mean is not interchangeability for every product.'),
        'Why is a nonsignificant ordinary difference test not enough to show equivalence?',
        'Its interval may be wide enough to include both large beneficial and large harmful differences. Equivalence requires ruling out effects beyond a meaningful margin, not merely failing to reject zero.')
    add('multiplicity','Control the family, not just one reported p-value',
        p(f'With 20 independent true-null tests at α = 0.05, the probability of at least one false rejection is 1 − 0.95²⁰ = {100*mp["fwer_20_independent"]:.1f}%. Dependence changes that exact calculation, but repeated searching still changes the inferential procedure. The family includes relevant unreported tests, outcomes and analytic variants, not only the final table.')+
        table(['Hypothetical test','Raw p','Holm-adjusted p','Reject at family α=.05?'],[[f'Test {i+1}',fmt(v,3),fmt(mp['holm'][i],3),'Yes' if mp['holm'][i]<=.05 else 'No'] for i,v in enumerate(mp['p'])],'Authored synthetic p-values and recomputed Holm adjustment')+
        p(f'For five tests, Bonferroni compares each raw p-value with {fmt(mp["bonferroni_cutoff"],3)}. Holm orders p-values and uses a step-down rule, controlling familywise error under arbitrary dependence. Its adjusted p-values are made monotone before returning them to original order. The lab calculates this explicitly.')+
        p('False discovery rate procedures address a different target: the expected proportion of false rejections among rejections, under their assumptions. Preregister primary questions, label exploration and validate discovered patterns in new data. A multiplicity correction cannot repair undisclosed selective reporting by itself.'),
        'Does reporting only the smallest p-value erase the other tests from the analysis family?',
        'No. The search that produced the selected result determines the error risk. Suppressing the other tests hides rather than removes multiplicity.')
    add('inference-handoff','Separate the estimate, uncertainty and decision',
        p('A defensible inference brief names the target, observation unit, design, exclusions, estimator and uncertainty method. It distinguishes the statistical result from the operational recommendation and states the assumptions most likely to change the conclusion.')+
        table(['Question','Method and caution'],[['One population mean','t interval when justified; check IID and distribution'],['One probability','Binomial/Wilson methods; define event and dependence'],['Matched comparison','Analyze differences; preserve pair identity'],['Independent means','Welch method; do not invent pairing'],['Practical equivalence','Prespecified margin and TOST, not a failed zero test'],['Many questions','Define the family and control the relevant error target']],'Choose an inferential method from the claim and design')+
        p(f'Example handoff: “For {pa["n"]} independently generated matched products, online minus offline averages {fmt(pa["mean"],3)} CU (95% CI {fmt(pa["low"],3)} to {fmt(pa["high"],3)}). The mean is detectably nonzero and also falls within a prespecified ±{fmt(pa["margin"])} CU equivalence margin under TOST. This concerns an average in an authored synthetic model, not all products or real retailers.”')+
        p('Before acting, ask four questions: Is the target clear? Does the design support it? Is the uncertainty method matched to the estimator and dependence? Would the plausible effect change the decision? Continue to regression with those questions intact.'),
        'What makes a statistically correct computation an incomplete recommendation?',
        'A missing target population, unsupported design assumption, unexamined practical consequence or hidden analysis search can make the computation irrelevant to the decision even when its arithmetic is correct.')
    assert len(sections)==24
    render_lesson(3,'Make uncertainty part of the decision','Distinguish samples from populations, match inference to the design and separate statistical evidence from practical importance.',sections)
    (ROOT/'content'/'lesson3-outline.json').write_text(json.dumps([x['title'] for x in sections],indent=2)+'\n')


def structure_notebook(number,script,data):
    """Break the exact executed source into readable cells; verify sequential rerun.

    Output remains the fresh stdout recorded by write_lab. Source concatenation
    is byte-for-byte identical to the standalone script, so no hidden notebook
    computation or cached hand-entered result can drift from the public lab.
    """
    import re, io, contextlib
    path=ROOT/'dist'/'assets'/f'lesson{number}-lab.ipynb'
    nb=json.loads(path.read_text())
    old_code=next(c for c in nb['cells'] if c['cell_type']=='code')
    output=old_code['outputs']
    chunks=re.split(r'(?=^# [1-9]\. )',script,flags=re.M)
    explain={
        1:[
          'Set the local seed and import the calculation libraries. This lab deliberately preserves known defects until their correction rule is made explicit.',
          'Define the quote observation and candidate key. Generate a fictional panel, add traceable defects, then preserve eligibility and missingness counts separately. Change the missingness rule and predict which counts should change before running it.',
          'Attach one lodging-level attribute to each quote. Compare validated many-to-one cardinality with an intentionally duplicated dimension. Explain which observations receive extra weight in the unsafe join.',
          'Reshape the town-quarter table without inventing a value for the missing cell. Trace one named town-quarter through melt and pivot, and verify uniqueness before spreading columns.',
          'Generate fixture events, expand to team-game units, assign managers with half-open date intervals, and calculate auditable denominators. The final JSON is computed from these generated observations, not pasted results.'
        ],
        2:[
          'Use a fixed local seed. The price model, firm model and probability examples are separate authored mechanisms. None is fitted to historical records.',
          'Generate unequal-size positive quote groups. Recompute bins, areas, quantiles, outlier fences, smooth densities and within-town shares. Change a bin width while holding rows fixed; inspect what changes and what does not.',
          'Use one contingency table for both conditional directions. Contrast empirical event shares with stipulated probability models. Recalculate expected rewards, variances and tail probabilities directly from the assumptions.',
          'Generate a noisy latent-trait firm model, then inspect individual pairs, grouped means and covariance. The symmetric nonlinear example and composition-reversal table expose limits of a single correlation. The final JSON contains freshly computed chart data and results.'
        ],
        3:[
          'Define reusable mean-interval and Wilson-interval functions. The t interval uses sample SD with n−1 and the actual t quantile; the Wilson interval respects probability boundaries.',
          'Create a planned session calendar and an invented cumulative index. Compute changes only between observed sessions, preserving the first undefined change and a fixed loss threshold.',
          'Simulate repeated samples to distinguish observation spread from estimator spread. Compare a running-mean path, a small-sample t calculation and empirical confidence-interval coverage.',
          'Compare same-size bootstrap with smaller subsets, then generate clustered measurements. State the resampling unit and the target of each variability calculation before comparing the numbers.',
          'Choose an exact binomial rejection threshold before observing the synthetic count. Use that same rule for its p-value, false-alarm probability and power at specified alternatives.',
          'Preserve product pairing, calculate the mean difference, paired t test and TOST margin test. Compare a separate independent-groups Welch analysis. Recompute Holm correction for a declared family and print the full fresh result object.'
        ]}
    cells=[nb['cells'][0]];scope={'__name__':'__main__'};captured=''
    for i,chunk in enumerate(chunks):
        heading='Setup' if i==0 else chunk.splitlines()[0].lstrip('# ').strip()
        cells.append({'cell_type':'markdown','metadata':{},'source':[f'## {heading}\n',explain[number][i]+'\n']})
        buffer=io.StringIO()
        with contextlib.redirect_stdout(buffer): exec(compile(chunk,f'lesson{number}-cell-{i+1}','exec'),scope)
        captured+=buffer.getvalue()
        cells.append({'cell_type':'code','metadata':{},'execution_count':i+1,'source':chunk.splitlines(keepends=True),'outputs':output if i==len(chunks)-1 else []})
    assert json.loads(captured)==data
    assert ''.join(''.join(c['source']) for c in cells if c['cell_type']=='code')==script
    cells.append({'cell_type':'markdown','metadata':{},'source':['## Audit and extend\n','Explain the observation unit, target population and main limitation before changing any parameter. Save the original seed and document each changed assumption. The JSON above is the complete fresh stdout used by the lesson; rerunning these cells in order recomputes it without network access or input files.\n']})
    for i,cell in enumerate(cells): cell['id']=f'lesson{number}-{i:02d}-{cell["cell_type"]}'
    nb['cells']=cells;path.write_text(json.dumps(nb,indent=2)+'\n')

def main():
    (ROOT/'dist'/'assets').mkdir(parents=True,exist_ok=True)
    descriptions={
        1:'Generate a fictional quote panel with deliberate quality defects, preserve keys, calculate common-term totals, reshape a request panel, and build a date-aware team-manager summary. Seed 41021. All currencies, entities and events are invented. Comments explain each transformation and audit assertion.',
        2:'Generate independent fictional quote groups and a separate noisy firm model. Recompute histograms, densities, quantiles, KDEs, event probabilities, expectations, distribution-family probabilities, grouped patterns and correlations. Seed 42022. Parameters are teaching assumptions, not fitted historical estimates.',
        3:'Generate a fictional index, IID waiting times, clustered measurements, quality trials and matched product quotes. Recompute sampling simulations, intervals, bootstrap and subset distributions, exact test power, paired and Welch tests, TOST and Holm correction. Seed 43023. No external records or empirical calibration.'}
    for n,script,build in [(1,LAB1,build1),(2,LAB2,build2),(3,LAB3,build3)]:
        data=write_lab(n,script,descriptions[n]);structure_notebook(n,script,data);build(data)
        print(f'Built synthetic lesson {n} from seed {data["seed"]}')

if __name__=='__main__': main()
