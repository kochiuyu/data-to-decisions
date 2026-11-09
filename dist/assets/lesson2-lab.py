"""Original synthetic distribution and association lab. Seed 42022.
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
