"""Dependency-free release checks; optional --execute reruns every synthetic lab."""
from pathlib import Path
from html.parser import HTMLParser
import ast,json,re,sys,subprocess,urllib.parse,math
from guided_paths import story
from guided_methods import method
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'dist'
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.h1=0;self.stops=0;self.svgs=0;self.named_svgs=0;self.tables=0;self.feed(text)
 def handle_starttag(self,tag,attributes):
  a=dict(attributes)
  if a.get('id'):self.ids.append(a['id'])
  for key in ['href','src']:
   if a.get(key):self.links.append(a[key])
  if tag=='h1':self.h1+=1
  if 'lesson-step' in a.get('class','').split():self.stops+=1
  if tag=='svg':
   self.svgs+=1
   if a.get('aria-label') or a.get('aria-labelledby'):self.named_svgs+=1
  if tag=='table':self.tables+=1

def finite(value):
 if isinstance(value,float):assert math.isfinite(value),'Nonfinite result'
 elif isinstance(value,dict):
  for x in value.values():finite(x)
 elif isinstance(value,list):
  for x in value:finite(x)

def validate(execute=False):
 pages={p:Page(p.read_text(encoding='utf-8')) for p in SITE.glob('*.html')}; assert len(pages)==35,('Page count',len(pages))
 expected={1:18,2:24,3:24,4:24,5:24,6:24,7:24,8:28,9:28,10:28};report={'pages':{},'labs':{},'executed':execute}
 for path,page in pages.items():
  assert page.h1==1,(path,'H1 count');assert len(page.ids)==len(set(page.ids)),(path,'Duplicate IDs')
  assert page.named_svgs==page.svgs,(path,'Unnamed SVG')
  for link in page.links:
   u=urllib.parse.urlsplit(link)
   if u.scheme or u.netloc:continue
   target=(path.parent/urllib.parse.unquote(u.path)).resolve() if u.path else path.resolve()
   assert target.is_relative_to(SITE.resolve()),(path,'Link escapes site',link)
   assert target.is_file(),(path,'Missing local target',link)
   if u.fragment and target.suffix=='.html':assert urllib.parse.unquote(u.fragment) in Page(target.read_text(encoding='utf-8')).ids,(path,'Missing anchor',link)
  match=re.fullmatch(r'lesson-(\d+)\.html',path.name)
  guide=re.fullmatch(r'lesson-(\d+)-guide\.html',path.name)
  appendix=re.fullmatch(r'lesson-(\d+)-appendix\.html',path.name)
  if match:
   n=int(match[1]);assert page.stops==0,(path,'Main lesson should be concise',page.stops)
   text=path.read_text(encoding='utf-8')
   assert 'Reveal the case’s known answer' in text and f'lesson-{n}-guide.html' in text,(path,'Missing case answer or guide link')
   assert all(f'<section id="{section}">' in text for section in ('situation','evidence','decision')),(path,'Missing business narrative section')
   assert text.index('id="big-picture"')>text.index('id="decision"'),(path,'Bigger picture should close the business story')
   main=text.split('<main id="main">',1)[1].split('</main>',1)[0]
   assert len(re.findall(r"[A-Za-z0-9]+",re.sub(r'<[^>]+>',' ',main)))>=350,(path,'Business case is too brief')
  if guide:
   n=int(guide[1]);data=json.loads((SITE/f'assets/lesson{n}-results.json').read_text(encoding='utf-8'))
   assert page.stops==len(story(n,data)['chapters'])==3,(path,'Guided chapter count',page.stops)
   text=path.read_text(encoding='utf-8')
   assert 'Guided route' in text and 'Decision check' in text and 'Reveal the case’s known answer' in text,(path,'Missing guided framing, decision or case answer')
   assert text.count('id="worked-method"')==1 and 'Worked step:' in text,(path,'Missing embedded method')
   assert f'lesson-{n}-appendix.html#{method(n,data)["anchor"]}' in text,(path,'Missing linked appendix method')
   assert text.index('id="big-picture"')>text.index('id="guided-reveal"'),(path,'Bigger picture should close the guided story')
  if appendix:
   n=int(appendix[1]);assert page.stops==expected[n],(path,'Appendix stop count',page.stops)
   assert 'How the fictional data were generated' in path.read_text(encoding='utf-8'),(path,'Missing generation appendix')
  report['pages'][path.name]={'stops':page.stops,'figures':page.svgs,'tables':page.tables}
 for n in range(1,11):
  src=(SITE/f'assets/lesson{n}-lab.py').read_text(encoding='utf-8');ast.parse(src)
  nb=json.loads((SITE/f'assets/lesson{n}-lab.ipynb').read_text(encoding='utf-8'));data=json.loads((SITE/f'assets/lesson{n}-results.json').read_text(encoding='utf-8'));finite(data)
  ids=[c.get('id') for c in nb['cells']]; assert all(ids) and len(ids)==len(set(ids)),(n,'Missing or duplicate notebook cell IDs')
  cells=[c for c in nb['cells'] if c['cell_type']=='code'];assert cells,(n,'No notebook code')
  combined=''.join(''.join(c['source']) for c in cells);assert combined==src,(n,'Notebook/script drift')
  out=''.join(''.join(o.get('text',[])) for c in cells for o in c.get('outputs',[]) if o.get('output_type')=='stream')
  assert json.loads(out)==data,(n,'Notebook/result mismatch')
  assert all(c.get('execution_count') is not None for c in cells),(n,'Unexecuted cell')
  assert not any(c.get('attachments') for c in nb['cells']),(n,'Hidden notebook attachment')
  if execute:
   result=subprocess.run([sys.executable,str(SITE/f'assets/lesson{n}-lab.py')],cwd=ROOT,check=True,capture_output=True,text=True)
   assert json.loads(result.stdout)==data,(n,'Recomputed result drift')
  report['labs'][n]={'code_cells':len(cells),'verified_saved_output':True,'rerun':execute}
 for path in ROOT.rglob('*'):
  if not path.is_file() or any(s in path.parts for s in ['.git','.venv','__pycache__','.openai']):continue
  assert path.suffix.lower() not in {'.csv','.dta','.xlsx','.xls','.zip','.pdf','.parquet','.feather'},(path,'Unexpected embedded artifact')
  if path.suffix in {'.html','.js','.json','.py','.ipynb','.md','.txt','.yml','.css'}:
   txt=path.read_text(encoding='utf-8')
   assert not re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}',txt),(path,'Secret-shaped value')
   if path.suffix in {'.html','.py','.ipynb','.json'} and 'outline' not in path.name:
    assert not re.search(r'read_(?:csv|excel|stata|parquet)\s*\(\s*[\'\"]https?://|requests\.get|urlopen\(',txt),(path,'External data access')
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':validate('--execute' in sys.argv)
