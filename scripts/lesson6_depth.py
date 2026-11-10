"""Prediction theory, visual explanations, and one chronological worked analysis."""
from functools import lru_cache
import re
import numpy as np
from lesson2_depth import figure,text
from lesson5_depth import graph

CALCULATIONS = '''# Use one validation design for every forecasting procedure.
data = world()['panel'].query('3<=week<=16')
development = data.query('week<=13')
final_test = data.query('week>=14')
features = FORECAST_FEATURES
training = development.query('week<=7')
validation = development.query('8<=week<=9')
first_fit = fit_forecast(training,'Linear regression')
first_predictions = predict_forecast(first_fit,validation)
first_errors = validation.stockout_rate.to_numpy()-first_predictions
result, depth = prediction_analysis()
pooled_mse = sum(300*v*v for v in result['scores'][1]['fold_rmse'])/900
assert np.isclose(np.sqrt(pooled_mse),result['scores'][1]['rmse'])
assert np.isclose(np.sqrt(np.mean(first_errors**2)),result['scores'][1]['fold_rmse'][0])
# Inspect the complete input record before scoring its target week.
frozen = fit_forecast(development,result['selected'],depth['alpha'])
final_predictions = predict_forecast(frozen,final_test)
assert np.isclose(np.sqrt(np.mean((final_test.stockout_rate-final_predictions)**2)),result['rmse'])
clean_basis = forecast_basis(development[features])
assert clean_basis.shape == (1650,18)
assert np.linalg.matrix_rank(np.column_stack([np.ones(1650),clean_basis])) == 19
# A labelled missing-input exercise uses a copy of the first fold.
quality_train = training.copy(); quality_valid = validation.copy()
quality_train.loc[quality_train.store_id.isin(['S001','S002']), 'demand_forecast'] = np.nan
quality_valid.loc[quality_valid.store_id=='S001','demand_forecast'] = np.nan
median = quality_train.demand_forecast.median()
for frame in [quality_train,quality_valid]:
    frame['demand_missing'] = frame.demand_forecast.isna().astype(int)
    frame['demand_filled'] = frame.demand_forecast.fillna(median)
scale_mean = quality_train.demand_filled.mean()
scale_sd = quality_train.demand_filled.std(ddof=0)
quality_valid['demand_z'] = (quality_valid.demand_filled-scale_mean)/scale_sd
assert quality_valid.loc[quality_valid.demand_missing==1,'demand_filled'].eq(median).all()
# The log1p procedure learns its smearing factor on training residuals.
log_fit = fit_forecast(training,'Log-linear')
log_naive = np.expm1(log_fit[0].predict(validation[features]))
log_adjusted = predict_forecast(log_fit,validation)
assert np.allclose(log_adjusted,(log_naive+1)*log_fit[2]-1)
# Build coefficient paths on development data; alpha selection uses validation.
path_alphas = np.logspace(-3,1,25)
path_coefs = np.array([fit_forecast(development,'LASSO',a)[0][-1].coef_ for a in path_alphas])
selected_lasso = fit_forecast(development,'LASSO',depth['alpha'])
lasso_coefficients = selected_lasso[0][-1].coef_
assert np.count_nonzero(abs(lasso_coefficients)>1e-8) == depth['retained']
# One standardized predictor: exact soft-threshold solution.
z = np.array([-1.,-1.,1.,1.]); centered_y = 2*z
soft_coefficients = []
for alpha in [0.,.5,1.,2.,3.]:
    covariance = np.mean(z*centered_y)
    soft_coefficients.append(np.sign(covariance)*max(abs(covariance)-alpha,0))
assert soft_coefficients == [2.,1.5,1.,0.,0.]
# Verify the full Gaussian criteria and the Bernoulli illustration.
for row in depth['criteria']:
    assert np.isclose(row['aic'],row['negative2log']+2*row['parameters'])
    assert np.isclose(row['bic'],row['negative2log']+row['parameters']*np.log(1650))
bernoulli_likelihood = [p**3*(1-p)**2 for p in [.2,.4,.6,.8]]
assert [.2,.4,.6,.8][np.argmax(bernoulli_likelihood)] == .6
'''

DETAIL_TITLES = [
 'Likelihood compares parameter choices using the observed outcomes',
 'Three successes in five trials put the likelihood maximum at 0.6',
 'Gaussian maximum likelihood gives the OLS mean coefficients',
 'Deviance compares the fitted likelihood with a saturated reference',
 'Full information criteria count the variance parameter as well',
 'Expected test error averages over training samples and new outcomes',
 'The absolute-value penalty creates a zero-coefficient region',
 'Pooled RMSE weights squared fold errors by their sample sizes',
 'Smearing estimates an original-scale mean from training residuals',
 'Each validation window fits its own preparation rules',
]
CODE_TITLES = [
 'Construct dated inputs and fit the first validation fold',
 'Pool losses and verify the frozen forecast and clean feature basis',
 'Learn missing-input replacement and scaling from training rows',
 'Retransform log predictions and construct development coefficient paths',
 'Check the selected terms and calculate exact soft-threshold coefficients',
 'Verify the Gaussian criteria and Bernoulli likelihood example',
]

@lru_cache(maxsize=1)
def evidence():
    import retail_case
    ns=dict(retail_case.__dict__)
    exec(compile(CALCULATIONS,'lesson6-shared-calculations','exec'),ns)
    return ns

