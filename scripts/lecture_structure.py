"""Motivation -> general theory -> worked application -> synthesis.

Replace general exposition embedded in the case with the theory sequence.
Keep the worked records, results, code, exercises, and original topic anchors.
"""
from copy import deepcopy
from slide_titles import Tree,visual_frames
from slide_headlines import MAIN
from theory_content import TITLES,theory_sections
from retail_ui import p,formula
from curriculum_content import teach

# These explanations are taught in the general theory before the case begins.
# Numerically worked blocks remain in the application even when they reuse a formula.
MOVE = {
1:{
 'evidence':['What you should be able to do'],
 'coverage':['Population, sample, and reporting frame','The four Vs become operating requirements'],
 'structure':['Three structures, one continuing business','Measurement scales determine useful arithmetic','Choose a practical storage format','A tidy table has an explicit key'],
 'relationships':['Choose the relationship before choosing the command'],
 'workflow':['Preserve, profile, define, clean, validate, document','Use AI to accelerate work that can be checked'],
},
2:{'explore':['Explore before committing to one summary','Choose a display for the question'],
 'distributions':['Use the same scale for a fair comparison'],
 'association':['Conditional means answer a narrower question']},
3:{'sampling-variation':['A statistic changes when the sample changes','Why sample size helps precision'],
 'resampling':['Bootstrap the unit that was sampled'],
 'testing':['Treat testing as an error-and-cost decision','Match the test to the relationship between rows']},
4:{'from-bins':['Three increasingly detailed predictions','OLS chooses a line by squared vertical misses'],
 'functional-form':['Four forms make four different claims','A spline lets the slope change at a named point']},
5:{'controls':['Omitted-variable bias has two ingredients','Categories need a reference group','An interaction makes a slope depend on context']},
6:{'prediction-task':['Define the task before choosing an algorithm','Choose a loss that reflects the decision','Complexity changes both bias and variability'],
 'validation-design':['Preprocessing belongs inside the fitted procedure'],
 'lasso':['LASSO adds a cost for large coefficients','Close the loop after deployment']},
7:{'counterfactuals':['Every store has two potential policy outcomes','Different averages answer different spending questions','Observed outcomes follow assignment'],
 'experiment-design':['Keep the intervention and comparison stable','Controlled and natural experiments differ in who assigns'],
 'experiment-value':['An A/B comparison can also be written as regression']},
8:{'identification':['Conditional independence is the working comparison claim','Subclassification makes the comparison visible'],
 'graph-structures':['Follow a path before choosing a control','Use the backdoor criterion for the total-effect question'],
 'target-weights':['Use AI to draw an argument that people can inspect']},
9:{'ideal-experiment':['Separate internal from external validity']},
10:{'panel-design':['The standard design has two groups and two periods','Parallel trends defines the missing outcome path'],
 'did-regression':['Continuous exposure requires a defined dose']},
}

APPLICATION_ORDER = {
1:['read-data','evidence','coverage','structure','calculate','reshape','relationships','aggregation','interpret','workflow','act'],
2:['read-data','distributions','calculate','interpret','association','act'],
3:['read-data','sampling-variation','calculate','interpret','resampling','testing','act'],
4:['read-data','from-bins','calculate','interpret','fit','functional-form','act'],
5:['read-data','calculate','interpret','regression-uncertainty','controls','residual-review','act'],
6:['read-data','calculate','validation-design','interpret','lasso','act'],
7:['counterfactuals','read-data','experiment-design','calculate','interpret','experiment-value','act'],
8:['read-data','graph-structures','calculate','interpret','target-weights','act'],
9:['ideal-experiment','read-data','calculate','interpret','matching-options','act'],
10:['read-data','panel-design','calculate','interpret','did-regression','act'],
}

SCOPE = {
1:['Define observations, variables, keys, and measurement scales','Prepare and combine records reproducibly','Apply the workflow to the stockout baseline'],
2:['Describe centre, spread, shape, and conditional relationships','Choose summaries and displays for the question','Apply them to the distribution of store performance'],
3:['Distinguish parameters, estimates, and sampling distributions','Build intervals, tests, and resampling procedures','Apply inference to the shelf audit'],
4:['Define OLS, slopes, fitted values, and residuals','Evaluate fit and interpret alternative functional forms','Apply regression to delivery time and stockouts'],
5:['Interpret controls, indicators, and interactions','Distinguish coefficient and prediction uncertainty','Apply the model to comparable store profiles'],
6:['Define prediction targets and loss functions','Validate and regularize the complete procedure','Apply it to forecasting next week’s stockouts'],
7:['Define potential outcomes and average treatment effects','Use random assignment to identify a comparison','Apply the design to the alert pilot'],
8:['Use causal diagrams to justify adjustment','Read chains, forks, colliders, and target weights','Apply the argument to voluntary alert adoption'],
9:['Specify the target trial and adjustment assumptions','Estimate effects using regression and matching','Apply both methods to the same adoption cohort'],
10:['Define the two-by-two change comparison','Connect parallel trends, regression, and uncertainty','Apply DiD to the later rollout'],
}

