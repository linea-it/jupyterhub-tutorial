# ignore warnings
import warnings
warnings.filterwarnings('ignore')
# computation
import numpy as np
# plots
import pylab as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import MultipleLocator
# widgets plot
import ipywidgets as widgets
# display
from IPython.display import Markdown as md
from IPython.display import display, Math


##############################
# funcs repeated
##############################
func = lambda x, a, b: a*x+b
def chi2(data, modelo, erro):
    return sum((data-modelo)**2/erro**2)
def like_chi2(chi2_, err):
    return np.exp(-.5*chi2_)/np.prod(np.sqrt(2*np.pi)*err)
def like(*args, **kwargs):
    return like_chi2(chi2(*args, **kwargs), args[2])
def show_chi2_numbers(x, y, err, parametros, func):
    out = ''
    for i, (a, b) in enumerate(parametros):
        out += (f'$c_{i}:'+\
          ' + '.join([rf'\frac{{({y_}-{func(x_, a, b)})^2}}{{{err_:.2f}^2}}'
                     for x_, y_, err_ in zip(x, y, err)])+\
          f'= {chi2(y, func(x, a, b), err):.2f}$\n\n'
               )
    return md(out)
##############################
# Plot funcs
##############################
def plot_nc():
    nc_om = np.loadtxt('data/NC_OmM.dat')
    nc_w = np.loadtxt('data/NC_wde.dat')
    
    vals = widgets.FloatSlider(
        value=1.0,
        min=.5,
        max=1.5,
        step=0.1,
        description='multiplicador:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.1f',
    )
    
    zbins = np.arange(nc_om[0].size+1)*.1
    zvals = np.arange(nc_om[0].size)*.1+.05
    
    f = plt.figure(figsize=(8, 4))
    axes = [plt.axes([.1, .3, .89, .6]), plt.axes([.1, .1, .89, .2])]
    axes[0].text(0, .82e5, 'Abundancia de halos de materia escura com $M\geq10^{13.8}M_\odot$ prevista para 10,000 graus$^2$\ncom a cosmologia de Plank 2015.')
    
    axes[0].hist(zvals, weights=nc_om[5], bins=zbins,
                 color='.7')
    
    axes[0].set_ylabel('numero de aglomerados')
    
    axes[1].set_ylabel('diferença')
    axes[1].set_xlabel('redshift')
    
    for ax in axes:
        ax.grid(lw=.5)
        ax.set_xlim(0, 2)
        
    axes[0].set_ylim(0, 8e4)
    axes[1].set_ylim(-1.1, 1.1)
    axes[1].axhline(0, lw=.8, ls='--', c='0')
    
    axes[0].set_xticklabels([])
    axes[0].set_yticklabels([f'{int(i):,}' 
                             for i in axes[0].get_yticks()])
    axes[1].set_yticklabels([f'{100*i:.0f}%' 
                             for i in axes[1].get_yticks()])
    
    @widgets.interact(v=vals)
    def update(v):
        i = int(10*v-5)
        
        axes[0].patches = axes[0].patches[:20]
        axes[0].hist(zvals, bins=zbins, weights=nc_om[i], color='r', histtype='step',
                     label=f'$\Omega_m = {v:.1f} \\times\Omega_m^0$')
        axes[0].hist(zvals, bins=zbins, weights=nc_w[i], color='C0', histtype='step',
                     label=f'$\mathcal{{w}} = {v:.1f} \\times \mathcal{{w}}^0$')
        axes[0].legend(loc=1)
        
        axes[1].lines = axes[1].lines[:1]
        axes[1].plot(zvals, nc_om[i]/nc_om[5]-1, c='C0')
        axes[1].plot(zvals, nc_w[i]/nc_w[5]-1, c='r')
