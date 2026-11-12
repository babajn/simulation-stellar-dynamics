"""Check candidate content without printing detected secret values."""
from pathlib import Path
import hashlib,json,re,sys
import nbformat
ROOT=Path(__file__).resolve().parents[1]
# Exact reviewed asset only. Review PDF text, metadata, links and page images
# before updating this digest; arbitrary PDFs remain excluded.
REVIEWED_ASSETS={
 'docs/lecture_baba_all.pdf':'1c83dfab1a6fa09dfc582fbc188a193e3bbbb30651d0e2d6b37b8e7ba802772d',
}
SKIP={'.git','build','.venv','venv','__pycache__','.ipynb_checkpoints'}
PATTERNS={
 'private key':r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
 'GitHub token':r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',
 'API credential':r'\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16})',
 'local user path':r'(?:/Users/|/home/)[A-Za-z0-9_-]+/',
 'email address':r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',
}
def main():
 issues=[];files=[]
 for p in sorted(ROOT.rglob('*')):
  rel=p.relative_to(ROOT)
  if any(x in SKIP for x in rel.parts) or not p.is_file():continue
  files.append(p)
  if rel.as_posix() in REVIEWED_ASSETS:
   if hashlib.sha256(p.read_bytes()).hexdigest()!=REVIEWED_ASSETS[rel.as_posix()]:
    issues.append((str(rel),'reviewed asset changed; review required'))
   continue
  if p.stat().st_size>10*1024**2:issues.append((str(rel),'over 10 MiB'))
  if p.suffix.lower() in {'.pdf','.key','.gif','.mp4'}:issues.append((str(rel),'excluded asset'))
  text=p.read_text(errors='replace')
  for label,pattern in PATTERNS.items():
   if re.search(pattern,text):issues.append((str(rel),label))
  if p.suffix=='.ipynb':
   nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
   for i,c in enumerate(nb.cells):
    if c.get('attachments'):issues.append((str(rel),f'attachment in cell {i}'))
    if c.cell_type=='code' and (c.outputs or c.execution_count is not None):issues.append((str(rel),f'saved output/count in cell {i}'))
 if issues:
  print(json.dumps(issues,ensure_ascii=False,indent=2));return 1
 print(f'PASS: {len(files)} candidate files, {sum(p.stat().st_size for p in files)} bytes; no matches in configured checks.')
 return 0
if __name__=='__main__':sys.exit(main())
