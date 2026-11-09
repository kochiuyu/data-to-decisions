"""Lesson 4: original fictional Juniper workshop, seed 440731.
DGP: independent X~Uniform(1,16), Z~N(0,1),
Y=20+5X+0.18X^2+5sin(X/3)+(3+0.35X)Z, n=180.
Y is completion minutes, X is batch size in standardized crate units.
Other examples use independent random draws from the same seeded stream.
No downloads, source records, historical outputs or external files are used.
"""
import json
import numpy as np
from sklearn.model_selection import KFold, train_test_split
rng=np.random.default_rng(440731)
def ols(X,y):
    b=np.linalg.lstsq(X,y,rcond=None)[0];e=y-X@b
    return b,e,float(e@e)
def design(x,kind):
    if kind=='hinge': return np.column_stack([np.ones(len(x)),x,np.maximum(x-8,0)])
    degree={'line':1,'quadratic':2,'cubic':3}[kind]
    return np.vander(x,degree+1,increasing=True)
def lowess(x,y,grid,frac=.35):
    out=[];k=int(np.ceil(len(x)*frac))
    for a in grid:
        d=np.abs(x-a);h=np.sort(d)[k-1];w=np.maximum(1-(d/h)**3,0)**3
        X=np.column_stack([np.ones(len(x)),x-a]);b=np.linalg.lstsq(X*np.sqrt(w[:,None]),y*np.sqrt(w),rcond=None)[0];out.append(float(b[0]))
    return out
n=180;x=rng.uniform(1,16,n);mu=20+5*x+.18*x*x+5*np.sin(x/3);y=mu+(3+.35*x)*rng.normal(size=n)
X=design(x,'line');b,e,sse=ols(X,y);tss=float(((y-y.mean())**2).sum());ess=float(((X@b-y.mean())**2).sum());grid=np.linspace(1,16,13)
bins=[]
for a,z in zip(np.linspace(1,16,7)[:-1],np.linspace(1,16,7)[1:]):
    m=(x>=a)&(x<z);bins.append([float(a),float(z),int(m.sum()),float(x[m].mean()),float(y[m].mean()),float(e[m].mean())])
