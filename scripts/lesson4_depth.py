"""Regression geometry and functional forms, with one shared retail sample.

The executable lab is also the source of the plotted model calculations.
Demand is explicitly introduced for continuous-shape comparisons; delivery
time remains the predictor in the introductory OLS and log calculations.
"""
from functools import lru_cache
import numpy as np
from lesson2_depth import figure, text

DETAIL_TITLES = [
    'The OLS first-order equations make sample residuals orthogonal to fitted values',
    'Orthogonality makes the summed squared deviations add',
    'Simple-regression R-squared equals squared sample correlation',
    'Exact log changes use the ratio of the two predictor values',
    'Retransforming a log outcome requires a target on the original scale',
    'Rescaling a predictor changes coefficient units without changing fitted values',
    'A hinge basis makes a spline continuous at its knot',
    'Local linear regression repeats a weighted fit at each target',
    'Influence measures how much a fitted conclusion depends on a record',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    from curriculum_worked import WORKED
    ns=dict(retail_case.__dict__)
    exec(compile(WORKED[4],'lesson4-shared-calculations','exec'),ns)
    return ns

def path(xs,ys,sx,sy,color,dash=False):
    points=' '.join(f'{sx(x):.2f},{sy(y):.2f}' for x,y in zip(xs,ys))
    return f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.8"'+(' stroke-dasharray="7 4"' if dash else '')+'/>'

def chart(title,x,y,xlabel,lines=(),marks=(),desc='',ylim=None,residual=None):
    lo,hi=float(min(x)),float(max(x)); pad=(hi-lo)*.07
    xmin,xmax=lo-pad,hi+pad
    vals=np.concatenate([np.asarray(y)]+[np.asarray(v[1]) for v in lines])
    ymin,ymax=ylim or (float(vals.min())-1,float(vals.max())+1)
    sx=lambda v:70+580*(v-xmin)/(xmax-xmin)
    sy=lambda v:250-195*(v-ymin)/(ymax-ymin)
    body=text(70,23,'Stockout rate (%)' if not title.startswith('Residual') else 'Residual (percentage points)',14)
    for tick in np.linspace(ymin,ymax,5):
        yy=sy(tick);body+=f'<line x1="70" x2="650" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#dce4da"/>'+text(62,yy+4,f'{tick:.1f}',12,'end')
    ticks=np.arange(2,6) if lo==2 and hi==5 else np.linspace(lo,hi,5)
    for tick in ticks:body+=text(sx(tick),274,f'{tick:.0f}' if tick>=20 else f'{tick:g}',13,'middle')
    for xx,yy in zip(x,y):body+=f'<circle cx="{sx(xx):.2f}" cy="{sy(yy):.2f}" r="2.7" fill="#677c73" opacity=".5"/>'
    for xx,yy,color,dash in lines:body+=path(xx,yy,sx,sy,color,dash)
    for xx,yy,label,col in marks:
        body+=f'<circle cx="{sx(xx):.2f}" cy="{sy(yy):.2f}" r="5" fill="{col}"/>'+text(sx(xx)+8,sy(yy)-9,label,13)
    if residual:
        xx,actual,fitted=residual
        body+=f'<line x1="{sx(xx):.2f}" x2="{sx(xx):.2f}" y1="{sy(actual):.2f}" y2="{sy(fitted):.2f}" stroke="#b65b32" stroke-width="4"/>'
        body+=text(sx(xx)+9,sy(actual)+16,'S001: actual 9.20%',13)
        body+=text(sx(xx)+9,sy(fitted)-8,'fitted 13.43%',13)
    body+=text(360,312,xlabel,15,'middle')
    return figure(title,body,desc)

def decomposition():
    # Generic geometry: lengths add for one observation, squares only in aggregate.
    body=text(35,25,'One observation: y − mean = fitted − mean + residual',17)
    for yy,label,col in [(75,'Observed y','#b65b32'),(155,'Fitted y','#276451'),(260,'Mean y','#183f36')]:
        body+=f'<line x1="130" x2="620" y1="{yy}" y2="{yy}" stroke="{col}" stroke-dasharray="5 4"/>'+text(20,yy+5,label,15)
    for xx,ya,yb,label,col in [(220,75,260,'Total deviation','#3259a2'),(390,155,260,'Fitted deviation','#276451'),(560,75,155,'Residual','#b65b32')]:
        body+=f'<line x1="{xx}" x2="{xx}" y1="{ya}" y2="{yb}" stroke="{col}" stroke-width="4"/>'
        body+=text(xx+10,(ya+yb)/2-9,label,13)
    body+=text(360,310,'After squaring and summing: SST = SSR + SSE',17,'middle')
    return figure('Deviations add for one row; squared deviations add across the fitted sample',body,'Schematic, not a particular store. The OLS cross-product sums to zero when the model includes an intercept; individual squared deviations do not simply add.')

def log_axes(x,y,coef,smear):
    body='';grid=np.linspace(2,5,121)
    for j,(values,pred,label) in enumerate([(np.log(y),coef[0]+coef[1]*grid,'ln(stockout rate)'),(y,np.exp(coef[0]+coef[1]*grid)*smear,'Stockout rate (%)')]):
        left=55+350*j;lo=float(min(values))-.1*(max(values)-min(values));hi=float(max(values))+.1*(max(values)-min(values))
        sx=lambda v:left+240*(v-1.8)/3.4;sy=lambda v:245-180*(v-lo)/(hi-lo)
        body+=text(left,25,label,16)
        for tick in np.linspace(lo,hi,4):
            yy=sy(tick);body+=f'<line x1="{left}" x2="{left+245}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="#dce4da"/>'+text(left-6,yy+4,f'{tick:.2f}' if j==0 else f'{tick:.1f}',12,'end')
        for xx,yy in zip(x,values):body+=f'<circle cx="{sx(xx):.2f}" cy="{sy(yy):.2f}" r="2.3" fill="#677c73" opacity=".5"/>'
        body+=path(grid,pred,sx,sy,'#276451')
        for v in range(2,6):body+=text(sx(v),271,v,13,'middle')
    body+=text(360,315,'Usual delivery time (days)',15,'middle')
    return figure('A line on the log-outcome scale becomes a curve on the rate scale',body,'Same stores and log-level fit. Left: predicted log rate. Right: exponentiation plus the common residual smearing factor gives rate-scale predictions.')

def restore(c):
    from retail_ui import section,table,formula
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();s=d['stores'];x=d['x'];y=d['y'];b=d['beta'];fitted=d['fitted'];err=d['residual']
    calc=next(v for v in c['sections'] if v['id']=='calculate')
    calc['body']=calc['body'].replace('6.96 + 1.62 × 4 = 13.43%', '6.95803 + 1.61872 × 4 ≈ 13.43292%')
    def block(title,visual,*notes):return teach(title,visual,list(notes))
    def put(key,heading,body,before=None,phase='Worked application'):
        item=dict(**section(key,heading,body),phase=phase)
        old=next((i for i,v in enumerate(c['sections']) if v['id']==key),None)
        if old is not None:c['sections'][old]=item
        else:c['sections'].insert(next(i for i,v in enumerate(c['sections']) if v['id']==before),item)
        c['headlines'][key]=[title for title,_ in visual_frames(Tree(body).root,heading)]
    put('theory-model-choice','Choose what the regression is meant to represent',
        block('Description, prediction, and intervention ask different questions',table(['Purpose','Question'],[
            ['Description','How does average Y vary with X in these records?'],['Prediction','How well can X anticipate an unknown Y?'],['Intervention','What would happen to Y if we changed X?']], 'The same fitted equation can support different tasks'),
            'Regression describes a conditional relationship. Predictive use additionally requires evidence about new observations; causal use requires a design that identifies an intervention effect. Begin with the question, then decide what evidence the fitted relationship needs. This lesson develops the equation and its fit; later lessons add validation and intervention designs.')+
        block('A model can be nonlinear in X while remaining linear in its coefficients',bullets('A straight line chooses one global slope','Logs and powers change the predictor or outcome scale','Group means and local fits allow more flexible shape','Linear in coefficients includes a + b₁X + b₂X²'),
            'Parametric regression chooses a finite equation and estimates its coefficients. A quadratic bends in X but remains linear in a, b₁, and b₂, so ordinary least squares can fit its transformed columns. Local smoothing instead repeats small fits near each target. All approaches make choices about smoothness or grouping; flexible does not mean assumption-free. A power curve aXᵇ differs from an exponential curve a exp(bX).')+
        block('OLS with an intercept balances residuals around the observed mean',formula('Σeᵢ = 0; mean(Ŷ) = Ȳ; a + bX̄ = Ȳ'),
            'These are algebraic properties of the fitted sample, not assumptions that population errors disappear. They follow from minimizing squared residuals with an intercept. In simple regression the line passes through the point (X̄,Ȳ). The residuals may still show curvature or unequal spread, even though their sum is zero. The appendix derives these identities from the first-order equations.'),
        before='theory-method',phase='General theory')
    put('theory-fit-geometry','See the pieces behind the fit statistics',
        block('The variation decomposition separates fitted movement from residual movement',decomposition(),
            'For each observation, yᵢ−ȳ = (ŷᵢ−ȳ)+eᵢ. Squaring produces an additional cross-term. In OLS with an intercept, the sum of that cross-term is zero, giving SST=SSR+SSE. The coloured lengths in the schematic are deviations, not sums of squares. The arithmetic in the retail application uses all 150 rows.')+
        block('Logs express proportional changes rather than a fixed unit difference',bullets('Use positive quantities and state the units','A log difference is ln(Y₂/Y₁)','Multiplicative relationships become additive on a log scale','Choose the relationship, then inspect the transformed fit'),
            'Logging can make a proportional relationship easier to express and can reduce a long right tail. A skewed predictor does not by itself require a log: examine the conditional pattern and the meaning of proportional changes. For a logged predictor, the intercept corresponds to X=1 in the stated units. Zero has no finite logarithm; changing zero to a small constant changes the analysis and needs a substantive measurement rule.'),
        before='read-data',phase='General theory')
    # Introductory OLS retains the delivery predictor, sample, and original results.
    group=s.groupby('lead_days').baseline_rate
    coarse=np.where(x<=3,y[x<=3].mean(),y[x>3].mean())
    four=group.transform('mean').to_numpy()
    grids=np.linspace(2,5,121)
    groups_desc='Four group sizes: 32, 39, 40, and 39 stores. Dots remain at their actual delivery values; overlapping dots can hide records.'
    put('from-bins','Build the relationship from increasingly specific predictions',
        block('An overall mean gives every store the same prediction',chart('The overall mean ignores differences in delivery time',x,y,'Usual delivery time (days)',[(grids,np.full(len(grids),y.mean()),'#3259a2',True)],desc=f'All 150 baseline stores. The dashed line is the overall mean, {y.mean():.2f}%. '+groups_desc),
            'The mean is the least-squares prediction when the model has only an intercept. It uses no information about delivery time. Plot the individual stores before summarizing them: stores with the same delivery time still have different stockout rates.')+
        block('Group means adapt the prediction while sharing it within each group',chart('Grouping lets fitted rates differ across delivery patterns',x,y,'Usual delivery time (days)',[(np.array([2,3.49,3.5,5]),np.array([y[x<=3].mean()]*2+[y[x>3].mean()]*2),'#b65b32',True)],[(v,float(group.mean().loc[v]),f'n={int((x==v).sum())}','#276451') for v in range(2,6)],desc='Orange dashed segments: two groups, 2–3 versus 4–5 days. Green markers: four exact delivery-group means. The vertical connector marks the bin boundary, not an observed transition.'),
            f'The two group means are {y[x<=3].mean():.3f}% for 71 stores and {y[x>3].mean():.3f}% for 79 stores. Every store in a group receives its group mean as its fitted value. Four delivery groups allow more detail: 10.23%, 11.92%, 13.14%, and 15.22%. A binned scatter summarizes mean Y at a chosen representative X; for continuous bins use the actual mean X or explicitly label a midpoint.',
            'Check: which variation is hidden by the green points? They retain between-group differences but hide the distribution of individual rates inside each group. Showing the raw dots alongside the summaries preserves that information.')+
        block('Covariance and predictor variance reconstruct the fitted line',table(['Step','Value'],[
            ['Mean delivery time; mean rate',f'{x.mean():.4f} days; {y.mean():.4f}%'],['Sample covariance; sample X variance',f'{np.cov(x,y,ddof=1)[0,1]:.4f}; {x.var(ddof=1):.4f}'],['Slope = covariance / variance',f'{b[1]:.5f} percentage points per day'],['Intercept = mean Y − slope × mean X',f'{b[0]:.5f}%']], 'Calculate with full precision; round only for display'),
            'The covariance has units of days times percentage points; the predictor variance has units of days squared. Their ratio therefore has units of percentage points per day. Both sample quantities use the same n−1 divisor, which cancels in the ratio. The intercept is a mathematical anchor at zero delivery days, outside the observed two-to-five-day range; use predictions in the observed range for the case.'),
        )
    put('line-geometry','Locate observations, fitted values, and residuals',
        block('The fitted line passes through the means and leaves vertical residuals',chart('A store’s residual is its vertical distance from the fitted line',x,y,'Usual delivery time (days)',[(grids,b[0]+b[1]*grids,'#276451',False)],[(x.mean(),y.mean(),'Mean point','#3259a2')],desc='Same 150 stores. Blue point: (3.573 days, 12.742%). Orange segment: S001 actual minus fitted rate.',residual=(4,y[0],fitted[0])),
            f'S001 has actual rate {y[0]:.5f}% and fitted rate {fitted[0]:.5f}%, so its residual is {err[0]:.5f} percentage points. A positive residual would place a point above the line. The one-day slope describes movement along the line across stores; a residual describes one store’s departure from that line. The fitted line balances the signed residuals, while minimizing their squared total.'),before='interpret')
    # Preserve the existing numerical fit table; add graphical diagnosis next.
    put('residual-patterns','Use the residual pattern to decide what to investigate',
        block('Residual patterns reveal what a single slope leaves behind',chart('Residuals should be examined against the predictor, not only in a histogram',x,err,'Usual delivery time (days)',[(grids,np.zeros(len(grids)),'#183f36',True)],desc='All fitted residuals, in percentage points. Their average is zero; this alone does not establish that the relationship is well represented.'),
            'Look for systematic movement of residual centres with delivery time, a change in their spread, and records far from the rest. Here each delivery group has substantial within-group variation. The mean residuals are small relative to that spread, consistent with the modest difference between the line and the four group means. The next lesson adds recorded operating conditions to explain more of the differences.')+
        block('An unusual record and an influential record are different findings',table(['Question','Action'],[
            ['Large residual: unusual Y given X?','Check the recorded outcome, period, and denominator'],['Extreme X: unusual predictor value?','Check units and the support for this comparison'],['Influence: does the fitted conclusion change?','Refit with one record omitted as a sensitivity check']], 'Investigate records before changing the analysis sample'),
            f'For the delivery slope, removing one store at a time identifies {s.iloc[d["influential"]].store_id} as producing the largest absolute change: the slope moves from {b[1]:.5f} to {d["leave_slopes"][d["influential"]]:.5f} points per day. This small observed change supports stability of that particular slope to single-record omission; it does not establish that the model captures every relevant feature.',
            'The sensitivity fit is a diagnostic, not an instruction to delete the store. Verify a suspected error against its source, correct only an established error, and document any eligibility change. Accurate extreme observations can be important business cases. A positive residual alone does not show poor management.'),before='functional-form')
    forms=d['form_fits'];names=['Level–level','Log–level','Level–log','Log–log']
    colors=['#183f36','#b65b32','#3259a2','#8b488c'];lines=[]
    for j,(coef,smear,rmse) in enumerate(forms):
        xx=np.log(grids) if j>=2 else grids;pred=coef[0]+coef[1]*xx
        if j in [1,3]:pred=np.exp(pred)*smear
        lines.append((grids,pred,colors[j],j%2==1))
    dx=d['dx'];grid=d['grid'];cf=d['curve_fits'];q=cf[2][0];sp=d['spline_coef']
    put('functional-form','Interpret transformations and compare their implied shapes',
        block('Four equations express four different meanings of a slope',table(['Model','Fitted equation','Rate-scale RMSE'],[
            [names[0],f'Ŷ = {forms[0][0][0]:.3f} + {forms[0][0][1]:.3f}X',f'{forms[0][2]:.3f}'],
            [names[1],f'fitted ln Y = {forms[1][0][0]:.3f} + {forms[1][0][1]:.3f}X',f'{forms[1][2]:.3f}'],
            [names[2],f'Ŷ = {forms[2][0][0]:.3f} + {forms[2][0][1]:.3f}ln X',f'{forms[2][2]:.3f}'],
            [names[3],f'fitted ln Y = {forms[3][0][0]:.3f} + {forms[3][0][1]:.3f}ln X',f'{forms[3][2]:.3f}']], 'Same 150 stores; X = delivery days, Y = stockout rate in percent'),
            'For models fitted to log Y, the equation predicts the average log outcome. The RMSE column returns predictions to the rate scale using exp(fitted log Y) times the mean exp(log residual). This common scale permits a meaningful fit comparison. It does not make raw log-scale R² or squared errors directly comparable to their level-scale counterparts. All rows use the same stores.')+
        block('A small log coefficient still needs an explicit unit calculation',table(['Model and change','Exact fitted change','Interpretation'],[
            ['Level–level: +1 day',f'{b[1]:.3f} points','A percentage-point difference in the rate'],
            ['Log–level: +1 day',f'{100*np.expm1(forms[1][0][1]):.2f}%','Relative rate change; about 13.0% by approximation'],
            ['Level–log: X increases 1%',f'{forms[2][0][1]*np.log(1.01):.4f} points','Slope × ln(1.01)'],
            ['Log–log: X increases 1%',f'{100*np.expm1(forms[3][0][1]*np.log(1.01)):.3f}%','Relative change; about 0.425% by approximation']], 'Percentage points and percentage changes answer different questions'),
            'A rise from 10% to 11% is one percentage point and a 10% relative increase. These examples interpret the fitted equations; delivery time is observed only at whole-day values, so the 1% changes are mathematical illustrations of the model. For a log outcome, the finite-change percentages describe the exponentiated fitted-log scale and also the smearing-adjusted mean prediction when the smearing factor is held constant.',
            'Check: if the log-log slope were −0.25, would 1% more X mean 25% less Y? No: the local approximation is 0.25% less Y. The coefficient is an elasticity, a ratio of proportional changes.')+
        block('Different equations can produce similar fitted rates over the observed range',chart('The four forms imply modest differences in this delivery range',x,y,'Usual delivery time (days)',lines,desc='Level–level: dark solid; log–level: orange dashed; level–log: blue solid; log–log: purple dashed. Log outcomes use residual smearing.'),
            'The curves nearly overlap here, and their training RMSEs range from about 1.60 to 1.64 points. Their interpretations still differ. A log-level equation is exponential in X; a log-log equation is a power curve. Choose a form for the question and plausible relationship, then assess it. Similar training fit is not evidence that the equations agree beyond the observed range.')+
        block('Changing the outcome scale changes the shape of the same fitted equation',log_axes(x,y,forms[1][0],forms[1][1]),
            'The left panel fits a straight line to log rates. Returning to rates produces a gently convex curve: a fixed proportional increase is a larger absolute increase when the starting rate is larger. The right panel multiplies exp(fitted log rate) by the common smearing factor 1.00862. Distances from these two curves have different units, so squared residuals on the two panels are not directly comparable. The underlying store records have not changed.')+
        block('Continuous demand reveals shape that four delivery values cannot identify',chart('Demand permits a continuous comparison of linear and curved fits',dx,y,'Baseline demand index',[(grid,cf[k][2],colors[k-1],k==3) for k in [1,2,3]],desc='Same stores and outcome; new predictor: baseline demand. Linear: dark; quadratic: orange; cubic: blue dashed.'),
            f'We now hold the business case and 150 stores fixed but change the predictor to baseline demand. Its continuous values let us examine curve shape. The training RMSEs are {cf[1][3]:.3f}, {cf[2][3]:.3f}, and {cf[3][3]:.3f} points for the line, quadratic, and cubic. Curvature is modest relative to the spread among stores. These are demand models, so their coefficients must not be read as delivery-time slopes.',
            'A cubic on delivery time has four coefficients for only four distinct X values, and reproduces the four group means. It does not supply observations between those values. The demand comparison provides a more useful setting for the original lesson’s curve discussion while keeping the same running example.')+
        block('A quadratic slope changes with the predictor value',formula(f'Ŷ = {q[0]:.3f} + {q[1]:.3f}z − {abs(q[2]):.3f}z²; z = (demand − 100)/10'),
            f'The slope per demand-index point is ({q[1]:.5f} + 2 × {q[2]:.5f}z)/10. At demand 90 (z=−1), it is {(q[1]-2*q[2])/10:.4f} stockout percentage points per index point; at demand 120 (z=2), it is {(q[1]+4*q[2])/10:.4f}. Read the linear and squared terms jointly. The division by ten converts the slope in z units back to the original index.',
            'The displayed quadratic eventually turns downward near the upper edge. That is a feature of its fitted equation, not proof that raising demand reduces stockouts. Inspect the actual data density and restrict interpretation to supported comparisons. The cubic adds a 3b₃z² term to the derivative; the appendix shows the general calculation.')+
        block('A spline changes its slope at a named knot while remaining continuous',chart('The demand spline permits a flatter relationship after index 110',dx,y,'Baseline demand index',[(grid,d['spline_line'],'#276451',False)],[(110,sp[0]+sp[1],'Knot 110','#b65b32')],desc='Illustrative knot at demand index 110, not an estimated optimal threshold. The line is continuous where its slope changes.'),
            f'Fit Ŷ = {sp[0]:.3f} + {sp[1]:.3f}z − {abs(sp[2]):.3f}max(z−1,0), where z=(demand−100)/10. Below 110, the slope per index point is {sp[1]/10:.4f}; above 110 it is {(sp[1]+sp[2])/10:.4f}. Both pieces give {sp[0]+sp[1]:.3f}% at the knot, so there is no jump. The knot is chosen for this teaching comparison, not claimed as a policy boundary.')+
        block('The hinge column switches on only after the knot',table(['Demand','z','max(z−1,0)','Fitted rate (%)'],[[v,f'{(v-100)/10:g}',f'{max((v-100)/10-1,0):g}',f'{sp[0]+sp[1]*(v-100)/10+sp[2]*max((v-100)/10-1,0):.3f}'] for v in [100,110,120]], 'Compute each fitted value from the same three columns'),
            'Below the knot, the hinge term contributes zero. Above it, the term adds a change in slope rather than a new intercept jump. At the knot it is exactly zero. Check: is the upper-segment slope the hinge coefficient alone? No: add the original slope and the hinge coefficient, then convert from z units to demand-index units.')+
        block('A wider local neighborhood produces a smoother description',chart('Local fits use nearby stores rather than one global equation',dx,y,'Baseline demand index',[(grid,d['smooth35'],'#b65b32',False),(grid,d['smooth65'],'#3259a2',True)],desc='Local linear fits with tricube distance weights: nearest 35% of stores (orange) versus 65% (blue dashed); no robust reweighting iterations.'),
            'At each target demand, choose the nearest fraction of stores, weight closer observations more heavily, fit a small line, and evaluate it at the target. Repeat along the horizontal axis. The 35% curve follows more local movement; the 65% curve pools a broader neighborhood. At the boundary, the neighborhood lies mostly on one side, which affects how much local information is available.',
            'Compare the broad pattern rather than interpreting every wiggle as a business mechanism. The code uses an explicit local-linear rule so the curves can be reproduced. It is a LOWESS-style exploration, not a separate prediction validation exercise. Lesson 6 tests candidate procedures on new observations.'),
        )
    # A coherent technical continuation, not an unrelated second lecture.
    details=[]
    def detail(i,visual,*notes):details.append(block(DETAIL_TITLES[i],visual,*notes))
    detail(0,formula('∂SSE/∂a = −2Σeᵢ = 0; ∂SSE/∂b = −2ΣXᵢeᵢ = 0'),
        'With an intercept and nonconstant X, solve these equations to get b=Σ(X−X̄)(Y−Ȳ)/Σ(X−X̄)² and a=Ȳ−bX̄. Thus mean fitted equals mean observed. Since fitted values are a+bX, Σŷᵢeᵢ=aΣeᵢ+bΣXᵢeᵢ=0. These are estimation-sample identities; E[u|X]=0 is a separate population-model assumption.')
    detail(1,formula('Σ(Y−Ȳ)² = Σ(Ŷ−Ȳ)² + Σe² + 2Σ(Ŷ−Ȳ)e'),
        'The last term vanishes by the OLS equations and Σe=0. This gives the decomposition used in the main table. For this course SSR denotes explained variation and SSE residual variation; some software uses SSR for residual sums, so inspect definitions. The lab checks the cross-product and the sum numerically.')
    detail(2,formula('R² = b²Sxx/Syy = Sxy²/(Sxx Syy) = rXY²'),
        'Sxx=Σ(X−X̄)², Syy=Σ(Y−Ȳ)², and Sxy=Σ(X−X̄)(Y−Ȳ). Substitute b=Sxy/Sxx into explained variation b²Sxx. The identity applies to simple in-sample OLS with an intercept and nonzero variation. The observed value is 0.547877. Training MSE=SSE/n; an unbiased error-variance estimator under the usual homoskedastic linear model uses SSE/(n−2).')
    detail(3,table(['Form','Change from X₁ to X₂'],[
        ['Level–level','Δ fitted Y = b(X₂−X₁)'],['Log–level','% change = 100{exp[b(X₂−X₁)]−1}'],['Level–log','Δ fitted Y = b ln(X₂/X₁)'],['Log–log','% change = 100{(X₂/X₁)ᵇ−1}']], 'Log-outcome changes refer to the exponentiated fitted-log scale'),
        'For a small change, exp(t)−1≈t and ln(1+t)≈t. This yields the usual percentage interpretations. The exact formulas avoid factor-of-100 errors. Logged predictor values must be positive, and a change from X₁ to X₂ concerns the specified model, not automatically an intervention effect.')
    detail(4,formula('If ln Y = m(X)+u: E[Y|X] = exp(m(X)) E[exp(u)|X]'),
        'Exponentiating m(X)=E[ln Y|X] gives the conditional geometric mean. It is the conditional median only with a zero-median log error. A common smearing factor estimates E[exp(u)] by the sample mean of exp(log residual). Applying this factor at every X assumes the required retransformation factor is constant in X; otherwise model it conditionally. The observed log-level smearing factor is about 1.00862. The main comparison computes all errors in stockout percentage points.')
    detail(5,formula('z=(D−100)/10; dŶ/dD=(b₁+2b₂z+3b₃z²)/10'),
        'Centering and rescaling helps make polynomial columns easier to work with. Keep all lower-order terms with an intercept. The line, quadratic, and cubic use two, three, and four coefficients, respectively. A better nested training fit follows from added flexibility; test performance is a different question. The lab computes every curve from the same demand values and sample.')
    detail(6,formula('a+bz+c max(z−k,0) = a+bz below k; (a−ck)+(b+c)z above k'),
        'Both pieces equal a+bk at the knot. For several knots, add one hinge column max(z−kⱼ,0) per knot; each coefficient changes the slope after its knot. Here k=1 in z units equals demand 110. There is one intercept column. This avoids the discontinuity of unrelated segment equations and the redundant intercepts that can occur in an overcomplete spline basis.')
    detail(7,formula('wᵢ = [max{1−(|Dᵢ−d|/h)³,0}]³; fit Yᵢ ≈ a_d+b_d(Dᵢ−d)'),
        'At target d, h is the distance to the ceiling(fraction×n)-th nearest observation. Fit weighted least squares to columns 1 and D−d, and report a_d. The outermost observation has zero weight under this rule. Repeat for 121 targets between the observed minimum and maximum. The two fractions are 0.35 and 0.65. No residual-based robust iterations are performed; the implementation therefore need not match a library’s default LOWESS settings.')
    detail(8,formula('Delivery-slope sensitivityᵢ = b(without store i) − b(full sample)'),
        'A residual measures unusual Y conditional on a fitted model; leverage concerns an unusual predictor configuration; influence measures a change in a fitted result. In simple OLS with an intercept, leverage hᵢ=1/n+(Xᵢ−X̄)²/Σ(X−X̄)². Cook’s distance combines residual size and leverage to summarize influence on fitted values. The main exercise uses a directly interpretable leave-one-out slope difference and leaves all verified observations in the primary analysis.')
    c['appendix_extra']='<section id="regression-details"><h2>Derive the geometry and reproduce the curve comparisons</h2>'+''.join(details)+'</section>'
    return c