def loss_picture():
    x=np.linspace(-3,3,121)
    return graph('The loss function determines which misses are expensive',x,np.zeros(len(x)),
      'Error = observed − predicted','Loss (illustrative units)',show_points=False,
      lines=[(x,abs(x),'#276451',False),(x,x*x,'#3259a2',False),(x,np.where(x>0,2*x,-x),'#ad5a20',True)],
      desc='Green: absolute error. Blue: squared error. Orange dashed: twice the cost per point of underprediction. Positive errors mean the forecast was too low.')

def split_picture():
    body=text(30,25,'Ordinary 3-fold validation: exchangeable rows',17)
    for row in range(3):
        for col in range(3):
            x=30+col*218;y=44+row*30
            body+=f'<rect x="{x}" y="{y}" width="208" height="24" rx="4" fill="'+('#e6bd88' if row==col else '#cce0d5')+'"/>'
            body+=text(x+104,y+17,'Validate' if row==col else 'Train',13,'middle')
    body+=text(30,166,'Forecasting: train before each validation window',17)
    for j,(train,valid) in enumerate([('3–7','8–9'),('3–9','10–11'),('3–11','12–13')]):
        y=185+31*j
        body+=f'<rect x="30" y="{y}" width="295" height="25" rx="4" fill="#cce0d5"/>'
        body+=f'<rect x="338" y="{y}" width="180" height="25" rx="4" fill="#e6bd88"/>'
        body+=text(177,y+18,'Train: target weeks '+train,14,'middle')+text(428,y+18,'Validate: '+valid,14,'middle')
    body+='<rect x="540" y="185" width="150" height="87" rx="5" fill="#dfe7f3"/>'
    body+=text(615,215,'Final: weeks',14,'middle')+text(615,241,'14–16',18,'middle')
    body+=text(360,315,'Select → refit weeks 3–13 → final evaluation → later monitoring',14,'middle')
    return figure('Validation must reproduce the information available at prediction time',body,'Top: each independent-observation fold is held out once. Bottom: expanding time windows for this course; the final period is excluded from selection. Boxes indicate roles, not duration.')

def complexity_picture(d):
    scores=d['result']['scores']; choices=[scores[i] for i in [0,1,2]]
    a=np.array([x['training_rmse'] for x in choices]);b=np.array([x['rmse'] for x in choices])
    body=text(45,24,'RMSE (percentage points)',15)
    lo=2.65;hi=3.85;sy=lambda y:260-(y-lo)/(hi-lo)*205
    for tick in [2.7,3.,3.3,3.6,3.8]:
        yy=sy(tick);body+=f'<path d="M65 {yy} H670" stroke="#dce4da"/>'+text(57,yy+4,tick,12,'end')
    for vals,col,dash in [(a,'#276451',''),(b,'#ad5a20',' stroke-dasharray="6 4"')]:
        points=' '.join(f'{110+j*250},{sy(v)}' for j,v in enumerate(vals))
        body+=f'<polyline points="{points}" fill="none" stroke="{col}" stroke-width="3"{dash}/>'
        for j,v in enumerate(vals):body+=f'<circle cx="{110+j*250}" cy="{sy(v)}" r="5" fill="{col}"/>'
    for j,label in enumerate(['Mean: 1','Additive: 6','Quadratic: 19']):body+=text(110+j*250,288,label,14,'middle')
    body+=text(360,320,'Model: mean-equation parameters, including intercept',14,'middle')
    return figure('The quadratic fit improves training loss but worsens validation loss',body,'Green solid: pooled fitting errors across the three training windows. Orange dashed: pooled later-window errors. Both series use original rate units; model labels are categorical, not equally spaced parameter counts.')

def tuning_picture(d):
    rows=d['depth']['tuning'];x=np.log10([v['alpha'] for v in rows]);y=np.array([v['rmse'] for v in rows])
    return graph('Validation selects alpha 0.01 before the final period',x,y,'log₁₀(alpha): −3=.001, −2=.01, −1=.1, 0=1','Validation RMSE (points)',
      lines=[(x,y,'#276451',False)],labels=[(-2,y[1],'Selected')],desc='Each point pools 900 predictions from the same three forward validation windows. Candidate penalties were .001, .01, .1, and 1.')

def paths_picture(d):
    x=np.log10(d['path_alphas']);coeff=d['path_coefs']; names=d['forecast_feature_names']()
    top=np.argsort(abs(d['lasso_coefficients']))[-3:][::-1];cols=['#276451','#3259a2','#ad5a20']
    body='';sx=lambda v:65+(v+3)/4*590;sy=lambda v:250-(v+1.2)/3.4*165
    for v in [-1,0,1]:body+=f'<path d="M65 {sy(v)} H655" stroke="#dce4da"/>'+text(56,sy(v)+4,v,12,'end')
    for j in range(coeff.shape[1]):
        c=cols[list(top).index(j)] if j in top else '#b8c6be';width=3 if j in top else 1
        body+=f'<polyline points="'+ ' '.join(f'{sx(a):.2f},{sy(b):.2f}' for a,b in zip(x,coeff[:,j]))+f'" fill="none" stroke="{c}" stroke-width="{width}"/>'
    for i,j in enumerate(top):
        body+=f'<path d="M65 {18+19*i} H85" stroke="{cols[i]}" stroke-width="3"/>'+text(95,22+19*i,names[j],13)
    for v in [-3,-2,-1,0,1]:body+=text(sx(v),278,v,12,'middle')
    body+=text(360,311,'log₁₀(alpha); coefficient units: rate points per standardized feature',13,'middle')
    return figure('A stronger penalty can remove terms from the forecasting equation',body,'Paths fit weeks 3–13. The three largest selected coefficients are highlighted; other paths are gray. Paths illustrate shrinkage, while earlier validation chooses alpha. Correlated-feature paths need not shrink monotonically.')