def plot_with_line(x, y, err, func=func,
    show_chi2=False):
    avals = widgets.FloatSlider(
        value=0,
        min=-10,
        max=10.0,
        step=0.01,
        description='a:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )
    bvals = widgets.FloatSlider(
        value=5,
        min=-10,
        max=10.0,
        step=0.01,
        description='b:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )

    plt.figure(figsize=(6, 4))
    ax = plt.axes()
    ax.scatter(x, y)
    ax.errorbar(x, y, err,
                ls='', fmt='.',
                lw=1,
                capsize=5)
    ax.grid(lw=.5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_ylim(-2, 15)

    @widgets.interact(a=avals, b=bvals)
    def update(a, b):
        ax.lines = []
        signal = '+' if b>=0 else ''
        label=f'$f(x) = {a:.2f}\,x {"+" if b>=0 else ""} {b:.2f}$'
        if show_chi2:
                label += f'\n$\chi^2 = {chi2(y, func(x, a, b), err):.4f}$'
        ax.plot(x, func(x, a, b), c='r', label=label)
        ax.legend(loc=2)
def plot_fit_degeneressence(x, y, err,
    a_vals, b_vals, func=func):
    plot_data = {
        'datapoints':[True for i in range(5)],
        'fitpars':{'a':2.5, 'b':.5},
        'err':{'v':1}
        }
    
    a_grid, b_grid, chi2_grid = compute_chi2_grid(a_vals, b_vals, func, x, y, err)
    like_grid = like_chi2(chi2_grid, err)

    avals = widgets.FloatSlider(
        value=plot_data['fitpars']['a'],
        min=a_vals[0]+.1,
        max=a_vals[-1]-.1,
        step=0.01,
        description='a:',
        disabled=False,
        continuous_update=True,
        orientation='vertical',
        readout=True,
        readout_format='.2f',
        #layout=widgets.Layout(width='500px')
    )
    bvals = widgets.FloatSlider(
        value=plot_data['fitpars']['b'],
        min=b_vals[0]+.1,
        max=b_vals[-1]-.1,
        step=0.01,
        description='b:',
        disabled=False,
        continuous_update=True,
        orientation='vertical',
        readout=True,
        readout_format='.2f',
        #layout=widgets.Layout(width='500px')
    )
    evals = widgets.FloatSlider(
        value=plot_data['err']['v'],
        min=0.001,
        max=10,
        step=0.2,
        description='err:',
        disabled=False,
        continuous_update=True,
        orientation='vertical',
        readout=True,
        readout_format='.1f',
        #layout=widgets.Layout(width='500px')
    )
    output = widgets.Output()
    with output:
        fig, axes = plt.subplots(2, figsize=(6, 8))
    axes[0].contourf(a_grid, b_grid, like_grid,
                levels=np.linspace(like_grid.min(), like_grid.max(), 100)
                )
    
    a, b = plot_data['fitpars']['a'], plot_data['fitpars']['b']
    axes[0].scatter(a, b, c='r')
    axes[0].set_xlabel('a')
    axes[0].set_ylabel('b')
    
    axes[1].scatter(x, y)
    axes[1].errorbar(x, y, err, 
                ls='', fmt='.',
                lw=1,
                capsize=5)
    axes[1].grid(lw=.5)
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('y')
    axes[1].set_ylim(-2, 15)
    axes[1].plot(x, func(x, a, b), c='r',
            label=f'$f(x) = {a:.2f}\,x {"+" if b>=0 else ""} {b:.2f}$\n'+
            f'$\chi^2 = {chi2(y, func(x, a, b), err):.4f}$')
    axes[1].legend(loc=2)
    
    points = [widgets.Checkbox(
                description=f'point {i+1}',
                value=True
                    )
              for i in range(5)]

    def update(change, argtype, argname):
        plot_data[argtype][argname] = change.new
        
        a, b = plot_data['fitpars']['a'], plot_data['fitpars']['b']
        use = plot_data['datapoints']
        if argtype in ('datapoints', 'err'):
            like_temp = like_chi2(compute_chi2_grid(a_vals, b_vals,
                    func, x[use], y[use], err[use]*plot_data['err']['v'])[2], err[use]*plot_data['err']['v'])
            axes[0].collections = []
            axes[0].contourf(a_grid, b_grid, like_temp,
                levels=np.linspace(like_temp.min(), like_temp.max(), 100)
                )
            axes[1].collections = []
            axes[1].scatter(x[use], y[use], color='C0',)
            axes[1].errorbar(x[use], y[use], err[use]*plot_data['err']['v'], 
                        ls='', fmt='.', color='C0',
                        lw=1, capsize=5)
    
        axes[0].collections = axes[0].collections[:-1]
        axes[0].scatter(a, b, c='r')
        axes[1].lines = []
        axes[1].plot(x, func(x, a, b), c='r',
                label=f'$f(x) = {a:.2f}\,x {"+" if b>=0 else ""} {b:.2f}$\n'+
                f'$\chi^2 = {chi2(y[use], func(x[use], a, b), err[use]*plot_data["err"]["v"]):.4f}$')
        axes[1].legend(loc=2)
    points[0].observe(lambda c:update(c, 'datapoints', 0),'value')
    points[1].observe(lambda c:update(c, 'datapoints', 1),'value')
    points[2].observe(lambda c:update(c, 'datapoints', 2),'value')
    points[3].observe(lambda c:update(c, 'datapoints', 3),'value')
    points[4].observe(lambda c:update(c, 'datapoints', 4),'value')
    
    avals.observe(lambda c:update(c, 'fitpars', 'a'),'value')
    bvals.observe(lambda c:update(c, 'fitpars', 'b'),'value')
    evals.observe(lambda c:update(c, 'err', 'v'),'value')
    
    return widgets.HBox([output, 
                  widgets.VBox(
                      [widgets.HBox([avals, bvals])]+[evals]+points)])
def plot_like_deg():

    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes()
    ax.set_xlabel('a')
    ax.set_ylabel('b')
    
    fig.canvas.toolbar_visible = False
    fig.canvas.header_visible = False
    fig.canvas.resizable = True
    
    plt.show()
    
    vals = widgets.FloatSlider(
        value=0,
        min=-1,
        max=1,
        step=0.1,
        description=r'$\theta$:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )
    
    vals_pars = np.linspace(-5, 5, 100)
    
    @widgets.interact(t=vals)
    def update(t):
        grid1, grid2, like2_grid = compute_grid(vals_pars, vals_pars,
                            func=lambda a, b: np.exp(-(a**2+b**2+2*t*a*b))
                                               )
        ax.collections = []
        ax.contourf(grid1, grid2, like2_grid,
                levels=np.linspace(like2_grid.min(), like2_grid.max(), 100)
                )
    
        ax.set_title(f'$\mathcal{{L}} \propto \exp{{\left[-(a^2+b^2{"+" if t>=0 else ""}{2*t}\; ab)\\right]}}$')
        plt.show()
def plot_like_marg(x, y, err,
    a_vals, b_vals, func=func):
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection='3d')
    
    a_grid, b_grid, chi2_grid = compute_chi2_grid(a_vals, b_vals, func, x, y, err)
    like_grid = like_chi2(chi2_grid, err)
    ax.plot_wireframe(a_grid, b_grid, like_grid,
                     lw=.5)
    
    ax.set_xlabel('a')
    ax.set_ylabel('b')
    ax.set_zlabel('$\mathcal{L}$')
    
    
    fig.canvas.toolbar_visible = False
    fig.canvas.header_visible = False
    fig.canvas.resizable = True
    
    plt.show()
    
    vals = widgets.FloatSlider(
        value=0,
        min=-10,
        max=10.0,
        step=0.01,
        description='value:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )
    
    @widgets.interact(par=['a', 'b'], v=vals)
    def update(par, v):
        ax.lines = []
        if par=='a':
            l = [like(y, func(x, v, b), err) for b in b_vals]
            ax.plot(b_vals*0+v, b_vals, l, c='r')
        elif par=='b':
            l = [like(y, func(x, a, v), err) for a in a_vals]
            ax.plot(a_vals, a_vals*0+v, l, c='r')
def plot_mr(data, fit=False):
    f = plt.figure(figsize=(7, 7))
    ax = plt.axes()
    ax.errorbar(data['Richness'], data['Mass_Mpc'],
                 data['MassError_Mpc'], ls='', lw=.5,
                fmt='.', markersize=1, capsize=2)
    ax.set_xlabel('Richness')
    ax.set_ylabel('Mass [$M_{\odot}$]')
    ax.grid(which='both')
    ax.grid(which='minor',  linewidth=.5)

    xlog = widgets.Checkbox(
        value=False,
        description='log scale (x)',
        disabled=False,
        indent=False
    )
    ylog = widgets.Checkbox(
        value=False,
        description='log scale (y)',
        disabled=False,
        indent=False
    )
    avals = widgets.FloatSlider(
        value=0,
        min=-5,
        max=5,
        step=0.01,
        description=r'$\alpha$:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )
    bvals = widgets.FloatSlider(
        value=15,
        min=0,
        max=20,
        step=0.01,
        description=r'$\beta$:',
        disabled=False,
        continuous_update=True,
        orientation='horizontal',
        readout=True,
        readout_format='.2f',
        layout=widgets.Layout(width='500px')
    )

    powfmt = lambda x: '%s\\times 10^{%s}'%tuple(f'{x:.2e}'.replace('+','').split('e'))


    def update(a, b, xlog, ylog):
        ax.lines = []
        if a is not None:
            r_ = np.linspace(np.log10(data['Richness'].min()),
                         np.log10(data['Richness'].max()),
                         100)
            ax.plot(10**r_, 10**func(r_, a, b), c='r')
            plt.title(f'$logM(N_{{gals}}) = {a:.2f}\,logN_{{gals}}+ {b:.2f}$\n'+
                  f'$M(N_{{gals}}) = {powfmt(10**b)}\,(N_{{gals}})^{{{a:.2f}}}$\n')
        xscale = 'log' if xlog else 'linear'
        yscale = 'log' if ylog else 'linear'
        ax.set_xscale(xscale)
        ax.set_yscale(yscale)
        if ylog:
            ax.set_ylim(1e13, 5e15)
        else:
            ax.set_ylim(1e10, 5e15)
    if fit:
        @widgets.interact(a=avals, b=bvals, xlog=xlog, ylog=ylog)
        def up(a, b, xlog, ylog):
            update(a, b, xlog, ylog)
    else:
        @widgets.interact(xlog=xlog, ylog=ylog)
        def up(xlog, ylog):
            update(None, None, xlog, ylog)

##############################
### Functions for students ###
##############################
def compute_grid(vals1, vals2, func):
    '''
    Calcula uma função em uma grade 2D
    
    Parameters
    ----------
    vals1: array
        Valores para o parâmetro 1
    vals2: array
        Valores para o parâmetro 2
    func: function
        Função a ser calculada
        
    Returns
    -------
    grid1: array 2D
        Valores do parâmetro 1 na grade
    grid2: array 2D
        Valores do parâmetro 2 na grade
    chi2_grid: array 2D
        Valores da função na grade
    '''
    grid1 = np.outer(vals1, vals2*0+1)
    grid2 = np.outer(vals2, vals1*0+1).T
    chi2_grid = np.array([[func(p1, p2) for p2 in vals2]
                                for p1 in vals1])
    return grid1, grid2, chi2_grid
def compute_chi2_grid(vals1, vals2, func, x, y, err):
    '''
    Calcula o chi^2 em uma grade 2D
    
    Parameters
    ----------
    vals1: array
        Valores para o parâmetro 1
    vals2: array
        Valores para o parâmetro 2
    func: function
        Função a ser ajustada, deve ter como input (x, parâmetro1, parâmetro2)
    x: array
        Valores da componente x
    y: array
        Valores da componente y
    err: array
        Erros na componente y
        
    Returns
    -------
    grid1: array 2D
        Valores do parâmetro 1 na grade
    grid2: array 2D
        Valores do parâmetro 2 na grade
    chi2_grid: array 2D
        Valores do chi^2 na grade
    '''
    return compute_grid(vals1, vals2, func=lambda p1, p2: chi2(y, func(x, p1, p2), err))
def plot_likelihood2D(alpha_vals, beta_vals, func, x, y, err, nlevels=100):
    '''
    Grafica a likelihood em uma grade com cores
    
    Parameters
    ----------
    vals1: array
        Valores para o parâmetro 1
    vals2: array
        Valores para o parâmetro 2
    func: function
        Função a ser ajustada, deve ter como input (x, parâmetro1, parâmetro2)
    x: array
        Valores da componente x
    y: array
        Valores da componente y
    err: array
        Erros na componente y
    nlevels: int
        Numeros de niveis da figura
    '''
    grid1, grid2, chi2_grid = compute_chi2_grid(alpha_vals, beta_vals,
                                                func, x, y, err)
    like_grid = like_chi2(chi2_grid, err)
    
    fig = plt.figure(figsize=(7, 7))
    plt.contourf(grid1, grid2, like_grid,
                levels=np.linspace(like_grid.min(), like_grid.max(), nlevels)
                )

    plt.xlabel(r'$\alpha$')
    plt.ylabel(r'$\beta$')

    plt.show()
def plot_likelihood3D(alpha_vals, beta_vals, func, x, y, err):
    '''
    Grafica a likelihood em uma grade em 3D
    
    Parameters
    ----------
    vals1: array
        Valores para o parâmetro 1
    vals2: array
        Valores para o parâmetro 2
    func: function
        Função a ser ajustada, deve ter como input (x, parâmetro1, parâmetro2)
    x: array
        Valores da componente x
    y: array
        Valores da componente y
    err: array
        Erros na componente y
    '''
    grid1, grid2, chi2_grid = compute_chi2_grid(alpha_vals, beta_vals,
                                                func, x, y, err)
    like2_grid = like_chi2(chi2_grid, err)
    
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_wireframe(grid1, grid2, like2_grid,
                     lw=.5)

    ax.set_xlabel(r'$\alpha$')
    ax.set_ylabel(r'$\beta$')
    ax.set_zlabel(r'$\mathcal{L}$')

    fig.canvas.toolbar_visible = False
    fig.canvas.header_visible = False
    fig.canvas.resizable = True

    plt.show()
