"""Independent numerical checks of the functions actually defined in the notebooks."""
from pathlib import Path
import ast, contextlib, io, json, os, unittest
import numpy as np
from scipy.integrate import quad
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR', str(ROOT/'build'/'.matplotlib'))
METRICS={}
def load(prefix):
    p=next((ROOT/'notebooks').glob(prefix+' *.ipynb'))
    cells=json.loads(p.read_text())['cells']
    env={'__name__':'validation','G':1.,'M':1.,'rho0':1.,'depth_colors':['red','blue','green']}
    for c in cells:
        if c['cell_type']!='code': continue
        tree=ast.parse(''.join(c['source']))
        tree.body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef,ast.ClassDef))]
        with contextlib.redirect_stdout(io.StringIO()): exec(compile(tree,str(p),'exec'),env)
    return env
class PhysicsChecks(unittest.TestCase):
    def test_scalar_orders_and_time_grid(self):
        e=load('ex04')
        methods={'euler_method':1,'rk2_heun_method':2,'rk2_midpoint_method':2,'rk4_method':4,'adams_bashforth_moulton_2nd':2,'adams_bashforth_moulton_4th':4}
        orders={}
        for name,order in methods.items():
            f=e[name]; errors=[]
            for h in [1/40,1/80]:
                t,y=f(lambda t,y,a:-a*y,1.,0.,1.,h,2.)
                errors.append(abs(y[-1]-np.exp(-2)))
            p=np.log2(errors[0]/errors[1]); orders[name]=float(p)
            self.assertLess(abs(p-order),.25,name)
            t,y=f(lambda t,y,a:t,0.,2.,3.,.3,0.)
            self.assertAlmostEqual(t[-1],3.)
            self.assertTrue(np.allclose(np.diff(t),1/3))
            if order>=2:self.assertAlmostEqual(y[-1],2.5,places=10)
            for duration in [.01,.02]:
                tt,yy=f(lambda t,y,a:-y,1.,0.,duration,.02,1.)
                self.assertEqual(len(tt),len(yy)); self.assertTrue(np.all(np.isfinite(yy)))
            with self.assertRaises(ValueError):f(lambda t,y,a:-y,1.,0.,1.,0.,1.)
        METRICS['scalar_orders']=orders
    def test_backward_euler(self):
        e=load('ex01')
        for name in ['backward_euler_method','backward_euler_method_fsolve']:
            fn=e[name]; args=[e['f_nl']]
            if name=='backward_euler_method':args.append(e['df_nl_dy'])
            t,y=fn(*args,1.,0.,1.,.1,5.)
            residual=y[1:]-y[:-1]+.5*y[1:]**2
            self.assertLess(np.max(abs(residual)),1e-9)
    def test_kepler_orders_energy_alignment(self):
        e=load('ex05'); r0=np.array([1.,0.]);v0=np.array([0.,1.])
        methods={'euler_method':1,'rk2_heun_method':2,'rk2_midpoint_method':2,'rk4_method':4,'adams_bashforth_moulton_2nd':2,'adams_bashforth_moulton_4th':4,'leapfrog_method':2}
        orders={}
        for name,order in methods.items():
            fn=e[name]; errors=[]
            for h in [1/80,1/160]:
                t,r,v,de=fn(r0,v0,0.,1.,h)
                actual=.5*np.sum(v*v,axis=1)-1/np.linalg.norm(r,axis=1)
                self.assertEqual(len(t),len(de)); np.testing.assert_allclose(de,abs(actual+.5),atol=1e-14)
                errors.append(np.linalg.norm(r[-1]-[np.cos(1),np.sin(1)]))
            p=np.log2(errors[0]/errors[1]);orders[name]=float(p);self.assertLess(abs(p-order),.3,name)
            t,r,v,de=fn(r0,v0,0.,.01,.1);self.assertEqual(len(t),len(de))
        # Eccentric orbit: angular momentum and reversibility are distinct from energy.
        r0=np.array([1.,0.]);v0=np.array([0.,.7]);fn=e['leapfrog_method']
        t,r,v,de=fn(r0,v0,0.,20.,.002)
        angular=r[:,0]*v[:,1]-r[:,1]*v[:,0]
        drift=float(np.max(abs(angular-.7)));self.assertLess(drift,1e-11)
        _,rr,vv,_=fn(r[-1],-v[-1],0.,20.,.002)
        rev=float(np.linalg.norm(rr[-1]-r0)+np.linalg.norm(vv[-1]+v0));self.assertLess(rev,1e-8)
        METRICS['kepler_position_orders']=orders;METRICS['leapfrog_angular_momentum_max_error']=drift;METRICS['leapfrog_reversal_error']=rev
    def test_tree(self):
        metrics={}
        for prefix in ['ex06a','ex06b']:
            e=load(prefix);Body=e['Body'];BH=e['BarnesHut']
            with contextlib.redirect_stdout(io.StringIO()):
                tree=BH((-4,4,-4,4)); bodies=[Body([0,0],1),Body([1,0],2),Body([-2,0],1)]
                for b in bodies:tree.insert(b)
            np.testing.assert_allclose(tree.calculate_gravitational_force(bodies[0],theta=10),[1.75,0],atol=1e-14)
            with self.assertRaises(ValueError):tree.insert(Body([0,0],2))
            with self.assertRaises(ValueError):tree.insert(Body([8,0],2))
            rng=np.random.default_rng(17)
            bodies=[Body(p,m) for p,m in zip(rng.uniform(-2,2,(32,2)),rng.uniform(.1,2,32))]
            with contextlib.redirect_stdout(io.StringIO()):
                tree=BH((-4,4,-4,4))
                for b in bodies:tree.insert(b)
            direct=[]
            for b in bodies:
                direct.append(sum((b.mass*q.mass*(q.position-b.position)/np.linalg.norm(q.position-b.position)**3 for q in bodies if q is not b),start=np.zeros(2)))
            exact=np.array([tree.calculate_gravitational_force(b,theta=0) for b in bodies]);direct=np.array(direct)
            np.testing.assert_allclose(exact,direct,rtol=1e-12,atol=1e-12)
            self.assertAlmostEqual(tree.root.mass,sum(b.mass for b in bodies))
            approx=np.array([tree.calculate_gravitational_force(b,theta=.3) for b in bodies])
            metrics[prefix]={'theta0_max_abs_error':float(np.max(abs(exact-direct))),'theta03_max_relative_error':float(np.max(np.linalg.norm(approx-direct,axis=1)/np.linalg.norm(direct,axis=1)))}
        METRICS['tree']=metrics
    def test_spherical_harmonics(self):
        e=load('ex07a');c=e['compute_rho_lm']
        np.testing.assert_allclose(c(0,0,.5,e['uniform_sphere']),[np.sqrt(4*np.pi),0],atol=1e-12)
        np.testing.assert_allclose(c(1,0,.5,e['dipole_distribution']),[np.sqrt(4*np.pi/3),0],atol=1e-12)
        fn=e['reconstruct_density_cached']; errors=[]
        for rho in [e['uniform_sphere'],e['dipole_distribution'],e['triaxial_distribution']]:
            value=fn(3,.5,.8,1.2,rho);errors.append(float(abs(value-rho(.5,.8,1.2))))
            self.assertLess(errors[-1],1e-12)
            np.testing.assert_allclose(c(1,1,.5,rho,24,48),c(1,1,.5,rho,48,96),atol=1e-12)
        uniform_errors=[]
        for r in [.2,.8,1.5]:
            val=e['compute_gravitational_potential'](0,r,.3,.5,e['uniform_sphere'],10.)
            uniform_errors.append(float(abs(val-e['potential_uniform_sphere'](r,0,0))))
        self.assertLess(max(uniform_errors),1e-6)
        val=e['compute_gravitational_potential'](0,1.,0.,0.,e['plummer_sphere'],10.)
        tail=(1+10**2)**(-1.5)
        self.assertAlmostEqual(val-e['potential_plummer_sphere'](1.,0,0),tail,places=8)
        METRICS['spherical_reconstruction_errors']=errors;METRICS['uniform_potential_max_error']=max(uniform_errors);METRICS['plummer_rmax10_omitted_potential']=tail
    def test_ho92(self):
        e=load('ex08');phi=e['phi_basis'];rho=e['rho_basis'];norm=e['compute_I_nl']
        orth=[]
        for l in [0,1,2]:
            for n in [0,1,2]:
                numerical=quad(lambda r:phi(r,n,l)*rho(r,n,l)*r*r,0,np.inf,epsabs=1e-10)[0]
                orth.append(abs(numerical/norm(n,l)-1))
                cross=quad(lambda r:phi(r,n,l)*rho(r,n+1,l)*r*r,0,np.inf,epsabs=1e-10)[0]
                self.assertLess(abs(cross),1e-8)
                for r in [.2,1.,3.]:
                    h=1e-4*r
                    d1=(phi(r+h,n,l)-phi(r-h,n,l))/(2*h)
                    d2=(phi(r+h,n,l)-2*phi(r,n,l)+phi(r-h,n,l))/h**2
                    lhs=d2+2*d1/r-l*(l+1)*phi(r,n,l)/r**2
                    self.assertLess(abs(lhs-4*np.pi*rho(r,n,l))/(1+abs(lhs)),2e-6)
        self.assertLess(max(orth),1e-10)
        # Fine radial grid and extended boundary isolate the lowest Hernquist mode.
        r=np.geomspace(1e-5,1e3,4001);theta=np.linspace(0,np.pi,65);az=np.linspace(0,2*np.pi,65)
        result=e['compute_potential_for_density'](e['hernquist_sphere'],r,theta,az,n_max=0,l_max=0)
        err=float(np.max(abs(result[:,0,0]/(-1/(1+r))-1)))
        self.assertLess(err,1e-5)
        # Density scaling and restricted m support.
        r=np.linspace(.01,3,50);theta=np.linspace(0,np.pi,17);az=np.linspace(0,2*np.pi,17)
        a=e['compute_potential_for_density'](e['uniform_sphere'],r,theta,az,n_max=2,l_max=1,m_max=0)
        b=e['compute_potential_for_density'](lambda r,t,p:2*e['uniform_sphere'](r,t,p),r,theta,az,n_max=2,l_max=1,m_max=0)
        np.testing.assert_allclose(b,2*a,atol=1e-12)
        METRICS['ho92_normalization_relative_error']=max(orth);METRICS['hernquist_extended_grid_relative_error']=err
if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(PhysicsChecks)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    out=ROOT/'build';out.mkdir(exist_ok=True)
    (out/'physics.json').write_text(json.dumps(METRICS,indent=2))
    raise SystemExit(not result.wasSuccessful())
