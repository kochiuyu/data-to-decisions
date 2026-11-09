"""Lesson 9. Synthetic process-coaching program at fictional facilities.
Seed 9109; no input files, network, external observations or empirical calibration.
X and B precede assignment. Selection is ignorable given them by construction.
"""
import json
import numpy as np
from scipy.special import expit
from sklearn.linear_model import LogisticRegression
rng=np.random.default_rng(9109);n=2400
x=rng.normal(size=n);b=rng.binomial(1,.45,n)
true_e=expit(-.3+1.2*x+.8*b)
d=rng.binomial(1,true_e)
y0=45+4*x+2*x*x+3*b+rng.normal(0,5,n)
tau=3+1.5*x+2*b;y=y0+d*tau

def fit_predict(interactions=True):
    def design(z):
        cols=[np.ones(n),z,x,x*x,b]
        if interactions:cols.extend([z*x,z*b])
        return np.column_stack(cols)
    X=design(d);beta=np.linalg.lstsq(X,y,rcond=None)[0]
    L=design(np.ones(n))-design(np.zeros(n));contrast=L@beta
    bread=np.linalg.inv(X.T@X);h=np.einsum('ij,jk,ik->i',X,bread,X);res=y-X@beta;cov=bread@(X.T@((res/(1-h))[:,None]**2*X))@bread
    avgL=L.mean(axis=0);se=float(np.sqrt(avgL@cov@avgL))
    return {'ate_se':se,'ate_low':float(contrast.mean()-1.96*se),'ate_high':float(contrast.mean()+1.96*se),'beta':beta.tolist(),'ate':float(contrast.mean()),'att':float(contrast[d==1].mean()),'atu':float(contrast[d==0].mean()),'subgroup_b0':float(contrast[b==0].mean()),'subgroup_b1':float(contrast[b==1].mean())}
full=fit_predict();additive=fit_predict(False)
# Estimated score has an intercept, X, and B, matching the assignment form.
ps=LogisticRegression(C=1e6,max_iter=2000).fit(np.column_stack([x,b]),d).predict_proba(np.column_stack([x,b]))[:,1]
w=np.where(d,1/ps,1/(1-ps))
def wmean(v,z,weights): return float(np.average(v[d==z],weights=weights[d==z]))
def ess(a):return float(a.sum()**2/(a@a))
def smd(v,weights):
    # Fixed, unweighted pooled within-arm SD makes before/after comparable.
    scale=np.sqrt((v[d==1].var(ddof=1)+v[d==0].var(ddof=1))/2)
    return (wmean(v,1,weights)-wmean(v,0,weights))/scale
balance=[{'variable':name,'before':float(smd(v,np.ones(n))),'ipw':float(smd(v,w))} for name,v in [('workload X',x),('baseline B',b),('workload squared',x*x)]]
ipw=wmean(y,1,w)-wmean(y,0,w)
# ATT coarsened exact matching. Each retained treated unit gets weight 1;
# each control in its cell gets n_t(cell)/n_c(cell).
cells=np.digitize(x,[-1.5,-.75,0,.75,1.5])*2+b
cw=np.zeros(n);cell_rows=[]
for c in np.unique(cells):
    mask=cells==c;nt=int((mask&(d==1)).sum());nc=int((mask&(d==0)).sum());keep=nt>0 and nc>0
    if keep:cw[mask&(d==1)]=1;cw[mask&(d==0)]=nt/nc
    cell_rows.append({'cell':int(c),'treated':nt,'control':nc,'retained':bool(keep)})
keep=cw>0;cem=wmean(y,1,cw)-wmean(y,0,cw)
for r,v in zip(balance,[x,b,x*x]):r['cem']=float(smd(v,cw))
bins=np.linspace(0,1,11);hist=[]
for a,z in [('Control',0),('Treated',1)]:hist.append(np.histogram(ps[d==z],bins=bins)[0].tolist())
# A harder assignment scenario illustrates failed overlap, not merely poor fitting.
hard=(x>.5).astype(int);no_support=int((hard==1).sum())
# A sample-rule audit uses artificial eligibility labels, never private firm data.
age=rng.integers(1,16,n);region=rng.choice(['North','South','East'],n)
eligible=(age>=3)&np.isin(region,['North','South'])
wrong=(age>=3)|np.isin(region,['North','South'])
# Omitted variable sensitivity is a separate DGP with a newly drawn latent cause.
u=rng.normal(size=n);dh=rng.binomial(1,expit(-.3+.8*x+.8*b+u));yh=45+4*x+3*b+2*u+3*dh+rng.normal(0,5,n)
Xh=np.column_stack([np.ones(n),dh,x,b]);hidden_coef=float(np.linalg.lstsq(Xh,yh,rcond=None)[0][1])
# Conditional effect function transported to an explicitly different synthetic target.
xt=rng.normal(.7,1,2000);bt=rng.binomial(1,.7,2000);target_truth=float((3+1.5*xt+2*bt).mean())
beta=np.array(full['beta']);transport=float((beta[1]+beta[5]*xt+beta[6]*bt).mean())
out={'seed':9109,'n':n,'treated':int(d.sum()),'control':int((1-d).sum()),'means':{'treated':float(y[d==1].mean()),'control':float(y[d==0].mean())},'raw_gap':float(y[d==1].mean()-y[d==0].mean()),'truth':{'ate':float(tau.mean()),'att':float(tau[d==1].mean()),'atu':float(tau[d==0].mean())},'regression':full,'additive':additive,'ipw':float(ipw),'cem':float(cem),'cem_truth_att':float(tau[(d==1)&keep].mean()),'cem_kept_treated':int(((d==1)&keep).sum()),'cem_kept_control':int(((d==0)&keep).sum()),'cells':cell_rows,'balance':balance,'scores':{'min':float(ps.min()),'max':float(ps.max()),'tail_n':int(((ps<.05)|(ps>.95)).sum()),'hist_centers':((bins[:-1]+bins[1:])/2).tolist(),'control_hist':hist[0],'treated_hist':hist[1]},'weights':{'max':float(w.max()),'ess_t':ess(w[d==1]),'ess_c':ess(w[d==0])},'hard_assignment_treated_without_controls':no_support,'audit':{'correct_n':int(eligible.sum()),'wrong_n':int(wrong.sum()),'extra_n':int((wrong&~eligible).sum())},'hidden_cause':{'true_effect':3,'adjusted_omitting_u':hidden_coef},'transport':{'true_target':target_truth,'estimated_target':transport}}
assert out['audit']['wrong_n']-out['audit']['correct_n']==out['audit']['extra_n']
print(json.dumps(out,indent=2,allow_nan=False))
