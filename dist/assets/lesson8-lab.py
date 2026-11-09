"""Lesson 8. Synthetic DAGs and conditional comparisons; seed 8108.
Independent exogenous Gaussian draws implement the displayed structural equations.
No parameter or observation is fitted to an external source.
"""
import json
import numpy as np
rng=np.random.default_rng(8108)
def ols(y,*xs):
    X=np.column_stack([np.ones(len(y))]+list(xs));b=np.linalg.lstsq(X,y,rcond=None)[0];res=y-X@b
    return {'coef':b.tolist(),'r2':float(1-res@res/((y-y.mean())@(y-y.mean())))}
n=900;s=rng.choice(3,n,p=[.5,.3,.2]);x=rng.normal(size=n);e=np.array([.2,.5,.8])[s];d=rng.binomial(1,e)
y0=10+5*s+2*x+rng.normal(0,2,n);tau=2+s;y=y0+d*tau
rows=[]
for k in range(3):
    a=(s==k)&(d==1);b=(s==k)&(d==0)
    rows.append({'stratum':k,'n':int((s==k).sum()),'treated':int(a.sum()),'control':int(b.sum()),'mean_t':float(y[a].mean()),'mean_c':float(y[b].mean()),'gap':float(y[a].mean()-y[b].mean()),'truth':float(2+k)})
weights={key:np.array([r[field] for r in rows],float) for key,field in [('ATE','n'),('ATT','treated'),('ATU','control')]}
standardized={key:float(w@np.array([r['gap'] for r in rows])/w.sum()) for key,w in weights.items()}
truth={'ATE':float(tau.mean()),'ATT':float(tau[d==1].mean()),'ATU':float(tau[d==0].mean())}
matched=[];distance=[];used=[]
for i in np.where(d==1)[0]:
    candidates=np.where((d==0)&(s==s[i]))[0];j=candidates[np.argmin(abs(x[candidates]-x[i]))]
    matched.append(y[i]-y[j]);distance.append(abs(x[i]-x[j]));used.append(int(j))
m=6000
X=rng.normal(size=m);D=.9*X+rng.normal(size=m);Y=-D+3*X+rng.normal(size=m)
conf={'naive':ols(Y,D),'adjusted':ols(Y,D,X),'population_naive':-1+3*.9/(.9**2+1),'truth':-1,'cov_ratio':float(np.cov(D,X,ddof=0)[0,1]/np.var(D))}
D=rng.normal(size=m);U=rng.normal(size=m);Y=.6*D+1.5*U+rng.normal(size=m);C=D+U+.3*rng.normal(size=m);R=C+.5*rng.normal(size=m)
coll={'naive':ols(Y,D),'adjusted':ols(Y,D,C),'descendant':ols(Y,D,R),'truth':.6,'population_adjusted':.6-1.5/(1+.3**2)}
D=rng.normal(size=m);M=.8*D+rng.normal(size=m);Y=.5*D+1.5*M+rng.normal(size=m)
med={'total':ols(Y,D),'direct':ols(Y,D,M),'truth_total':.5+.8*1.5,'truth_direct':.5}
print(json.dumps({'seed':8108,'n':n,'strata':rows,'standardized':standardized,'truth':truth,'raw_gap':float(y[d==1].mean()-y[d==0].mean()),'weights':{key:(w/w.sum()).tolist() for key,w in weights.items()},'matching':{'att':float(np.mean(matched)),'mean_distance':float(np.mean(distance)),'max_distance':float(np.max(distance)),'treated_n':len(matched),'unique_controls':len(set(used))},'confounding':conf,'collider':coll,'mediation':med},indent=2,allow_nan=False))
