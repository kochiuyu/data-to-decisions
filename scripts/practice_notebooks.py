"""Readable worked cells, separate unfinished tasks, and executed answer notebooks."""
import ast,contextlib,io,json
from course_practice import WORK,TASKS,evidence

def md(id,text):
    return dict(cell_type='markdown',id=id,metadata={},source=text.splitlines(keepends=True))

def code(id,text,count=None,output='',hidden=False):
    return dict(cell_type='code',id=id,metadata={'jupyter':{'source_hidden':True}} if hidden else {},
                source=text.splitlines(keepends=True),execution_count=count,
                outputs=[dict(output_type='stream',name='stdout',text=output.splitlines(keepends=True))] if output else [])

def split_steps(source):
    """Keep exact bytes and top-level syntax intact; divide at comment-led stages."""
    lines=source.splitlines(keepends=True);tree=ast.parse(source)
    occupied=set()
    for node in tree.body:
        occupied.update(range(node.lineno+1,node.end_lineno+1))
    starts=[0]
    for i,line in enumerate(lines):
        if i and line.startswith('# ') and (i+1) not in occupied and i-starts[-1]>=4:
            starts.append(i)
        elif i and i-starts[-1]>=14 and (i+1) not in occupied and line.strip():
            starts.append(i)
    starts.append(len(lines))
    return [''.join(lines[a:b]) for a,b in zip(starts,starts[1:]) if b>a]

def title_for(part,i):
    first=part.splitlines()[0]
    return first[2:] if first.startswith('# ') else f'Calculation stage {i}'

def worked_cells(source,tail,n,technical,namespace):
    cells=[md(f'intro-{n}',f'# Lesson {n}: worked reference\n\nAttempt the student practice notebook first. Then run these smaller stages in order. Each stage preserves the original calculation and its checks.\n'),
           md(f'setup-note-{n}','## Shared setup\n\nRun this collapsed support cell once. It creates the documented synthetic case and analysis functions; you do not need to edit the generator to do the tasks.\n'),
           code(f'setup-{n}',source+'\n',1,hidden=True),
           md(f'worked-note-{n}','## Reconstruct the analysis\n\n'+technical+'\n')]
    for i,part in enumerate(split_steps(tail),1):
        cells.append(md(f'stage-note-{n}-{i}','### '+title_for(part,i)+'\n\nBefore running: identify the observation unit and predict which objects this stage will create. After running: inspect those objects and explain each check.\n'))
        captured=io.StringIO()
        with contextlib.redirect_stdout(captured):exec(compile(part,f'lesson{n}-stage-{i}','exec'),namespace)
        cells.append(code(f'stage-{n}-{i}',part,i+1,captured.getvalue()))
    return cells