MOTIVATION = {
1:['How much of the reported service problem is real?','A credible decision needs a well-defined measure'],
2:['Where should limited review effort go first?','An average alone cannot locate the problem'],
3:['Is a sample audit informative enough to justify action?','The estimate needs a measure of precision'],
4:['How does operating risk vary with delivery time?','We need a relationship we can describe and calculate'],
5:['How can we compare stores with different operating conditions?','We need to specify what is held fixed'],
6:['Which stores will need attention next week?','We need evidence about future prediction error'],
7:['Do alerts improve service enough to cover their cost?','We need the outcome under a credible alternative policy'],
8:['What can voluntary adoption tell us about effectiveness?','We need to understand why the groups differ'],
9:['How much would alerts help the intended population?','We need comparable outcomes for both policy options'],
10:['Did expansion improve service beyond the background trend?','We need a credible comparison of changes'],
}

OPENERS = {
1:'Measurement definitions determine what a dataset can tell us',
2:'Distributions show how outcomes vary across observations',
3:'Inference quantifies what a sample tells us about a population',
4:'Regression summarizes how expected outcomes vary with predictors',
5:'Multiple regression defines comparisons conditional on other variables',
6:'Prediction quality is measured on outcomes beyond the fitting sample',
7:'Causal effects compare outcomes under alternative interventions',
8:'Causal diagrams make the logic of adjustment explicit',
9:'Adjustment and matching construct comparisons for a defined population',
10:'Difference-in-differences uses comparison trends to estimate policy effects',
}

TRANSFER = {
1:('Good analysis starts with a reproducible measurement contract',
 ['Define the unit, variable, key, and exposure','Validate each transformation against that definition','Carry provenance and reporting coverage into the result'],
 'The transferable method is to turn a question into a measurement contract and a reproducible preparation workflow. It applies to transactions, staffing, customers, and repeated organizational records. Define what a row represents, preserve the denominator, and validate each reshape, join, and aggregation before interpreting a result.'),
2:('A distribution explains what an average leaves hidden',
 ['Read centre, spread, shape, and sample size together','Use comparable denominators for group summaries','Distinguish description, prediction, and causal explanation'],
 'The same descriptive tools apply to costs, processing times, customer demand, and service quality. A single average does not show where variation or extreme outcomes occur. Choose a distributional summary and a conditional comparison that answer the question, then use their definitions consistently when allocating attention.'),
3:('Inference connects a sample estimate with a decision about its population',
 ['State the parameter and independent sampling unit','Use intervals and tests matched to the design','Compare uncertainty with the effect that matters'],
 'The inference framework transfers to audits, surveys, and experimental measurements. Specify the population quantity, understand how the sample was drawn, and quantify the estimator’s sampling variation. The business interpretation then compares the estimate and interval with a meaningful threshold and the cost of getting the decision wrong.'),
4:('Regression summarizes a relationship through a stated functional form',
 ['Read coefficients in the units of the chosen model','Trace fitted values and residuals','Compare shape and fit on a common outcome scale'],
 'A regression is a specified way to summarize how an outcome varies with predictors. The same reasoning applies to cost, demand, and performance relationships. Define the variables, choose the functional form, interpret its slope correctly, and inspect the residuals before deciding what the fitted relationship can contribute.'),
5:('A coefficient becomes meaningful through its conditional comparison',
 ['State which inputs are held fixed','Interpret main and interaction terms together','Match the uncertainty interval to the prediction target'],
 'Multiple regression makes comparisons more specific. Its interpretation depends on the included variables, coding, reference values, and interactions. Use fully specified profiles to explain the model in any application, and distinguish uncertainty about a coefficient, a mean response, and a new individual outcome.'),
6:('A predictive model is a validated procedure from inputs to action',
 ['Define the forecast date, target, and loss','Fit and tune the entire pipeline within development data','Evaluate later outcomes and monitor deployment'],
 'Forecasting demand, cost, or service pressure uses the same sequence: define the prediction task, construct information available at the decision time, select a procedure using validation, and evaluate it on genuinely held-out observations. The value comes from reliable future performance and the action it supports.'),
7:('Causal evaluation requires a counterfactual design before a cost calculation',
 ['Define the intervention and target effect','Align analysis with the assignment procedure','Translate the estimated effect and uncertainty into net benefit'],
 'Potential outcomes define what changes because of an intervention, and random assignment supplies a credible comparison for estimating that change. This logic applies to product experiments, training, and operating policies. Translate the resulting effect into a spending decision using explicit values and costs, with a review plan for implementation.'),
8:('A causal graph makes the adjustment argument explicit',
 ['Use timing and mechanisms to justify arrows','Block common-cause paths and preserve the target pathway','Average conditional effects for the intended population'],
 'The general skill is to explain why a proposed control belongs in the comparison. A graph separates common causes, mechanisms, and selected consequences; the target effect determines which paths should remain. This reasoning guides adjustment across applications before any particular regression is fitted.'),
9:('An adjusted effect belongs to the population the estimator actually represents',
 ['Use the same eligibility, timing, and outcome','Inspect overlap, balance, and model specifications','Name the retained or predicted target population'],
 'Regression adjustment and matching implement a comparison justified by the assignment model. Both need a clearly defined target and adequate comparison information. When applying these methods to another policy, align the target populations before comparing estimates and examine how the counterfactual outcomes are constructed.'),
10:('Difference-in-differences identifies an effect through a justified comparison of changes',
 ['Define groups, periods, and the signed change contrast','Defend the untreated parallel-trend argument','Report the target, uncertainty, and decision implications'],
 'The transferable insight is that a comparison group can supply the background movement missing from a before-and-after evaluation. The credibility comes from the untreated trend argument, while the estimate comes from a difference in changes. Use the same reasoning for phased operating policies and other interventions with appropriate comparison histories.'),
}

