"""Execute every notebook in a fresh kernel; store results outside source notebooks."""
from pathlib import Path
import argparse, json, os, sys, time, shutil
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec

ROOT = Path(__file__).resolve().parents[1]
class CurrentPythonKernel(KernelManager):
    @property
    def kernel_spec(self):
        return KernelSpec(argv=[sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'], display_name='Current Python', language='python')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT / 'notebooks')
    parser.add_argument('--output', type=Path, default=ROOT / 'build' / 'executed')
    parser.add_argument('--pattern', default='*.ipynb')
    parser.add_argument('--timeout', type=int, default=600)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault('MPLCONFIGDIR', str(args.output.resolve() / '.matplotlib'))
    os.environ.setdefault('IPYTHONDIR', str(args.output.resolve() / '.ipython'))
    os.environ.setdefault('JUPYTER_RUNTIME_DIR', str(args.output.resolve() / '.jupyter'))
    # Keep notebook-local helper modules available in the isolated execution directory.
    for helper in args.source.glob('*.py'):
        target=args.output/helper.name
        if helper.resolve()!=target.resolve(): shutil.copy2(helper,target)
    results=[]
    for path in sorted(args.source.glob(args.pattern)):
        print('START',path.name,flush=True)
        nb=nbformat.read(path, as_version=4)
        for cell in nb.cells:
            if cell.cell_type=='code': cell.outputs=[]; cell.execution_count=None
        started=time.perf_counter()
        client=NotebookClient(nb, timeout=args.timeout, kernel_manager_class=CurrentPythonKernel,
            resources={'metadata':{'path':str(args.output.resolve())}}, allow_errors=False)
        status='passed'; error=None
        try: client.execute()
        except Exception as exc: status='failed'; error=type(exc).__name__+': '+str(exc)
        nbformat.write(nb,args.output/path.name)
        results.append({'notebook':path.name,'status':status,'seconds':round(time.perf_counter()-started,2),
            'code_cells':sum(c.cell_type=='code' and bool(c.source.strip()) for c in nb.cells),
            'executed_cells':sum(c.cell_type=='code' and c.execution_count is not None for c in nb.cells),'error':error})
        (args.output/'execution.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
        print(status,path.name,results[-1]['seconds'], (error or '')[-500:],flush=True)
    if not results or any(r['status']!='passed' for r in results): sys.exit(1)
if __name__=='__main__': main()
