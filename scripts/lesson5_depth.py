"""Regression inference and adjusted comparisons, from one executable analysis."""
from functools import lru_cache
import numpy as np
from lesson2_depth import figure, text

CALCULATIONS = '''# Fit the same baseline stores; HC1 is the course robust covariance.
from scipy.stats import norm, t, f as f_dist, chi2
stores = world()['stores']
x = stores.lead_days.to_numpy(); y = stores.baseline_rate.to_numpy()
u = stores.urban.to_numpy(); demand = stores.baseline_demand.to_numpy()-100
promo = stores.promotion_share.to_numpy(); n = len(y)
X = np.column_stack([np.ones(n),x,u,demand,promo,x*u])
b, V, residual = fit_ols(X,y); fitted = X@b
p = X.shape[1]; B = np.linalg.inv(X.T@X)
sigma2_full = residual@residual/(n-p)
classical_se = np.sqrt(np.diag(sigma2_full*B))
robust_se = np.sqrt(np.diag(V)); z_score = b/robust_se
p_value = 2*norm.sf(np.abs(z_score))
ci95 = np.column_stack([b-1.96*robust_se,b+1.96*robust_se])
ci99 = np.column_stack([b-norm.ppf(.995)*robust_se,b+norm.ppf(.995)*robust_se])
# Simple-model pointwise bands use a classical future-variance model.
S = np.column_stack([np.ones(n),x]); bs, Vs, es = fit_ols(S,y)
s2 = es@es/(n-2); bread = np.linalg.inv(S.T@S)
grid = np.linspace(2,5,101); G = np.column_stack([np.ones(len(grid)),grid])
mean = G@bs; mean_se = np.sqrt(s2*np.einsum('ij,jk,ik->i',G,bread,G))
prediction_se = np.sqrt(s2+mean_se**2); critical = t.ppf(.975,n-2)
mean_band = np.column_stack([mean-critical*mean_se,mean+critical*mean_se])
prediction_band = np.column_stack([mean-critical*prediction_se,mean+critical*prediction_se])
row4 = np.array([1,4]); mean4 = row4@bs
mean_se4 = np.sqrt(s2*(row4@bread@row4)); prediction_se4 = np.sqrt(s2+mean_se4**2)
# Recover the omitted-variable identity without changing the sample.
L = np.column_stack([np.ones(n),x,u]); bl, Vl, el = fit_ols(L,y)
sorting, _, _ = fit_ols(S,u); ovb_product = bl[2]*sorting[1]
assert np.isclose(bs[1],bl[1]+ovb_product)
# Centering delivery changes the reference, not fitted values.
C = np.column_stack([np.ones(n),x-3,u,demand,promo,(x-3)*u])
bc, Vc, ec = fit_ols(C,y)
assert np.allclose(C@bc,fitted)
contrasts = []
for lead in [2,3,4,5]:
    c = np.array([0,0,1,0,0,lead]); value = c@b; se = np.sqrt(c@V@c)
    contrasts.append([lead,value,se,value-1.96*se,value+1.96*se])
urban_slope_row = np.array([0,1,0,0,0,1])
urban_slope_se = np.sqrt(urban_slope_row@V@urban_slope_row)
# A two-restriction test asks whether the group lines coincide.
R = np.eye(p)[[2,5]]; restrictions = R@b; RV = R@V@R.T
wald = restrictions@np.linalg.solve(RV,restrictions); wald_p = chi2.sf(wald,2)
A = np.column_stack([np.ones(n),x,demand,promo]); ba, Va, ea = fit_ols(A,y)
F = ((ea@ea-residual@residual)/2)/(residual@residual/(n-p))
F_p = f_dist.sf(F,2,n-p)
# Add centered curvature on the same rows and inspect nested training fit.
Q = np.column_stack([X,(demand/10)**2]); bq,Vq,eq = fit_ols(Q,y)
P = X[:,:5]; bp,Vp,ep = fit_ols(P,y)
sst = np.sum((y-y.mean())**2); fit_rows = []
for label,design,error in [('Lead only',S,es),('Add urban',L,el),('Add demand / promo',P,ep),('Group slopes',X,residual),('Add demand squared',Q,eq)]:
    count = design.shape[1]; sse = error@error
    fit_rows.append([label,count,1-sse/sst,1-(sse/(n-count))/(sst/(n-1)),np.sqrt(sse/n)])
def vif_values(design):
    values = []
    for j in range(1,design.shape[1]):
        other = np.delete(design,j,axis=1); target = design[:,j]
        error = target-other@np.linalg.lstsq(other,target,rcond=None)[0]
        values.append(np.sum((target-target.mean())**2)/(error@error))
    return np.array(values)
raw_vif = vif_values(X); centered_vif = vif_values(C)
# Predictions keep the full profile visible.
profiles = []
for group in [0,1]:
    for lead in [2,3,4,5]:
        row = np.array([1,lead,group,0,.25,lead*group])
        profiles.append([group,lead,row@b])
assert np.all(prediction_band[:,1]-prediction_band[:,0] > mean_band[:,1]-mean_band[:,0])
assert np.allclose(b[[1,5]],[1.53089239224744,.22833509751825537])
assert np.isclose(bc[2],contrasts[1][1])
assert np.allclose(X.T@residual,0,atol=1e-8)
'''