def reorganize(n,c):
    headlines=deepcopy(MAIN[n])
    headlines['main']=[OPENERS[n]]
    headlines['decision-brief']=[MOTIVATION[n][0]]
    kept={}
    for s in c['sections']:
        key=s['id']; remove=set(MOVE.get(n,{}).get(key,[]))
        if not remove:
            kept[key]=s
            continue
        html=s['body']; tree=Tree(html); children=tree.root.elements()
        edits=[]; cursor=0; names=[]; found=set()
        for node in children:
            # Enriched sections consist of authored teaching blocks.
            assert node.has('teaching-block'),(n,key,node.tag)
            name=node.attrs['data-presentation-title']
            count=len(visual_frames(node.find(lambda x:x.has('teaching-visual')),name))
            if name in remove:
                edits.append((node.start,node.stop));found.add(name)
            else:names.extend(headlines[key][cursor:cursor+count])
            cursor+=count
        assert cursor==len(headlines[key]) and found==remove,(n,key,found,remove)
        for start,stop in reversed(edits):html=html[:start]+html[stop:]
        if names:
            kept[key]=dict(s,body=html);headlines[key]=names
        else:headlines.pop(key)
    theory,theory_titles=theory_sections(n)
    assert set(kept)==set(APPLICATION_ORDER[n]),(n,set(kept),APPLICATION_ORDER[n])
    applications=[dict(kept[k],phase='Worked application') for k in APPLICATION_ORDER[n]]
    if n in [7,8,9,10]:
        bridge_title='In this case, a positive reduction means fewer stockouts' if n!=10 else 'Reverse the signed DiD to report a stockout reduction'
        equation='Reduction = usual-operation rate − alert rate = −(treatment effect)' if n!=10 else 'Reported reduction = comparison change − adopter change = −DiD'
        bridge=teach(bridge_title,formula(equation),'The general theory defines an outcome effect as treatment minus control. Here a smaller stockout rate is desirable, so the application reports the negative of that effect as a positive reduction. Keep this sign convention when comparing estimates, intervals, and the break-even threshold.')
        applications[0]['body']=bridge+applications[0]['body']
        headlines[applications[0]['id']].insert(1 if applications[0]['id']=='read-data' else 0,bridge_title)
    applications[0]['body']=p('Worked application: '+c['stage']+'. Apply the general method to the shared retail records below.')+applications[0]['body']
    c['sections']=theory+applications
    c['title']=TITLES[n];c['method']=TITLES[n]
    c['scope']=SCOPE[n];c['motivation']=MOTIVATION[n]
    c['bigger']=TRANSFER[n][2];c['transfer_points']=TRANSFER[n][1]
    headlines['big-picture'][0]=TRANSFER[n][0]
    headlines.update(theory_titles)
    c['headlines']=headlines
    if n == 2:
        from lesson2_depth import restore
        c = restore(c)
    if n == 3:
        from lesson3_depth import restore
        c = restore(c)
    if n == 4:
        from lesson4_depth import restore
        c = restore(c)
    if n == 5:
        from lesson5_depth import restore
        c = restore(c)
    if n == 6:
        from lesson6_depth import restore
        c = restore(c)
    if n == 7:
        from lesson7_depth import restore
        c = restore(c)
    if n == 8:
        from lesson8_depth import restore
        c = restore(c)
    if n == 9:
        from lesson9_depth import restore
        c = restore(c)
    return c