def coefficients_picture(d):
    terms=d['depth']['terms'][:6];maxv=max(abs(t['coefficient']) for t in terms);body=''
    short={'lead_days urban':'Lead × urban','lead_days':'Lead days','promotion_plan':'Promotion planned','lag_rate urban':'Lag rate × urban','demand_forecast':'Demand forecast','lag_rate lead_days':'Lag rate × lead'}
    for i,t in enumerate(terms):
        y=37+43*i;v=t['coefficient'];length=abs(v)/maxv*190;x=410-length if v<0 else 410
        body+=text(225,y+5,short.get(t['feature'],t['feature']),14,'end')
        body+=f'<rect x="{x:.2f}" y="{y-10}" width="{length:.2f}" height="20" fill="'+('#ad5a20' if v<0 else '#276451')+'"/>'
        body+=text(625,y+5,f'{v:+.3f}',13)
    body+='<path d="M410 15 V280" stroke="#72847a"/>'+text(360,320,'Rate-point contribution per one training-standard-deviation change',13,'middle')
    return figure('Ten of eighteen constructed features remain in the selected LASSO',body,'Six largest absolute coefficients at alpha .01, fitted to development rows. Each constructed feature is standardized separately. These predictive coefficients are not intervention effects.')

def restore(c):
    from retail_ui import section,table,formula,p,step_link
    from curriculum_content import teach,bullets
    from slide_titles import Tree,visual_frames
    d=evidence();r=d['result'];dep=d['depth'];fmt=lambda v:f'{v:.3f}'
    c['sections']=[];c['authored_sections']=True
    c['headlines']={k:v for k,v in c['headlines'].items() if k in {'main','decision-brief','memo','big-picture'}}
    c['brief']='Operations needs a short list of stores to review before next week starts. Which forecasting procedure should the team trust? We will define the prediction loss, use later development weeks to compare complete procedures, and evaluate the selected rule on the final period.'
    c['presentation_points']={'memo':[f"Select {r['selected']} using rolling validation",f"Final RMSE: {r['rmse']:.3f} points; mean benchmark: {r['baseline_rmse']:.3f}",'Use the ranking to allocate review capacity'],
      'question':['A richer model lowers training error but raises validation error. Which should we deploy?'],
      'answer':['Select by the predeclared validation loss','Refit the chosen procedure on development rows','Use final outcomes to evaluate the frozen choice'],
      'truth':['New weekly variation remains after using timely inputs','The generator’s hidden quantities are excluded from model features']}
    c['headlines']['memo']=['Validation favors the additive forecast for this operating task','A better training fit does not justify worse validation performance']
    def block(title,visual,*notes):
        if '<svg' in visual:
            # Preserve the full accessible description; keep the projected caption short.
            captions={
              'The loss function determines which misses are expensive':'Green: absolute. Blue: squared. Orange dashed: asymmetric loss.',
              'Validation must reproduce the information available at prediction time':'Green: training. Orange: validation. Blue: final evaluation. Boxes show roles, not duration.',
              'The quadratic fit improves training loss but worsens validation loss':'Green solid: fitting RMSE. Orange dashed: later-window RMSE. Each label names a candidate model.',
              'Validation selects alpha 0.01 before the final period':'The same 900 held-out rows score each candidate penalty; alpha .01 wins.',
              'A stronger penalty can remove terms from the forecasting equation':'Colored: three largest selected terms. Gray: other terms. Vertical axis: standardized coefficients.',
              'Ten of eighteen constructed features remain in the selected LASSO':'Six largest absolute coefficients; alpha .01; each constructed feature is standardized separately.',
              'Final observed rates versus frozen forecasts':'450 final store-weeks. Above the diagonal: more stockouts than forecast.',
            }
            name=re.search(r'<title>(.*?)</title>',visual).group(1)
            visual=re.sub(r'<figcaption>.*?</figcaption>','<figcaption>'+captions[name]+'</figcaption>',visual,flags=re.S)
            visual=re.sub(r'font-size="(\d+)"',lambda m:m.group(0)+' style="font-size:'+str(max(16,int(m.group(1))+2))+'px"',visual)
        return teach(title,visual,list(notes))
    def put(key,title,body,phase='Worked application'):
        c['sections'].append(dict(**section(key,title,body),phase=phase))
        c['headlines'][key]=[t for t,_ in visual_frames(Tree(body).root,title)]
    put('prediction-task','Define what a useful forecast must predict',
      block('A prediction task specifies the target, decision time, and loss',bullets('Target: an outcome not yet available','Inputs: information available when the decision is made','Loss: the cost assigned to each prediction miss','Evaluation: predictions for rows excluded from fitting'),
        'A labelled training row has both predictors X and an observed outcome Y. A live scoring row has its available predictors but awaits the outcome. Regression predicts a numerical outcome such as a rate; classification predicts a category or its probability. The forecast horizon and intended users determine what counts as an available input. This lesson predicts one week ahead for existing stores.')+
      block('Squared loss gives large misses more weight than absolute loss',loss_picture(),
        'Write the error as observed minus predicted. Absolute loss grows proportionally with its size; squared loss grows faster. The orange example charges twice as much per point when the forecast is too low. Loss need not be symmetric. A choice of loss expresses the operating problem before it determines which model wins. Under squared loss the optimal point forecast is the conditional mean; under absolute loss it is a conditional median.')+
      block('One large miss changes RMSE more than it changes MAE',table(['Errors (points)','MAE','MSE','RMSE'],[['−1, +1, +4','2.000','6.000','2.449'],['−2, +2, +2','2.000','4.000','2.000']], 'MAE = mean absolute error; RMSE = square root of mean squared error'),
        'For the first row, absolute errors total 6 and squared errors total 18. Divide each by three, then take the square root only for RMSE. Both rows have the same MAE, but the four-point miss raises the first RMSE. MSE has squared outcome units; MAE and RMSE have the original units. Our common model-selection score is RMSE in percentage points.')+
      block('Expected prediction error combines bias, variation across fits, and new noise',formula('Expected squared error = bias² + prediction variance + noise variance'),
        'At a fixed input x, bias is the difference between the average prediction across training samples and the true conditional mean. Prediction variance describes how fitted predictions change across those samples. Noise is the new outcome’s variation around its conditional mean. A more flexible model may reduce bias while increasing variance; it cannot remove irreducible outcome noise. This expectation is not an exact decomposition of each observed residual.')+
      block('Overfitting learns sample-specific variation that does not improve new predictions',table(['Model behavior','Fitting sample','New outcomes'],[['Too restrictive','Misses persistent structure','Can retain substantial bias'],['More flexible','Can reduce fitting loss','May improve or worsen loss'],['Overfitted','Captures sample-specific variation','Fails to carry that gain forward']], 'Choose useful flexibility by performance outside the fitting rows'),
        'Adding regressors to a nested OLS model cannot increase its minimized training sum of squared errors. That algebra does not apply to new rows. Overfitting occurs when fitting sample-specific variation harms generalization; underfitting misses useful structure. Validation measures the consequence for the intended prediction task rather than choosing complexity from training fit alone.'),phase='General theory')
    put('theory-validation','Separate fitting, selection, and evaluation',
      block('Validation must follow the information pattern of the future decision',split_picture(),
        'Ordinary k-fold validation fits k models, leaving a different part out each time. It is useful when the observations can be treated as exchangeable for the task. Forecasting asks a different question: train on earlier weeks and predict later ones. The same stores can appear in both periods because the intended use is future outcomes at existing stores. Predicting entirely new stores would also require holding stores out.')+
      block('The fitted procedure includes every transformation learned from the data',bullets('Choose target, features, candidates, and score','Fit preparation and model inside each training window','Use validation outcomes to choose the procedure','Refit on development data before final evaluation'),
        'Medians, scaling parameters, category rules learned from observed data, coefficients, and any target retransformation all belong to the fitted procedure. Reusing preparation learned from validation rows gives those rows a role in fitting. The final period measures the selected procedure. After evaluation, changes to the procedure call for a new evaluation period. The appendix links the pipeline guidance and the exact implementation.')+
      block('Pool squared errors before taking the root of a validation score',formula('Pooled RMSE = √[Σ n_f × RMSE_f² / Σ n_f]'),
        'A fold with more validation rows contributes more squared errors. Averaging the fold RMSEs does not produce the pooled RMSE, even when fold sizes are equal. For equal sizes, square the fold scores, average those squares, then take the square root. Choosing alpha from these same development folds is model selection; the final period supplies the subsequent evaluation of that choice.')+
      block('Information criteria trade likelihood fit against parameter count',formula('AIC = −2 log L + 2k; BIC = −2 log L + k log n'),
        'For a common response and common rows, better likelihood fit lowers the first term and extra parameters raise the penalty. Lower is better within that comparison. Count identifiable fitted parameters, including residual variance for the full Gaussian criteria used here. BIC penalizes an extra parameter more than AIC when log n exceeds two. These training criteria and later-period RMSE answer different questions; the worked example reports both.'),phase='General theory')
    put('theory-shrinkage','Control flexibility with a coefficient penalty',
      block('LASSO trades squared fitting loss against the absolute size of coefficients',formula('Minimize RSS/(2n) + α Σ|b_j|; leave the intercept unpenalized'),
        'With alpha zero the objective reduces to least squares. Increasing alpha makes a coefficient earn its place by improving fit enough to offset its penalty. The absolute-value penalty has a corner at zero, allowing some coefficients to be exactly zero. Standardizing features makes their penalty comparable across measurement units. Alpha must be chosen by validation rather than by the final outcomes.')+
      block('The penalty creates an exact zero when the fitted signal is small enough',table(['α','Unpenalized slope','LASSO slope'],[[0,2,2],[.5,2,1.5],[1,2,1],[2,2,0],[3,2,0]], 'Illustration: centered y=2z, mean(z²)=1; b=max(2−α,0)'),
        'For this one-predictor example, the objective differs from (b−2)²/2 + alpha|b| only by a constant. On the positive side its minimum moves from 2 toward zero as alpha rises. Once alpha reaches 2, zero minimizes it. The appendix shows the positive and negative cases. With correlated features, one coefficient can rise while another falls, so a whole coefficient path need not be monotone.')+
      block('Standardization puts each constructed feature on its own training scale',formula('z_j = (x_j − training mean_j) / training SD_j'),
        'First construct the declared powers and interactions, then standardize each resulting column using the training rows. A coefficient then measures rate points per one training-standard-deviation change in that constructed feature, holding the other constructed columns fixed. A product is standardized as a product column; it is not generally the product of standardized inputs. The intercept describes the prediction at all standardized inputs equal to zero.')+
      block('Feature design and missing-input rules are part of the model',bullets('Use main terms, powers, and interactions that fit the task','Remove exact duplicates such as a binary variable’s square','Record unavailable inputs with a missingness indicator','Fit replacement values from training rows'),
        'For a binary variable D, D²=D, so adding its square adds no independent information. For categories, retain a documented reference level and a rule for new categories. A missing response cannot contribute supervised training loss. A missing predictor can be handled by a trained imputation rule plus an indicator, so the same procedure can score future rows. We will work that preparation step on a small copy of the retail records.'),phase='General theory')
    put('theory-scale','Score forecasts on the scale of the decision',
      block('Exponentiating a fitted log value does not recover an arithmetic mean',formula('For log(1+Y): predicted Y = exp(fitted log value) × smearing factor − 1'),
        'Exponentiation is nonlinear. A global smearing factor averages exp(residual) over training rows and estimates a common retransformation correction. Here log1p handles zero rates without discarding them. Conditional changes in log-error spread can require a richer correction; compare the complete procedure on held-out rows. For the simpler log(Y) illustration, residuals −0.2 and +0.2 multiply a naive forecast of 10 by 1.0201, giving 10.201.')+
      block('Compare transformed-target procedures using the same original-scale loss',bullets('Use identical validation rows','Learn retransformation inside each training fold','Return predictions to rate units','Compare the resulting RMSE in percentage points'),
        'A smaller log-scale fitting error cannot be compared directly with a rate-scale fitting error. Retransform first and evaluate the forecast that operations would receive. Likewise, a high training R² does not establish a low future prediction loss. The candidate comparison below includes both level and log1p procedures under one chronological validation design.'),phase='General theory')
    row=d['final_test'].iloc[0]
    scaler=d['frozen'][0][0]; estimator=d['frozen'][0][-1]
    raw_slopes=estimator.coef_/scaler.scale_
    raw_intercept=estimator.intercept_-np.sum(estimator.coef_*scaler.mean_/scaler.scale_)
    contributions=[('Intercept',raw_intercept)]+[(name,float(row[name]*coef)) for name,coef in zip(d['features'],raw_slopes)]
    assert np.isclose(sum(value for _,value in contributions),d['final_predictions'][0])
    put('read-data','Place the retail inputs on the decision clock',
      block('Five timely inputs predict the next store-week stockout rate',table(['Input','Available before target week'],[['lag_rate','Previous week’s measured rate'],['lead_days, urban','Store attributes'],['demand_forecast','Target-week planning forecast'],['promotion_plan','Already scheduled promotion']], '150 stores; target weeks 3–16; no alert use in this period'),
        'The outcome is 100 times unavailable product-days divided by 140 scheduled product-days. Each row predicts a target week using the previous week’s rate and plans known beforehand. The realized target-week demand, outcome, and eventual alert status are excluded. This is a weekly forecast for the same stores, not a prediction for a new region.')+
      block('A complete scoring row contains inputs before it contains its outcome',table(['Before week 14: '+row.store_id,'Value'],[['Previous-week rate',f'{row.lag_rate:.3f}%'],['Delivery / urban',f'{int(row.lead_days)} days / {int(row.urban)}'],['Demand forecast',f'{row.demand_forecast:.3f}'],['Promotion planned',int(row.promotion_plan)],['Frozen-model forecast',f'{d["final_predictions"][0]:.3f}%']], 'Model fitted on target weeks 3–13; no week-14 outcome used in this forecast'),
        f'The forecast is {d["final_predictions"][0]:.3f}%. At the end of the target week the observed rate becomes available, allowing the error to be recorded. During weeks 14–16 the fitted coefficients remain fixed while the lagged input updates each week. A later realized lag is legitimate information for the next one-week-ahead forecast.')+
      block('The forecast adds an intercept and five input contributions',table(['Original-unit term','Contribution to forecast'],[[name,f'{value:+.5f}'] for name,value in contributions],f'Sum of unrounded contributions = {d["final_predictions"][0]:.5f}% for S001, week 14'),
        'Convert the standardized linear coefficients back to original units: divide each slope by its training standard deviation, and subtract the mean adjustments from the intercept. Multiply those slopes by the five inputs in the preceding row. Urban is zero for this store, so its contribution is zero. Summing the intercept and contributions reconstructs the forecast; rounding intermediate entries can change the last displayed digit.'))
    scores=r['scores'][1]['fold_rmse'];first=d['validation'].head(5)
    put('validation-design','Follow one fold from rows to score',
      block('Three expanding windows produce 900 comparable validation predictions',table(['Fold','Training weeks / rows','Validation weeks / rows','Linear RMSE'],[[1,'3–7 / 750','8–9 / 300',fmt(scores[0])],[2,'3–9 / 1,050','10–11 / 300',fmt(scores[1])],[3,'3–11 / 1,350','12–13 / 300',fmt(scores[2])]], 'Each held-out outcome appears once; final weeks 14–16 are excluded'),
        'For each candidate, fit preparation and coefficients again at the start of each fold. Training windows expand, but validation windows do not overlap. The final refit uses all 1,650 development rows in weeks 3–13. The later final evaluation has 450 rows. These fixed historical splits reconstruct the selection process for the teaching exercise.')+
      block('Individual squared misses build the first fold’s loss',table(['Store','Week','Observed','Predicted','Squared error'],[[a.store_id,int(a.week),fmt(a.stockout_rate),fmt(d['first_predictions'][i]),fmt(d['first_errors'][i]**2)] for i,a in enumerate(first.itertuples())], 'First five of 300 predictions from the additive model fitted on weeks 3–7'),
        f'Compute error as observed minus predicted for each row, square it, and sum across all 300 validation rows. The sum is {np.sum(d["first_errors"]**2):.3f}; dividing by 300 gives {np.mean(d["first_errors"]**2):.3f}. Its square root is {scores[0]:.3f} percentage points. The five displayed rows illustrate the arithmetic; the fold score uses all 300.')+
      block('Pooling the three fold losses gives a 2.780-point validation score',formula(f'√[({scores[0]:.5f}² + {scores[1]:.5f}² + {scores[2]:.5f}²)/3] = {r["scores"][1]["rmse"]:.5f}'),
        'Each fold has 300 validation rows, so equal weights are appropriate for their squared scores. The arithmetic mean of the three roots is a different statistic. Store both the row errors and fold scores so the pooled result can be reconstructed and unusually difficult periods can be investigated.'))
    q=d['quality_valid'].query('store_id=="S001"').iloc[0]
    put('preprocessing','Rehearse a missing forecast before using the procedure',
      block('A training median fills a missing input while an indicator records its absence',table(['Quality exercise','Demand input','Missing flag','Filled value'],[['S001, week 8','Unavailable',1,fmt(q.demand_filled)],['Training rows','10 withheld out of 750','Calculated before fill',f'Median {d["median"]:.3f}']], 'Labelled copy: withhold S001/S002 training forecasts and S001 validation forecasts'),
        'The reconciled analysis inputs are complete. This separate exercise deliberately hides selected demand forecasts to practise the deployment rule; it does not alter the main model comparison. Calculate the median from the remaining training values, create an indicator before filling, then apply the saved median to missing validation values. An unchanged observed value retains a zero indicator.')+
      block('The validation row uses the training mean and standard deviation unchanged',formula(f'z = ({q.demand_filled:.3f} − {d["scale_mean"]:.3f}) / {d["scale_sd"]:.3f} = {q.demand_z:.3f}'),
        'The mean and population-standard-deviation convention here match StandardScaler. Both are calculated after training-fold imputation. Apply those same values to validation rows; do not re-standardize the validation set on its own mean. If evaluating the missing-input procedure as a new candidate, refit this entire preparation inside every fold and include the missingness flag as an input.'))
    criteria=dep['criteria']
    put('feature-design','Make the flexible model’s complexity explicit',
      block('The quadratic design has eighteen distinct slope features',table(['Feature group','Count'],[['Five original predictors',5],['Squares of three continuous predictors',3],['Pairwise interactions among five predictors',10],['Total slope features',18],['Including intercept: mean-equation rank',19]], 'Exclude urban² and promotion_plan² because each equals its original binary input'),
        'The three continuous variables are previous rate, delivery time, and the demand forecast. Include their squares and all ten distinct pairwise products. The resulting 19-column design, including the intercept, has rank 19 in development data. The additive model has five slopes and an intercept. LASSO uses this same clean 18-feature expansion before scaling.')+
      block('AIC favors the quadratic fit while BIC favors the additive fit',table(['Mean model','Mean parameters','Total k','AIC','BIC'],[['Additive',6,7,fmt(criteria[0]['aic']),fmt(criteria[0]['bic'])],['Quadratic',19,20,fmt(criteria[1]['aic']),fmt(criteria[1]['bic'])]], 'Full Gaussian criteria on identical 1,650 development rows; k includes residual variance'),
        'The quadratic model’s better likelihood offsets AIC’s smaller penalty, but not BIC’s larger penalty. These are illustrative Gaussian working-model criteria: repeated weekly records motivate chronological validation as the operating performance check. The appendix derives the full likelihood constants and counts. We select the forecasting procedure using the predeclared rolling RMSE.'))
    put('calculate','Compare complete forecasting procedures on the same weeks',
      block('The additive regression has the lowest pooled validation RMSE',table(['Procedure','Validation RMSE','Fitting RMSE'],[[x['model'],fmt(x['rmse']),fmt(x['training_rmse'])] for x in r['scores']], 'Same 900 validation rows; fitting losses pool each fold’s own training rows'),
        'The mean-rate rule is the baseline. Additive regression uses the five timely inputs. Quadratic regression uses the clean expansion. Log-linear fits log(1+rate) and applies its training smearing factor. LASSO uses the expansion with alpha selected from .001, .01, .1, and 1. The additive rule wins under the stated criterion; the small differences among the richer candidates do not demonstrate a stable ranking in all future periods.')+
      block('The richer equation improves fitting error without improving later forecasts',complexity_picture(d),
        'The quadratic model lowers fitting loss because it contains the additive model’s terms. Its validation loss rises slightly. This illustrates why an improving training fit is insufficient for selection. The graph uses the actual course results, not a forced textbook U-shape. Fitting rows recur in expanding training windows; their pooled error is a description of those fits, while each validation outcome is scored once.')+
      block('The log procedure is judged after returning predictions to rate units',table(['First validation fold','Value'],[['Training smearing factor',f'{d["log_fit"][2]:.5f}'],['First naive expm1 forecast',fmt(d['log_naive'][0])],['First adjusted rate forecast',fmt(d['log_adjusted'][0])],['Pooled log-procedure RMSE',fmt(r['scores'][3]['rmse'])],['Pooled level-procedure RMSE',fmt(r['scores'][1]['rmse'])]], 'Adjusted = (naive + 1) × training smearing factor − 1'),
        'The two candidates predict the same original rate on the same held-out rows. The level procedure wins narrowly here. A log transformation can still be useful in another setting, but its value is assessed through the actual decision loss after retransformation, not by comparing incomparable fitting scales.'))
    put('lasso','Trace the penalty choice into the retained equation',
      block('Rolling validation selects a LASSO penalty of 0.01',tuning_picture(d),
        f'The four candidate penalties produce pooled scores of '+', '.join(f'{x["alpha"]:g}: {x["rmse"]:.4f}' for x in dep['tuning'])+f' points. Alpha {dep["alpha"]:g} minimizes this set. Standardization is refitted inside every fold. The curve reports the selection metric, not the final-period score.')+
      block('Larger penalties shrink the model toward an intercept-only forecast',paths_picture(d),
        'Follow a colored path from left to right as alpha increases. The vertical position is the coefficient of a separately standardized constructed feature. A path reaching zero removes that term at that penalty. All paths here use development rows for illustration. They do not provide an additional reason to change the penalty selected by validation.')+
      block('The selected LASSO retains ten of eighteen candidate features',coefficients_picture(d),
        'The selected LASSO has ten nonzero slopes under a tolerance of 1e−8. The chart shows its six largest absolute coefficients; the appendix’s saved results list all retained terms. Products and main effects should be read as components of one prediction equation. Correlated inputs can exchange signal, so selection is not a claim that these are the unique important variables.'))
    final=d['final_test'];errors=final.stockout_rate.to_numpy()-d['final_predictions'];weekly=[]
    for week in [14,15,16]:
        e=errors[final.week.to_numpy()==week];weekly.append([week,len(e),fmt(np.sqrt(np.mean(e**2))),fmt(np.mean(e))])
    put('interpret','Evaluate the frozen choice on later outcomes',
      block('The final forecast improves on the mean-rate benchmark',table(['Final weeks 14–16','RMSE (points)','MAE (points)'],[['Frozen additive model',fmt(r['rmse']),fmt(r['mae'])],['Development mean forecast',fmt(r['baseline_rmse']),fmt(np.mean(abs(final.stockout_rate-r['baseline'])))]], '450 one-week-ahead predictions; model fitted once on weeks 3–13'),
        'The selected additive procedure scores 2.963 points against 3.880 for the mean benchmark. This evaluates the selection made using development data. It does not establish a treatment effect or the financial value of acting on a forecast. The same dated record should retain model version, inputs, prediction, later outcome, and action.')+
      block('Points above the diagonal reveal weeks when the model underpredicted stockouts',graph('Final observed rates versus frozen forecasts',d['final_predictions'],final.stockout_rate.to_numpy(),'Predicted rate (%)','Observed rate (%)',diagonal=True,desc='Each point is one of 450 final store-weeks. The dashed line is observed=predicted. Observed values are vertical throughout this lesson.'),
        'Read vertical distance from the diagonal as observed minus predicted. Points above it have more stockouts than forecast; points below have fewer. Inspect where misses concentrate across the forecast range and return to the corresponding operating records. Prediction intervals and their targets were developed in Lesson 5; this plot evaluates point predictions.')+
      block('Track both error size and average underprediction across weeks',table(['Target week','Rows','RMSE','Mean error'],weekly,'Mean error = observed − predicted; positive means average underprediction'),
        'Save both overall accuracy and error by period. Before extending to alert use, assign the operations analyst a weekly review: compare the newest errors with this evaluation period, inspect missing inputs and changes in promotion or delivery, and investigate a sustained increase. The alert intervention changes operating conditions, so collect a new evaluation period for that policy setting.'))
    put('act','Use forecasts to allocate a finite review capacity',
      block('Rank stores by forecasts made before the operating week starts',table(['Week 16 review order','Forecast (%)'],[[x['store_id'],fmt(x['prediction'])] for x in r['watchlist']], 'Illustration: review the five highest forecasts at the end of week 15'),
        'The list uses predictions, not observed week-16 outcomes. A capacity of five is an explicit operating choice: managers review products at those stores and record the time, response, and benefit. Changing the number reviewed changes workload and the possible value of the process. The model supplies a ranking; the team supplies the action and capacity rule.')+
      block('A useful forecast leads to an action whose effect can be tested',bullets('Version and log the weekly prediction procedure','Assign review capacity and record the response','Monitor prediction loss and operating changes','Use Lesson 7 to evaluate whether alerts improve outcomes'),
        'Reliable forecasting answers where problems are likely to arise. Whether replenishment alerts reduce those problems is a separate question about the response. The next lesson tests that response using random assignment. Carry the forecast contract and monitoring record forward so prediction and intervention evaluation remain connected.'))
    c['memo']=f"Use {r['selected']} selected by common rolling validation. Its final RMSE is {r['rmse']:.3f} points versus {r['baseline_rmse']:.3f} for the mean-rate benchmark. Freeze the weekly input contract, allocate review capacity, and evaluate whether the subsequent alert action improves outcomes."
    c['question']='The quadratic model lowers training RMSE but raises validation RMSE. Which rule should operations choose under the stated criterion?'
    c['answer']='Choose the additive model by its lower rolling-validation RMSE, refit it on development rows, and evaluate that frozen procedure on the final period. Extra terms earning a better training fit is not sufficient evidence of better forecasts.'
    c['code']=CALCULATIONS
    c['technical']=[
      'Use 150 stores and target weeks 3–16. Five inputs are available before each target week. Development ends at week 13; validation windows 8–9, 10–11, and 12–13 follow training windows ending at 7, 9, and 11. Final target weeks are 14–16. All candidates use the same held-out rows.',
      'The shared source defines forecast_basis, fit_forecast, predict_forecast, and prediction_analysis. Follow one fold below, then verify the pooled score, clean design rank, missing-input exercise, log retransformation, coefficient paths, and likelihood arithmetic. These calculations also generate the lesson figures.',
      'Final RMSE is a point-performance summary of a frozen forecasting procedure. Repeated observations concern the same stores over time; the Gaussian information criteria are a working-model illustration. No independent-row confidence interval for the difference in candidate scores is claimed. Use time-respecting evaluation for this operating task.',
      'Change one feature group or penalty candidate using only development data. Record the selection rule before scoring the final period. For an empirical claim after exploring these published outcomes, obtain a new later evaluation period. The labelled missing-input exercise can be developed into a complete fold-local pipeline.'
    ]
    detail=[
      (formula('L(θ;y) = probability or density of the observed y at parameter θ'),
       'The observations are fixed while the parameter varies. This is not a posterior probability for the parameter. For independent binary observations, the product of Bernoulli probabilities gives the likelihood; for continuous outcomes use their density. Logistic regression supplies probabilities through a link function and maximizes the corresponding Bernoulli likelihood.'),
      (table(['p','Likelihood p³(1−p)²'],[[v,f'{v**3*(1-v)**2:.5f}'] for v in [.2,.4,.6,.8]],'Observed sequence: 1, 0, 1, 1, 0'),
       'The log likelihood is 3 log p + 2 log(1−p). Its derivative 3/p−2/(1−p) vanishes at p=3/5, and the second derivative is negative. For a count likelihood a binomial coefficient multiplies every candidate value by the same constant, so the maximizing p is unchanged.'),
      (formula('ℓ(b,σ²) = −n log(2π)/2 − n log(σ²)/2 − RSS(b)/(2σ²)'),
       'With independent normal errors of a common variance, maximizing over b minimizes RSS and therefore gives OLS. The variance MLE is RSS/n. This is different from the degrees-of-freedom-adjusted variance used for classical coefficient inference. At the MLE, −2ℓ=n[log(2π)+1+log(RSS/n)].'),
      (formula('Deviance = 2[ℓ(saturated model) − ℓ(fitted model)]'),
       'A saturated reference fits each observed outcome as fully as its distribution permits. Deviance is not universally just minus twice the fitted log likelihood; the reference term matters. For Gaussian models with known variance it gives RSS/σ². Estimating a separate unrestricted variance in a saturated normal fit creates a boundary issue, so do not use that construction as a generic shortcut.'),
      (table(['Component','Additive','Quadratic'],[['−2 log likelihood',fmt(criteria[0]['negative2log']),fmt(criteria[1]['negative2log'])],['Mean parameters',6,19],['Variance parameters',1,1],['AIC penalty',14,40],['BIC penalty',fmt(7*np.log(1650)),fmt(20*np.log(1650))]],'Same response, same n=1,650, identifiable columns'),
       'Adding the displayed penalty to −2 log likelihood produces the main-lesson table. The quadratic basis has 18 slopes plus the intercept; adding variance gives k=20. In the previous redundant expansion, two binary squares duplicated existing columns. A nominal column count would overstate the identifiable mean dimension. Do not apply these ordinary parameter counts as a LASSO degrees-of-freedom formula.'),
      (formula('E[(Ynew−f̂D(x))² | x] = [E_D f̂D(x)−f(x)]² + Var_D[f̂D(x)] + σ²(x)'),
       'D indexes random training samples; f(x)=E[Y|x]. The new error has conditional mean zero and is independent of the fitted training procedure given x. Expand the square around the expected prediction; the cross terms have zero expectation. The variance term concerns variation between fitted predictions, not the raw outcome variance in one sample.'),
      (formula('For centered y,z with mean(z²)=1: b = sign(c) max(|c|−α,0), c=mean(zy)'),
       'The objective is b²/2−cb+alpha|b| plus a constant. For b>0 its derivative is b−c+alpha; for b<0 it is b−c−alpha. At zero the subgradient contains zero when |c|≤alpha. This produces the exact-zero region. With multiple correlated columns, coordinate descent repeats conditional versions of this update; coefficients need not follow independent straight paths.'),
      (formula('Σ errors² = Σ_f n_f RMSE_f²; pooled RMSE = √(Σ errors² / Σ_f n_f)'),
       'When each held-out row appears once, this is simply the row-level loss. If windows have unequal sizes, use their counts. The square root is monotone, so minimizing pooled RMSE is equivalent to minimizing pooled MSE. LassoCV’s built-in mean-fold-MSE rule is a different weighting rule when fold sizes differ; this lesson explicitly pools errors from its equal-sized chronological windows.'),
      (formula('S_train = mean[exp(log(1+y_train)−f̂(x_train))]; ŷ = exp(f̂(x))S_train−1'),
       'Fit the log model and estimate S using only the current training fold. A single S is a common-smearing working assumption; conditional residual-distribution changes can require a conditional correction. The comparison therefore scores the actual retransformed predictions against validation outcomes in rate units.'),
      (bullets('Fit training median; add missingness flag before filling','Construct the predefined nonredundant feature basis','Fit training means and scales','Fit coefficients and predict later rows'),
       'For the complete data, the main LASSO pipeline constructs deterministic features, then fits StandardScaler and Lasso anew in each window. The separate quality exercise demonstrates imputation explicitly. The shared executable source contains the full implementation.'),
    ]
    references='<p>References: <a href="https://scikit-learn.org/stable/common_pitfalls.html">preprocessing within validation</a>; <a href="https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html">LASSO objective and implementation</a>.</p>'
    c['appendix_extra']='<section id="prediction-details"><h2>Reconstruct the prediction method</h2>'+''.join(block(t,v,n) for t,(v,n) in zip(DETAIL_TITLES,detail))+references+'</section>'
    next(s for s in c['sections'] if s['id']=='calculate')['body']+=step_link(6,'calculation')
    return c
