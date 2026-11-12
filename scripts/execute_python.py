"""Execute Python-only notebooks in fresh processes, saving plots via Agg.

This does not test Jupyter frontend rendering, widgets, or magics.
"""
import sys

def execute_one():
    from pathlib import Path
    import json,sys,traceback,hashlib
    p=Path(sys.argv[1]);out=Path(sys.argv[2]);sys.path.insert(0,str(p.parent))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    nb=json.loads(p.read_text());count=0;figcount=0
    code='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
    def show(*args,**kwargs):
     nonlocal figcount
     for num in plt.get_fignums():
      figcount+=1;plt.figure(num).savefig(out/f'figure-{figcount:03d}.png',dpi=90,bbox_inches='tight')
     plt.close('all')
    plt.show=show
    result={'status':'passed','code_sha256':hashlib.sha256(code.encode()).hexdigest(),'error':None}
    env={'__name__':'__main__','__file__':str(p)}
    try:
     for i,c in enumerate(nb['cells']):
      if c['cell_type']=='code' and ''.join(c['source']).strip():
       exec(compile(''.join(c['source']),f'{p.name}:cell{i+1}','exec'),env);count+=1
    except Exception:
     result['status']='failed';result['error']=traceback.format_exc();traceback.print_exc()
    finally:
     result.update(executed_cells=count,code_cells=sum(c['cell_type']=='code' and bool(''.join(c['source']).strip()) for c in nb['cells']),figures=figcount)
     (out/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(result['status']!='passed')

def main():
    from pathlib import Path
    import json, subprocess, sys, time, os
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--pattern',default='*.ipynb')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];out=root/'build/python-executed';out.mkdir(parents=True,exist_ok=True)
    worker=Path(__file__).resolve()
    results=[]
    for p in sorted((root/'notebooks').glob(args.pattern)):
     dest=out/p.stem;dest.mkdir(exist_ok=True)
     started=time.perf_counter()
     env=os.environ.copy();env['MPLBACKEND']='Agg';env['MPLCONFIGDIR']=str(out/'.matplotlib')
     with (dest/'stdout.txt').open('w') as stdout,(dest/'stderr.txt').open('w') as stderr:
      job=subprocess.run([sys.executable,str(worker),str(p),str(dest),"--worker"],cwd=dest,stdout=stdout,stderr=stderr,env=env)
     result=json.loads((dest/'result.json').read_text()) if (dest/'result.json').exists() else {'status':'failed','error':'worker exited before writing result'}
     result.update(notebook=p.name,seconds=round(time.perf_counter()-started,2),engine='fresh-python-process / Agg',exit_code=job.returncode)
     results.append(result);(out/'execution.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
     print(result,flush=True)
     if job.returncode:print((dest/'stderr.txt').read_text()[-2000:],flush=True)
    raise SystemExit(any(x['status']!='passed' for x in results))

if __name__=="__main__":
    execute_one() if "--worker" in sys.argv else main()