STARTERS={
1:"extract = pd.DataFrame({'store':['A','B','C','C'], 'count':[10,np.nan,8,12], 'exposure':[100,50,40,40]})\n# Preserve both source claims; calculate each defensible target separately.\ncomplete_record_rates = None\nfull_extract_bounds = None\n",
2:"counts = np.array([[54,6],[28,12]])\n# Rows: short/long delivery. Columns: available/stockout.\noverall_probability = None\nconditional_probabilities = None\nrecombined_mean = None\n",
3:"from scipy.stats import norm\nsigma, margin, budget_n = 4.0, 1.0, 40\n# Use independent stores as units and round required counts upward.\nrequired_stores = None\nbudget_margin = None\ntrial_per_arm = None\n",
4:"x = np.array([-2.,-1.,0.,1.,2.]); mean_y = x*x\nX = np.column_stack([np.ones(5),x])\n# Fit, calculate residuals, then inspect totals AND their pattern.\nbeta = None\nresidual = None\nlosses = None\n",
5:"s = world()['stores']; x=s.lead_days.to_numpy(); y=s.baseline_rate.to_numpy()\nZ=np.column_stack([np.ones(len(s)),s.urban,s.baseline_demand-100,s.promotion_share,x*s.urban])\n# Remove the same columns from both x and y.\nrx = None\nry = None\npartial_slope = None\n",
6:"rows=world()['panel'].query('3<=week<=16').copy()\ndevelopment=rows.query('week<=13'); final=rows.query('week>=14').copy()\n# Use the existing validation-selected model. Evaluate, do not reselect on final outcomes.\nfinal_predictions = None\ncapacity_matched_metrics = None\n",
7:"n_offered, n_observed, offered_mean, control_mean = 50,40,12.,15.\n# Fill missing outcomes with each stated bound before averaging all assigned stores.\nworst_case_reduction_bounds = None\nrestricted_reduction_bounds = None\n",
8:"paths_a=[['D','W','Y']]\npaths_b=[['D','W','Y'],['D','U','Y']]\n# For these fork-only paths, list the ones remaining open after controlling W.\nopen_paths_a = None\nopen_paths_b = None\n",
9:"w=world(); covariates=['lead_days','urban','baseline_rate']\nv=w['stores'].query(\"cohort=='Voluntary'\")[[\"store_id\",\"offer\"]+covariates].sort_values('store_id').reset_index(drop=True)\n# Fit scores, exact-match urban status, apply original .2 SD logit caliper.\n# Keep outcomes out of this design table until you freeze pairs and inspect balance.\npairs = None\nbalance = None\nretained_target = None\n",
10:"before=np.array([18.,18.,10.,10.]); after=np.array([14.,14.,14.,14.]); D=np.array([1,1,0,0])\n# No unit receives a treatment in this labelled counterexample.\napparent_did = None\ninterpretation = ''\n"
}

def publish_practice(write,n,source,metadata):
    prompt,flaw,transfer,criteria=TASKS[n]
    intro=f'# Lesson {n}: independent practice\n\nExplain → reconstruct → diagnose → transfer. These tasks are not submitted or stored. Labelled exercise extracts are separate from the main case. Install the course requirements before running. Attempt the tasks before opening the companion solution notebook.\n'
    cells=[md(f'p-intro-{n}',intro),
           md(f'p-explain-{n}','## 1. Explain\n\nWrite the target population, outcome unit and main assumption in your own words. State what a successful calculation would establish—and what it would leave unresolved.\n'),
           md(f'p-explain-response-{n}','Your explanation: …\n'),
           md(f'p-setup-note-{n}','## Shared support code\n\nRun once. This collapsed cell provides numpy, pandas and the same case functions as the worked lab. It performs no network downloads and leaves the main data unchanged. You only need to edit the task cells below.\n'),
           code(f'p-setup-{n}',source+'\n',hidden=True),
           md(f'p-reconstruct-{n}','## 2. Reconstruct\n\n'+prompt+'\n\nReplace `None` with your calculation. Running the starter successfully is not evidence that the exercise is complete. Inspect your outputs and include units.\n'),
           code(f'p-work-{n}',STARTERS[n]),
           md(f'p-diagnose-{n}','## 3. Diagnose\n\n'+flaw+'\n\nName the mistaken step, show its consequence, and write a corrected version.\n'),
           md(f'p-diagnose-response-{n}','Your diagnosis and correction: …\n'),
           md(f'p-transfer-{n}','## 4. Transfer\n\n'+transfer+'\n\nSupply your calculation or diagram, state any missing information, and defend a next action.\n'),
           code(f'p-transfer-work-{n}','# Use this space for your transfer calculation or a small counterexample.\n'),
           md(f'p-transfer-response-{n}','Your recommendation and limits: …\n'),
           md(f'p-check-{n}','## 5. Review after attempting\n\n'+criteria+'\n\nCompare with the separate solution notebook. Correct your answer in a different paragraph and explain what changed. A justified request for more evidence can earn full credit.\n')]
    def save(kind,content):
        nb=dict(cells=content,metadata=metadata,nbformat=4,nbformat_minor=5)
        write(f'assets/lesson{n}-{kind}.ipynb',json.dumps(nb,indent=2,ensure_ascii=False)+'\n')
    save('practice',cells)
    import retail_case
    scope=dict(retail_case.__dict__)
    solutions=[md(f's-intro-{n}',f'# Lesson {n}: practice solutions\n\nRead after attempting. All exercise data and assumptions are labelled in the practice task.\n'),
               code(f's-setup-{n}',source+'\n',1,hidden=True)]
    for i,part in enumerate(split_steps(WORK[n]),1):
        solutions.extend([md(f's-note-{n}-{i}','## '+title_for(part,i)+'\n'),code(f's-work-{n}-{i}',part,i+1)])
        exec(compile(part,f'practice-solution-{n}-{i}','exec'),scope)
    output=json.dumps(scope['answer'],indent=2,allow_nan=False)+'\n'
    solutions.extend([code(f's-result-{n}',"print(json.dumps(answer, indent=2, allow_nan=False))\n",len(solutions)+1,output),
                      md(f's-reasoning-{n}','## Reasoning and transfer criteria\n\n'+criteria+'\n\n'+SOLUTION_NOTES[n]+'\n')])
    save('practice-solutions',solutions)
    write(f'assets/lesson{n}-practice-solutions.py',source+'\n'+WORK[n]+"\nprint(json.dumps(answer, indent=2, allow_nan=False))\n")
    write(f'assets/lesson{n}-practice-results.json',output)

