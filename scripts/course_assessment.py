"""Cumulative assessments and decision criteria for the existing course pages."""
from retail_ui import p,table,formula

CHECKPOINTS = '''<section id="checkpoints"><h2>Three checkpoints build an independent recommendation</h2>
<p>Each lesson follows explain → reconstruct → diagnose → transfer. Begin with the student notebook, then consult its separate solution. The completed reference lab remains an auditable worked example. Record revisions to your reasoning rather than replacing your first answer silently.</p>
<h3>After Lesson 3: measurement and audit memo</h3><p>Submit a one-page memo with the observation key, denominator, reporting coverage, a repair log and a descriptive plot. Use the unresolved-data exercise to distinguish a sensitivity range from a sampling interval. State the audit target, independent unit, planned precision and budget. A sound answer can conclude that the measurement is not yet adequate for a spending decision.</p>
<h3>After Lesson 6: forecast and operating protocol</h3><p>Submit a dated prediction contract, a training/validation diagram, a benchmark comparison and a five-review workload calculation. Explain which data are available before each forecast. Report the final holdout once, label the added queue check exploratory, and propose a future evaluation period. Specify the action and the experiment needed to learn whether the action helps.</p>
<h3>After Lesson 10: expansion and evaluation plan</h3><p>Submit a two-page decision memo and a reproducible analysis appendix. Compare the populations and assumptions of the pilot, adjusted adoption study and rollout. Name the eligible next-phase stores, capacity, intervention cost, uncertainty and evidence that could reverse the decision. Use the <a href="synthesis.html#capstone">capstone brief and rubric</a>; a defended delay or narrower expansion is acceptable.</p>
<p><strong>Core probability route:</strong> Lesson 2 teaches a count table, proportions, conditioning and weighted expectations. Lesson 3 extends this to repeated samples and distributions of estimates. Detailed probability families and Bayes calculations remain optional appendix material.</p></section>'''

def capstone(results):
    reduction=results[10]['effect']['value']
    rows=[]
    for value,cost in [(6,20),(4,20),(6,35),(4,35)]:
        rows.append([value,cost,f'{cost/(1.4*value):.2f}',f'{1.4*value*reduction-cost:.2f}'])
    sensitivity=table(['Value per avoided stockout day','Policy cost / week','Break-even points','Rollout point-estimate net CU'],rows,'Accounting sensitivity scenarios; values and costs are assumptions, not measured benefits')
    rubric=table(['Criterion','Points','Evidence for full credit'],[
        ['Measurement and target',4,'Correct units, denominators, time periods, coverage and eligible population'],
        ['Design and identification',4,'Assignment/trend/control assumptions and plausible failure mechanisms'],
        ['Calculation and uncertainty',4,'Reproducible contrasts, matched targets, appropriate intervals and sensitivity'],
        ['Operations and economics',4,'Capacity, costs, benefits, alternatives and a feasible implementation protocol'],
        ['Judgment and communication',4,'A defensible choice, material limits and a specific result that would reverse it']],
        '20-point rubric: 0 absent; 1 named; 2 partly supported; 3 substantially supported; 4 complete and coherent')
    return '<section id="capstone"><h2>Capstone: make and defend your own decision</h2>'+p(
        'The recommendation above is one worked response, not the required answer. Prepare a two-page memo plus a reproducible appendix. Compare three feasible options: retain usual operations while gathering more evidence; expand to a defined comparable subset; or run a randomized next phase before broader commitment. Do not average estimates from different study populations into one universal effect.',
        'Planning scenario: the next phase has 30 eligible stores and staff can conduct five additional reviews each week. These capacity figures are exercise assumptions, not facts established by the case. State whether your intervention can be delivered within that constraint. A forecast review queue and the weekly alert service are distinct activities; document the workload and cost of each rather than treating the five-slot queue as permission to treat 30 stores.')+sensitivity+p(
        'A one-point reduction avoids 1.4 stockout product-days per store-week because exposure is 140. At the rollout point estimate, the least favorable displayed accounting scenario can reverse the financial recommendation. Repeat the cost calculation at the study interval endpoints, while recognizing that those endpoints do not quantify bias from a violated trend assumption or uncertain accounting values.',
        'Your analysis appendix must show the selected study target, effect and interval; a matching balance assessment where relevant; the capacity-matched forecast check; and at least one scenario involving missing data, an unmeasured common cause or an unequal untreated trend. Explain why your recommendation follows even after considering that scenario—or explain why it no longer follows.',
        'Predeclare an evaluation plan: eligible units, assignment/comparison, primary outcome, worthwhile improvement, sample-size assumptions, follow-up, implementation records, missing-outcome procedure and review date. Describe a result that would trigger continuation, revision or stopping. Separate a threshold chosen for teaching from an operating commitment that would require management agreement.')+rubric+p(
        'Assess the reasoning, not agreement with the worked recommendation. A proposal to delay, gather better comparison data or narrow the target can earn full credit. A numerical estimate with the wrong population or an unsupported causal claim cannot be rescued by polished presentation.',
        'Transfer challenge: repeat the decision structure for a staff-training program with incomplete attendance and shared managers. Describe what replaces the stockout denominator, why assignment and receipt differ, which unit should be randomized, and what outcome and cost records are needed. Do not reuse the retail effect size as evidence for training.')+'</section>'

def extend(html,section):
    assert html.endswith('</div></main>')
    return html[:-len('</div></main>')]+section+'</div></main>'