# Five new simulated rows for a hand-verifiable calculation.
tx=np.arange(1.,6.);ty=7+2.5*tx+rng.integers(-3,4,5);tb,te,tsse=ols(design(tx,'line'),ty)
hand=dict(x=tx.tolist(),y=ty.tolist(),xbar=float(tx.mean()),ybar=float(ty.mean()),sxx=float(((tx-tx.mean())**2).sum()),sxy=float(((tx-tx.mean())*(ty-ty.mean())).sum()),b=tb.tolist(),fitted=(design(tx,'line')@tb).tolist(),resid=te.tolist(),sse=tsse)
# Independent transformed-outcome examples, not transformations of the first outcome.
u=rng.uniform(1,12,200)
y_ll=np.exp(2.8+.11*u+rng.normal(0,.2,len(u)))
y_lg=40+15*np.log(u)+rng.normal(0,4,len(u))
y_gg=np.exp(2+.7*np.log(u)+rng.normal(0,.18,len(u)))
bll,ell,_=ols(design(u,'line'),np.log(y_ll));blg,_,_=ols(design(np.log(u),'line'),y_lg);bgg,egg,_=ols(design(np.log(u),'line'),np.log(y_gg))
ug=np.linspace(1,12,12);smear=float(np.exp(ell).mean())
trans=dict(log_level=bll.tolist(),level_log=blg.tolist(),log_log=bgg.tolist(),pct_one=float(100*np.expm1(bll[1])),level_ten=float(blg[1]*np.log(1.1)),pct_ten=float(100*np.expm1(bgg[1]*np.log(1.1))),smear=smear,grid=ug.tolist(),log_level_median=np.exp(bll[0]+bll[1]*ug).tolist(),log_level_mean=(smear*np.exp(bll[0]+bll[1]*ug)).tolist(),level_log_fit=(blg[0]+blg[1]*np.log(ug)).tolist(),log_log_fit=np.exp(bgg[0]+bgg[1]*np.log(ug)).tolist())
# A deliberately constructed sensitivity row is marked, never disguised as observed data.
xa=np.r_[x,35.];ya=np.r_[y,280.];Xa=design(xa,'line');ba,ea,ssa=ols(Xa,ya);hat=np.sum((Xa@np.linalg.inv(Xa.T@Xa))*Xa,axis=1);s2=ssa/(len(xa)-2);cook=ea**2/(2*s2)*hat/(1-hat)**2
j=int(np.argmax(cook));influence=dict(index=j,point=[float(xa[j]),float(ya[j])],h=float(hat[j]),resid=float(ea[j]),cook=float(cook[j]),slope_original=float(b[1]),slope_augmented=float(ba[1]),mean_h=float(hat.mean()),threshold=float(4/len(xa)))
# Measurement/selection are descriptive sensitivity examples, not causal estimators.
measured=x+rng.normal(0,3,n);bnoise,_,_=ols(design(measured,'line'),y)
keep=y>np.median(y);bsel,_,_=ols(design(x[keep],'line'),y[keep])
# Predeclared validation: hold out 25%, use 5-fold CV only in development.
dev,test=train_test_split(np.arange(n),test_size=.25,random_state=440732)
folds=list(KFold(5,shuffle=True,random_state=440733).split(dev));rows=[];cv={}
for kind in ['line','quadratic','cubic','hinge']:
    D=design(x,kind);bb,ee,ss=ols(D[dev],y[dev]);oof=np.empty(len(dev))
    for tr,va in folds:
        bf,_,_=ols(D[dev[tr]],y[dev[tr]]);oof[va]=D[dev[va]]@bf
    mse=float(np.mean((y[dev]-oof)**2));cv[kind]=mse
    rows.append(dict(model=kind,p=D.shape[1],train_rmse=float(np.sqrt(ss/len(dev))),cv_rmse=float(np.sqrt(mse))))
chosen=min(cv,key=cv.get);bc,_,_=ols(design(x[dev],chosen),y[dev]);testpred=design(x[test],chosen)@bc;test_rmse=float(np.sqrt(np.mean((y[test]-testpred)**2)))
quad,_,_=ols(design(x,'quadratic'),y);hinge,_,_=ols(design(x,'hinge'),y)
curve={kind:(design(grid,kind)@ols(design(x,kind),y)[0]).tolist() for kind in ['line','quadratic','cubic','hinge']}
# Exact OLS geometry is tested computationally.
assert np.isclose(tss,ess+sse)
assert abs(e.sum())<1e-8 and abs(x@e)<1e-7
assert len(set(dev)&set(test))==0
print(json.dumps(dict(seed=440731,n=n,x_min=float(x.min()),x_max=float(x.max()),mean_y=float(y.mean()),b=b.tolist(),sse=sse,tss=tss,ess=ess,r2=1-sse/tss,rmse=float(np.sqrt(sse/n)),residual_sd=float(np.sqrt(sse/(n-2))),variance=float(tss/(n-1)),resid_sum=float(e.sum()),x_resid=float(x@e),grid=grid.tolist(),truth=(20+5*grid+.18*grid*grid+5*np.sin(grid/3)).tolist(),ols_curve=(design(grid,'line')@b).tolist(),lowess=lowess(x,y,grid),bins=bins,scatter=np.column_stack([x[:36],y[:36]]).tolist(),residual_scatter=np.column_stack([x[:36],e[:36]]).tolist(),hand=hand,trans=trans,influence=influence,sensitivity=dict(clean=float(b[1]),noisy=float(bnoise[1]),selected=float(bsel[1]),selected_n=int(keep.sum())),validation=rows,selected=chosen,development_n=len(dev),test_n=len(test),test_rmse=test_rmse,quadratic=quad.tolist(),quadratic_slopes=[float(quad[1]+2*quad[2]*v) for v in [4,8,12]],hinge=hinge.tolist(),hinge_slopes=[float(hinge[1]),float(hinge[1]+hinge[2])],curves=curve)))