SOLUTION_NOTES={
1:'The conflict and missing numerator create identification ranges, not sampling intervals. Use the visit-weighted clinic rate for a patient-level question; use the clinic mean only for an equal-clinic target. Do not call either universally correct.',
2:'The weighted result changes through composition alone. The table does not establish what would happen if delivery were changed. To infer a population probability from a sample, Lesson 3 adds a sampling model and uncertainty.',
3:'The 40-store budget yields about ±1.24 points. Clustered planning needs assumptions about outcomes within teams and the number of independent teams; 140 product-days at one store are not 140 independent stores.',
4:'A U-shaped conditional mean can have zero covariance with X because the positive and negative arms cancel. A scatterplot or residual plot shows the relationship; zero correlation does not establish independence.',
5:'Residualizing both variables preserves the full-model coefficient. In this interaction model the delivery main coefficient refers to nonurban stores; the urban slope adds the interaction. Cluster by the independent assignment or dependence unit, while explaining any cross-store shocks.',
6:'A hospital example might predict tomorrow’s deterioration from today’s recorded measurements, score adverse events among five reviewed patients, and randomize the review offer among eligible patients or teams. Benefits require outcomes under review versus a credible alternative; risk capture alone cannot supply those benefits.',
7:'A protocol should retain every randomized offer in its assigned group, seek missing outcomes, and report sensitivity. Selective service use requires additional assumptions for an effect of receipt. A profitability decision also needs the accounting threshold, not just a test against zero.',
8:'The helper only checks the two stated noncollider forks; it is not a general path-blocking algorithm. In the coaching transfer, both workload and private ability can confound assignment. A measured noisy proxy for ability can leave residual confounding. Randomization or an independently justified design may be needed.',
9:'The redesign retains 18 adopters and 10 unique controls. Exact urban and matched delivery means are balanced; the baseline SMD is about −.079. These checks do not rule out unobserved causes. The regression interval assumes a suitable mean model and independent store errors, conditional on the retained covariates; it does not quantify all design uncertainty. Excluded adopters require new comparisons or a separately defended extrapolation.',
10:'The untreated selection example violates parallel untreated trends. In the composition example A falls by 2 while the unpaired mean rises by 3. A common-start panel model adds stable store and common time effects; it still needs a trend argument, sufficient clusters, no anticipation and checks for unequal shocks and changing coverage.'
}