DETAIL_TITLES = [
 'A covariance matrix connects every coefficient to its uncertainty',
 'Classical slope precision depends on residual spread and predictor spread',
 'HC1 and HC3 change uncertainty while preserving the OLS fit',
 'A future individual adds residual variance to mean-estimation variance',
 'Profile uncertainty includes covariance between coefficients',
 'A joint restriction uses the covariance of the whole restricted vector',
 'The classical F test compares nested residual sums of squares',
 'Centering preserves fitted values while changing the reference comparison',
 'Shared control slopes distinguish this model from unrestricted group fits',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    ns=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson5-shared-calculations','exec'),ns)
    return ns

def graph(title,x,y,xlabel,ylabel,lines=(),bands=(),diagonal=False,labels=(),show_points=True,desc=''):
    allx=np.asarray(x); vals=list(y)
    for xx,yy,col,dash in lines:vals.extend(yy)
    for xx,lo,hi,col in bands:vals.extend(lo);vals.extend(hi)
    xmin,xmax=float(min(allx)),float(max(allx));ymin,ymax=float(min(vals)),float(max(vals))
    if diagonal:xmin=ymin=min(xmin,ymin);xmax=ymax=max(xmax,ymax)
    dx=xmax-xmin or 1;dy=ymax-ymin or 1;xmin-=dx*.05;xmax+=dx*.05;ymin-=dy*.08;ymax+=dy*.08
    sx=lambda v:65+590*(v-xmin)/(xmax-xmin);sy=lambda v:255-200*(v-ymin)/(ymax-ymin)
    pts=lambda xx,yy:' '.join(f'{sx(a):.2f},{sy(b):.2f}' for a,b in zip(xx,yy))
    body=text(65,23,ylabel,14)
    for tick in np.linspace(ymin,ymax,5):
        yy=sy(tick);body+=f'<line x1="65" x2="655" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#dce4da"/>'+text(57,yy+4,f'{tick:.1f}',12,'end')
    for tick in np.linspace(min(allx),max(allx),5):body+=text(sx(tick),279,f'{tick:.1f}',12,'middle')
    for xx,lo,hi,col in bands:
        body+=f'<polygon points="{pts(xx,lo)} {pts(list(xx)[::-1],list(hi)[::-1])}" fill="{col}" opacity=".45"/>'
    for xx,yy in (zip(x,y) if show_points else []):body+=f'<circle cx="{sx(xx):.2f}" cy="{sy(yy):.2f}" r="2.7" fill="#526f68" opacity=".5"/>'
    if diagonal:lines=list(lines)+[(np.array([xmin,xmax]),np.array([xmin,xmax]),'#9b421e',True)]
    for xx,yy,col,dash in lines:body+=f'<polyline points="{pts(xx,yy)}" fill="none" stroke="{col}" stroke-width="3"'+(' stroke-dasharray="6 4"' if dash else '')+'/>'
    for xx,yy,label in labels:body+=f'<circle cx="{sx(xx):.2f}" cy="{sy(yy):.2f}" r="5" fill="#9b421e"/>'+text(sx(xx)+7,sy(yy)-8,label,13)
    body+=text(360,317,xlabel,15,'middle')
    return figure(title,body,desc)

def lines_picture():
    body=''
    for j,interaction in enumerate([False,True]):
        left=50+j*350
        body+=text(left,25,'Parallel slopes' if not interaction else 'Different slopes',17)
        body+=f'<path d="M{left},255 H{left+270} M{left},255 V55" fill="none" stroke="#72847a"/>'
        for k,col in enumerate(['#276451','#3259a2']):
            ya=230-45*k;yb=160-45*k-(55 if interaction and k else 0)
            body+=f'<line x1="{left+15}" y1="{ya}" x2="{left+250}" y2="{yb}" stroke="{col}" stroke-width="4"/>'
        body+=text(left+130,285,'Predictor X',14,'middle')
    body+=text(360,320,'Schematic: green D=0; blue D=1',14,'middle')
    return figure('An interaction changes how the group difference varies with X',body,'Schematic equations: parallel lines use a+bX+cD; unrestricted group lines add dXD. Both include the group main effect.')

def restore(c):
    from retail_ui import section,table,formula,p,step_link
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();b=d['b'];V=d['V'];se=d['robust_se'];s=d['stores']
    c['sections']=[]
    c['headlines']={k:v for k,v in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    c['authored_sections']=True
    c['presentation_points']={
      'memo':['Report a complete profile and its interval','Group differences and slope differences are distinct questions','Use residuals to guide operating review'],
      'question':['Joint test rejects; slope-only test does not. Why?'],
      'answer':['Coincident lines require zero level and slope differences','A level difference can drive joint rejection','The slope estimate may remain imprecise'],
      'truth':['The mechanism includes an interaction','A known nonzero effect need not be significant in every sample']}
    c['headlines']['memo']=['Report the comparison and its uncertainty together','A joint rejection can reflect level differences rather than slope differences']
    def block(title,visual,*notes):return teach(title,visual,list(notes))
    def put(key,title,body,phase='Worked application'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    put('theory-inference','Quantify uncertainty in a regression relationship',
      block('A coefficient and its standard error answer different questions',bullets('Coefficient: size and direction of the fitted comparison','Standard error: sampling variation of that estimate','Interval: a range of values compatible with the procedure','Test: compare the estimate with a stated benchmark'),
        'The coefficient estimates a population regression relationship. Its standard error describes how the estimator varies across samples under the analysis model. A precise estimate need not be large enough to matter operationally. Begin by naming the coefficient, its units, and the comparison being estimated.')+
      block('A test measures the distance from a benchmark in standard-error units',formula('Statistic = (b − β₀) / SE(b); interval = b ± critical value × SE(b)'),
        'For a two-sided test, the null specifies β=β₀ and the alternative allows values on either side. Under the null, compare the statistic with its reference distribution; the p-value is its two-tail probability at least this far from zero. It is not the probability that the null is true. A matching two-sided 5% test rejects exactly when the corresponding 95% interval excludes β₀. A 99% interval is wider and corresponds to a 1% test. Classical normal-error OLS uses Student t with n−p degrees of freedom; the robust examples here use a large-sample normal reference.')+
      block('More information narrows uncertainty when the model is held fixed',bullets('More independent observations improve precision','More predictor spread helps distinguish a slope','Less unexplained outcome spread reduces standard errors','Overlapping predictors make separate slopes harder to distinguish'),
        'In simple classical OLS, SE(b)=s/√Σ(X−X̄)². Here s²=SSE/(n−2), so residual variation raises uncertainty and predictor variation lowers it. The formula does not promise that collecting arbitrary extra rows or changing the population improves the same estimand. The appendix derives the slope and intercept calculations.')+
      block('Robust standard errors change uncertainty without changing the fitted line',table(['Choice','Variance model','Same OLS coefficients?'],[['Classical','Constant residual variance','Yes'],['HC1 robust','Variance may differ across independent stores','Yes']], 'Choose the covariance estimate, then use it consistently'),
        'Heteroskedasticity means unequal error variance across input profiles. HC1 estimates coefficient covariance using squared residuals with a degrees-of-freedom correction. HC3 uses a different leverage correction; the original deck used HC3. This course retains HC1 to keep all displayed coefficients, intervals, and contrasts on one convention. Robust covariance does not repair a misspecified mean equation or define the variance of a future individual outcome.'),phase='General theory')
    put('theory-prediction','Distinguish a mean response from one new outcome',
      block('A mean interval and an individual interval target different quantities',table(['Target','Uncertainty included'],[['E[Y | X=x]','Estimation of the mean relationship'],['A new Y at X=x','Mean estimation plus individual variation']], 'Use the same profile and outcome period for both'),
        'An individual prediction interval adds the new observation’s variation around its conditional mean. In this lesson one outcome is a store’s eight-week baseline-average rate, not one product-day or next week’s rate. With the same variance model and confidence level, an individual interval is wider than a mean interval.')+
      block('Classical mean uncertainty widens away from the predictor mean',formula('SE(mean at x) = s √[1/n + (x−X̄)²/Sxx]'),
        'Sxx=Σ(X−X̄)². Under constant residual variance, the mean standard error is smallest at X̄, where the second term vanishes. For a new individual, add 1 inside the square root. More data can make mean uncertainty small, while individual variation remains. These are pointwise intervals at each x, not a simultaneous confidence statement about the entire curve.')+
      block('A model’s scope follows the stores, period, and measurement it represents',bullets('Name the population and outcome period','Check that new profiles have comparable inputs','Look for changes in operating conditions','Evaluate later outcomes before expanding use'),
        'External validity concerns transferring a result to another setting. A baseline relationship for these stores does not automatically describe a new store format or a different supply network. Ask what similarities and new evidence support the transfer. This is an operating choice about where the model can help, rather than another coefficient test.'),phase='General theory')
    put('theory-foundations','Define adjusted comparisons and joint questions',
      block('Multiple regression holds the other included predictors fixed',formula('Y = β₀ + β₁X₁ + … + βₖXₖ + u'),
        'Ordinary least squares chooses coefficients to minimize the sum of squared residuals. A coefficient describes changing its predictor while holding the other specified predictors fixed. With interactions or powers, read the associated terms together. The design row records every input used in a prediction; the appendix shows its matrix representation.')+
      block('Overlapping predictors make separate coefficient estimates less precise',table(['R² from predicting one input with the others','Variance inflation','SE multiplier'],[['0.00','1','1'],['0.75','4','2'],['0.96','25','5']], 'Classical relationship: VIF=1/(1−R²); SE multiplier=√VIF'),
        'Multicollinearity means inputs carry overlapping information. Holding residual variance and that input’s total variation fixed, VIF describes how much coefficient variance increases compared with orthogonal predictors. Exact redundancy prevents unique coefficients; near redundancy inflates uncertainty. It does not by itself bias OLS or prove poor prediction. Inspect whether the intended separate comparisons are supported by the observed combinations.')+
      block('A joint test asks whether several restrictions hold together',bullets('One test: are the two delivery slopes equal?','Joint test: are both group intercept and slope differences zero?','Coincident lines require both restrictions','Evaluate the coefficient vector with its covariance'),
        'In a model a+bX+cD+dXD, equal slopes means d=0. Coincident group lines means c=d=0. Two separate non-rejections are not a substitute for a joint test. A classical F test compares nested residual sums of squares under constant variance; a robust Wald test uses the HC1 covariance. The application reports the robust joint result and the appendix shows both calculations.')+
      block('Omitted-variable changes combine an outcome association with sorting',formula('b short = b long + γ × δ'),
        'Fit Y on X, then Y on X and Z on the same observations. γ is Z’s coefficient in the longer regression; δ comes from regressing Z on X. Their product exactly explains the sample slope change. This is an algebraic comparison of regressions. Interpreting a coefficient as the effect of an intervention requires the design developed later in the course.'),phase='General theory')
    put('theory-specification','Encode the comparisons the model should allow',
      block('K categories use K−1 indicators when an intercept is present',table(['Delivery category','D3','D4','D5'],[['2 days: reference',0,0,0],['3 days',1,0,0],['4 days',0,1,0],['5 days',0,0,1]], 'Alternative categorical coding of the same delivery variable'),
        'Each indicator coefficient compares its category with the two-day reference, holding other terms fixed. The reference observations remain in the fit. Including all four indicators plus an intercept duplicates one column. This is an alternative to a single numeric delivery slope; do not add redundant columns merely to enlarge a model.')+
      block('Interactions let a group difference change with the predictor',lines_picture(),
        'For Y=a+bX+cD+dXD, group D=0 has line a+bX and group D=1 has line (a+c)+(b+d)X. The difference at X is c+dX. Dropping c forces the lines to share an intercept at X=0, which is a substantive restriction. For two continuous inputs, Y=a+bX+cZ+dXZ gives an X slope of b+dZ. Centering X at a meaningful value moves the reference comparison without changing fitted values.')+
      block('Curvature and interactions answer different questions about changing slopes',table(['Term added','Slope in X','Question'],[['qX²','b+2qX','Does the slope change with X?'],['dXZ','b+dZ','Does the slope change with Z?']], 'Interpret the complete expression at specified values'),
        'Lesson 4 introduced curved relationships. Multiple regression combines them with measured controls. With centered demand d=D−100 and term q(d/10)², the demand slope is b_d+2qd/100 in rate points per demand-index unit. For a continuous interaction with coefficients b=.5 and d=.2, the X slope is .5 at Z=0 and .9 at Z=2; these are illustrative coefficients, not retail estimates.'),phase='General theory')
    put('read-data','Keep the same outcome and analysis rows',block('The comparison uses the same 150 baseline store profiles',table(['Input','Meaning'],[['Outcome','Stockout rate over weeks 1–8 (%)'],['Lead / urban','Usual delivery days / 0–1 location'],['Demand−100','Observed baseline demand above reference'],['Promotion share','Fraction of baseline weeks promoted'],['Lead×urban','Allows the delivery slope to differ']], 'All models below use the same store-level rows'),
      'We retain the Lesson 4 outcome and sample. A promotion share of .25 means promotions in a quarter of baseline weeks. These are explanatory baseline inputs; Lesson 6 will specify what is available before a forecast is issued. Keeping the sample fixed makes changes between nested models interpretable.'))
    put('regression-uncertainty','Read uncertainty before comparing the richer model',
      block('The lead coefficient is precise; the slope difference is less precise',table(['Term','Estimate','HC1 SE','95% interval'],[[name,f'{b[i]:.3f}',f'{se[i]:.3f}',f'{d["ci95"][i,0]:.3f} to {d["ci95"][i,1]:.3f}'] for i,name in enumerate(['Intercept','Lead','Urban','Demand−100','Promotion share','Lead×urban'])], 'Six-column model; normal-reference 95% intervals'),
        'The lead coefficient is the slope for nonurban stores. The interaction estimates how much the urban slope differs. The urban main effect refers to lead=0 here; we will move that reference into the observed range. HC1 leaves the fitted coefficients unchanged.')+
      block('The interaction estimate does not establish a slope difference at 5%',formula(f'z = {b[5]:.3f}/{se[5]:.3f} = {d["z_score"][5]:.3f}; two-sided p = {d["p_value"][5]:.3f}'),
        'The null is that the two delivery slopes are equal after demand and promotion share are held fixed. Its 95% interval includes zero, so this test does not reject at 5%. The fitted slopes still differ numerically; neither a positive estimate nor a non-rejection settles whether the population slopes differ. Operational importance also depends on the size of a plausible difference.')+
      block('A higher confidence level produces a wider interval from the same estimate',table(['Term','95% interval','99% interval'],[[name,f'{d["ci95"][i,0]:.3f} to {d["ci95"][i,1]:.3f}',f'{d["ci99"][i,0]:.3f} to {d["ci99"][i,1]:.3f}'] for i,name in [(1,'Nonurban lead slope'),(5,'Slope difference')]], 'Same coefficient and HC1 SE; critical values 1.960 and 2.576'),
        'The estimate does not change when the confidence level changes. A larger critical value gives wider coverage and a stricter matching two-sided test. The nonurban slope excludes zero at both levels; the slope difference includes zero at both.'))
    put('interval-bands','Return to the simple line to see prediction uncertainty',
      block('A new store’s rate has a wider interval than the average relationship',graph('Mean and individual uncertainty around the Lesson 4 line',d['x'],d['y'],'Delivery time (days)','Stockout rate (%)',lines=[(d['grid'],d['mean'],'#276451',False)],bands=[(d['grid'],d['prediction_band'][:,0],d['prediction_band'][:,1],'#e6c487'),(d['grid'],d['mean_band'][:,0],d['mean_band'][:,1],'#6fa99b')],desc='Green: 95% pointwise mean interval. Gold: 95% pointwise individual prediction interval. Classical simple regression; each dot is one baseline store average.'),
        'We deliberately use the two-column simple model here to expose the textbook calculation. It is the same line as Lesson 4, not the six-column model in the preceding table. Constant residual variance and a normal-error reference supply the classical individual interval. The uncertainty target is a new comparable eight-week store average.')+
      block('The individual standard error adds residual variance before taking a square root',table(['Four-day delivery profile','Calculation'],[['Fitted mean',f'{d["mean4"]:.3f}%'],['Mean SE',f'{d["mean_se4"]:.3f} points'],['Residual variance',f'{d["s2"]:.3f} points²'],['Individual SE',f'√({d["s2"]:.3f}+{d["mean_se4"]:.3f}²) = {d["prediction_se4"]:.3f}'],['95% mean interval',f'{d["mean4"]-d["critical"]*d["mean_se4"]:.3f} to {d["mean4"]+d["critical"]*d["mean_se4"]:.3f}%'],['95% individual interval',f'{d["mean4"]-d["critical"]*d["prediction_se4"]:.3f} to {d["mean4"]+d["critical"]*d["prediction_se4"]:.3f}%']], 'Student t critical value with 148 degrees of freedom'),
        'Multiply each standard error by the same t critical value, then add and subtract from the same fitted mean. Residual variance is in squared rate points, so it is added to squared mean SE before taking the square root. This calculation connects the two bands to quantities that students can reconstruct.'))
    put('controls','Explain the coefficient change with three regressions',
      block('The omitted-variable identity names both ingredients of the change',table(['Regression','Coefficient'],[['Rate on lead: short slope',f'{d["bs"][1]:.5f}'],['Rate on lead and urban: lead slope',f'{d["bl"][1]:.5f}'],['Rate on lead and urban: urban coefficient γ',f'{d["bl"][2]:.5f}'],['Urban on lead: sorting slope δ',f'{d["sorting"][1]:.5f}']], 'Identical 150-store sample in all three fits'),
        'The positive location coefficient says urban stores have higher fitted rates at a fixed delivery time in this additive model. The negative sorting slope says urban location becomes less common as delivery time rises. Their product pulls the short-model delivery slope downward.')+
      block('The signs and arithmetic explain why the short slope is smaller',formula(f'{d["bs"][1]:.5f} ≈ {d["bl"][1]:.5f} + ({d["bl"][2]:.5f} × {d["sorting"][1]:.5f})'),
        f'The product is {d["ovb_product"]:.5f} points per day. Adding it to the longer-model slope recovers the short slope before rounding. This is the lead-plus-urban comparison, not the later model with demand, promotions, and an interaction. Naming each model prevents the arithmetic from being applied to unrelated coefficients.'))
    put('calculate','Construct complete adjusted profiles',
      block('The richer equation includes every input used by the profile',formula('Rate = b₀ + b₁lead + b₂urban + b₃(demand−100) + b₄promotion + b₅lead×urban'),
        'The design row is [1,lead,urban,demand−100,promotion,lead×urban]. Multiply each element by its coefficient and sum. For a nonurban store the location and product terms vanish; for an urban store both contribute. The coefficients are in the earlier uncertainty table.')+
      block('The fitted group lines compare the same demand and promotion scenario',graph('Adjusted group profiles',np.array([2,5]),np.array([9,16]),'Delivery time (days)','Fitted rate (%)',lines=[(d['grid'],b[0]+b[1]*d['grid']+b[4]*.25,'#276451',False),(d['grid'],b[0]+b[1]*d['grid']+b[2]+b[4]*.25+b[5]*d['grid'],'#3259a2',True)],show_points=False,desc='Green solid: nonurban. Blue dashed: urban. Demand=100, promotion share=.25. Lines are model predictions, not raw store observations.'),
        f'The nonurban slope is {b[1]:.3f} points/day and the urban slope is {b[1]+b[5]:.3f}. These are estimated lines. Their apparent separation concerns level differences as well as slope differences; the slope test alone does not test whether the lines coincide.')+
      block('Two complete four-day profiles differ by the main and interaction terms together',table(['Profile: demand 100, promotion .25','Fitted rate'],[['Nonurban, four days',f'{b[0]+4*b[1]+.25*b[4]:.3f}%'],['Urban, four days',f'{b[0]+4*b[1]+b[2]+.25*b[4]+4*b[5]:.3f}%'],['Urban minus nonurban',f'{b[2]+4*b[5]:.3f} points']], 'Difference = urban coefficient + 4 × interaction coefficient'),
        'Hold every other input fixed. The intercept, demand, and promotion terms cancel in the subtraction. This is a comparison of fitted baseline outcomes, which can inform which stores deserve a closer operating review.'))
    put('interpret','Put uncertainty around the comparison that matters',
      block('Centering delivery at three days gives the group coefficient a useful reference',table(['Coefficient meaning','Lead uncentered','Lead−3 centered'],[['Urban difference at reference',f'{b[2]:.3f} at zero days',f'{d["bc"][2]:.3f} at three days'],['Lead×urban coefficient',f'{b[5]:.3f}',f'{d["bc"][5]:.3f}'],['Predictions','Original profiles','Identical profiles']], 'Reference changes; fitted values and slope difference do not'),
        'Lead=0 is outside the observed two-to-five-day range. Replacing lead with lead−3 moves the urban coefficient to a supported operating value. The new intercept is the nonurban fitted value at three days, demand 100, and promotion zero. Centering changes coefficient meanings and their covariance, not the model’s predictions.')+
      block('Meaningful group differences can be precise even when a reference coefficient is not',table(['Lead days','Urban difference','HC1 SE','95% interval'],[[int(v[0]),f'{v[1]:.3f}',f'{v[2]:.3f}',f'{v[3]:.3f} to {v[4]:.3f}'] for v in d['contrasts']], 'Contrasts hold demand and promotion fixed; units are percentage points'),
        'For lead L, the contrast row is [0,0,1,0,0,L]. Its estimate is cᵀb and its variance is cᵀVc. Coefficient covariance matters: adding separate interval endpoints does not construct the correct interval. The slope difference can be uncertain while differences at supported profiles are estimated precisely.')+
      block('The joint test finds a group difference without establishing different slopes',formula(f'Robust joint Wald χ²(2) = {d["wald"]:.2f}; p < 0.001'),
        f'Test urban=0 and lead×urban=0 together, holding demand and promotion terms in the model. The computed p-value is {d["wald_p"]:.3g}. The joint null of coincident lines is rejected, while the slope-only p-value is {d["p_value"][5]:.3f}. The results answer different questions: the joint rejection can be driven by level differences.'))
    put('model-comparison','Add complexity for a defined comparison',
      block('Adjusted R-squared accounts for parameters consumed by the fit',formula('Adjusted R² = 1 − [SSE/(n−p)] / [SST/(n−1)]'),
        'Here p counts every estimated coefficient, including the intercept. Ordinary training R² cannot decrease when independent columns are added to a nested OLS model on the same rows. Adjusted R² can decrease because it accounts for the degrees of freedom used. Neither statistic estimates future forecasting accuracy.')+
      block('The same-sample comparison separates fit gains from extra parameters',table(['Model','p','R²','Adjusted R²','RMSE'],[[a,k,f'{r:.3f}',f'{ar:.3f}',f'{rm:.3f}'] for a,k,r,ar,rm in d['fit_rows']], '150 rows throughout; RMSE in rate points'),
        'The additive model includes lead, urban, demand, and promotions. The group-slopes model then adds lead×urban. The final model adds centered demand squared. The table evaluates training fit; Lesson 6 evaluates forecasting procedures on later data.')+
      block('A quadratic extends the controlled model with a changing demand slope',formula(f'Added term: {d["bq"][-1]:.4f} × [(demand−100)/10]²'),
        f'Keep all six earlier columns and add the square. In this model the demand slope is {d["bq"][3]:.4f} + 2×({d["bq"][-1]:.4f})×(demand−100)/100 points per index unit. Interpret the linear and squared terms together. The fit comparison shows the actual gain in these stores, rather than assuming a more flexible specification must be operationally better.'))
    top=int(np.argmax(d['residual']));bottom=int(np.argmin(d['residual']))
    put('residual-review','Use model errors to choose the next practical inquiry',
      block('Above the diagonal means more stockouts than the model fits',graph('Observed versus fitted baseline rates',d['fitted'],d['y'],'Fitted rate (%)','Observed rate (%)',diagonal=True,labels=[(d['fitted'][top],d['y'][top],s.iloc[top].store_id),(d['fitted'][bottom],d['y'][bottom],s.iloc[bottom].store_id)],desc='Fitted values are horizontal; observed values are vertical. Positive residuals lie above the diagonal.'),
        'A residual is observed minus fitted. Read its sign from the stated axes. The original hotel plot put observed values on the horizontal axis, so its above/below interpretation was reversed; this lesson consistently uses fitted horizontal and observed vertical.')+
      block('Residuals identify stores whose observed outcomes need another explanation',table(['Store','Observed','Fitted','Residual'],[[s.iloc[i].store_id,f'{d["y"][i]:.2f}',f'{d["fitted"][i]:.2f}',f'{d["residual"][i]:.2f}'] for i in np.argsort(d['residual'])[-5:][::-1]], 'Largest positive residuals from the six-column model'),
        'For these stores, inspect delivery disruptions, unrecorded practices, and measurement. The residual shortlist asks where to learn more; it does not establish who caused the difference. Keep the outcome period and compared profile visible during that conversation.')+
      block('A residual plot asks whether unexplained spread changes with the fitted rate',graph('Residuals versus fitted values',d['fitted'],d['residual'],'Fitted rate (%)','Observed − fitted (points)',lines=[(np.array([min(d['fitted']),max(d['fitted'])]),np.zeros(2),'#9b421e',True)],desc='The zero line separates underprediction from overprediction. Each dot is one store.'),
        'Look for systematic curvature, changing spread, or individual records that deserve investigation. Robust SEs address coefficient uncertainty under unequal variance, but they do not remove a missing mean pattern. Review the model and records together before expanding the operating use.'))
    put('act','Decide where this comparison can be used next',block('Use the baseline comparison to design a testable operating review',bullets('Report a complete profile and its uncertainty','Distinguish group-level differences from slope differences','Investigate stores with large residuals','Check transfer before using the model in a new setting'),
      'Suppose a new region has seven-day delivery cycles and a different promotion system. Those profiles extend beyond the observed delivery range and change the operating setting. Start by collecting comparable outcomes and validating the relationship there. For existing stores, Lesson 6 will turn the explanatory inputs into a procedure that can be evaluated before next week’s outcomes are known.'))
    c['memo']='Report adjusted profile differences with their uncertainty. The fitted delivery slopes are 1.531 and 1.759 points/day, but their difference is not established at 5%. The joint test and supported profile contrasts show location-related differences. Use the residual shortlist to guide operating review and validate any forecasting use.'
    c['question']='How can the group-lines joint test reject while the slope-difference test does not?'
    c['answer']='The joint test asks whether both level and slope differences are zero. A level difference can drive its rejection even when the slope difference is imprecise. State which comparison each test addresses.'
    c['truth']='The baseline mechanism includes a delivery-by-location interaction. Its known presence does not guarantee that a particular sample yields a statistically significant estimate. Compare the estimate and interval with the mechanism only after interpreting the observed data.'
    c['technical'][1]='Run the same fits, covariance calculations, pointwise bands, contrasts, joint tests, and nested comparisons used in the main lesson. The added code also verifies the omitted-variable identity and unchanged predictions after centering.'
    c['technical'][3]='Change the reference delivery time and verify that fitted values stay fixed. Then change one profile contrast and recalculate its variance from the full covariance matrix. Compare a joint restriction with an individual restriction.'
    detail=[
      (formula('b = (XᵀX)⁻¹Xᵀy; classical Var(b) = s²(XᵀX)⁻¹'),'X contains an intercept and all transformed input columns. Its full column rank identifies unique coefficients. Use a least-squares solver rather than a matrix inverse for estimation. Here p is the number of columns including the intercept, and s²=SSE/(n−p).'),
      (formula('SE(slope)=s/√Sxx; SE(intercept)=s√[1/n+X̄²/Sxx]'),'For simple OLS, Sxx=Σ(X−X̄)² and s²=SSE/(n−2). Under independent normal constant-variance errors, coefficient statistics follow Student t with n−2 degrees of freedom. An intercept at a distant zero can be imprecise even when mean predictions near X̄ are precise.'),
      (formula('HC1 = [n/(n−p)] B Xᵀdiag(e²)XB; B=(XᵀX)⁻¹'),'HC3 replaces each eᵢ² by eᵢ²/(1−hᵢ)² without the HC1 prefactor; hᵢ=xᵢᵀBxᵢ. Both preserve OLS coefficients and allow heteroskedasticity across independent rows. The displayed robust intervals use HC1 and a normal reference; the classical band uses a t reference and constant future variance.'),
      (formula('Var(mean at x₀)=x₀ᵀVar(b)x₀; classical prediction variance=s²+x₀ᵀs²Bx₀'),'The added s² represents a new independent outcome’s variance. For simple regression this becomes s²[1+1/n+(x₀−X̄)²/Sxx]. A robust covariance estimate for b does not automatically determine that new outcome’s conditional variance. The plotted bands are pointwise, and target the same eight-week store-average measurement.'),
      (formula('Estimate=cᵀb; SE=√(cᵀVc)'),'For an urban-minus-nonurban comparison at lead L, c=[0,0,1,0,0,L]. Thus variance=Vurban,urban+L²Vinteraction,interaction+2L Vurban,interaction. For the urban lead slope, c=[0,1,0,0,0,1]. Using the covariance terms is essential when adding coefficients.'),
      (formula('W = (Rb−r)ᵀ(RVRᵀ)⁻¹(Rb−r) → χ²(q)'),'R selects the tested linear combinations and r states their null values. Here R selects urban and lead×urban, r is zero, and q=2. HC1 supplies V. This asymptotic robust Wald test differs from the exact classical F test under normal constant-variance errors.'),
      (formula('F = [(SSE restricted−SSE full)/q] / [SSE full/(n−p)]'),f'The restricted model omits both location terms but retains lead, demand, and promotions. On the same 150 observations, F={d["F"]:.3f} with (2,144) degrees of freedom and p={d["F_p"]:.3g}. Its constant-variance justification is separate from the HC1 Wald result.'),
      (table(['Term','VIF before centering','VIF after lead−3'],[[name,f'{d["raw_vif"][j]:.2f}',f'{d["centered_vif"][j]:.2f}'] for j,name in [(1,'Urban'),(4,'Lead×urban')]],'Reparameterizing these interaction columns'), 'For each non-intercept column, regress it on all other columns and compute VIF=1/(1−R²). Centering can reduce reference-related overlap in an interaction basis, but does not create new information or fix fundamentally redundant predictors. Fitted values, residuals, and equivalent contrasts remain unchanged.'),
      (formula('Current model: group-specific intercept and lead slope; shared demand and promotion slopes'),'Separate unrestricted group fits would also allow the demand and promotion coefficients to differ. They match a pooled model only when the corresponding group interactions are included. As an optional extension, add centered-demand×promotion and interpret its demand slope at two promotion shares; keep the main terms and evaluate the resulting comparison on the same rows.'),
    ]
    c['appendix_extra']='<section id="multiple-regression-details"><h2>Reconstruct uncertainty and adjusted comparisons</h2>'+''.join(block(title,visual,note) for title,(visual,note) in zip(DETAIL_TITLES,detail))+'</section>'
    next(s for s in c['sections'] if s['id']=='calculate')['body']+=step_link(5,'calculation')
    return c
