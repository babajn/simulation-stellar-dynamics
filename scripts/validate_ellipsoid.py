import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from validate_physics import load
import numpy as np
from scipy.integrate import quad
x=load('ex08')
axes=np.array([1.,1.5,2.]);rs=np.linspace(.1,5,50)
def exact(r,j):
 low=max(0.,r*r-axes[j]**2)
 return -np.pi*np.prod(axes)*quad(lambda u:(1-r*r/(axes[j]**2+u))/np.sqrt(np.prod(axes**2+u)),low,np.inf,epsabs=1e-10)[0]
results={}
for label,nr,nt,np_,nmax,lmax in [('teaching',50,31,61,10,5),('refined',101,49,97,16,8)]:
 r=np.linspace(.1,5,nr);t=np.linspace(0,np.pi,nt);p=np.linspace(0,2*np.pi,np_)
 val=x['compute_potential_for_density'](x['ellipsoidal_sphere'],r,t,p,n_max=nmax,l_max=lmax)
 indices=[(nt//2,0),(nt//2,(np_-1)//4),(0,0)]
 errors={}
 for j,(ti,pi) in enumerate(indices):
  ana=np.array([exact(q,j) for q in r]);rel=abs(val[:,ti,pi]/ana-1)
  errors['xyz'[j]]=float(max(rel))
 results[label]=errors
print(json.dumps(results,indent=2));out=Path(__file__).resolve().parents[1]/'build'; out.mkdir(exist_ok=True); (out/'ellipsoid.json').write_text(json.dumps(results,indent=2))
assert max(results['teaching'].values()) < .025
assert max(results['refined'].values()) < .015
