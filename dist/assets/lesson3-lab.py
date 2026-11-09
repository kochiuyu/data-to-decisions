"""Original synthetic inference lab. Seed 43023. No network or input files.
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
