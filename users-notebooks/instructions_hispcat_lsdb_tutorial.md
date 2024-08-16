Instruções para criar o ambiente virtual para rodar o notebook de tutorial do HiPSCat / LSDB.

1) Limpar os ambientes de forma geral.
```bash
conda clean --all
pip cache purge
```

2) Criar o ambiente e ativar.
```bash
conda create -p $HOME/.conda/envs/lsdb_env
```
```bash
conda activate lsdb_env 
```
OU
```bash
source activate lsdb_env
```

3) Instalar pacotes necessários com conda.
```bash
conda install pathlib astropy bokeh holoviews geoviews cartopy matplotlib pandas dask distributed ipykernel lsdb pyogrio pyviz_comms jupyter_bokeh
```
Obs.: Esse passo demora bastante! Leva cerca de 10 a 20 minutos para o conda resolver o ambiente.

4) Instalar pacotes necessários com pip.
```bash
pip install hipscat
pip install hipscat-import
pip install dblinea
```

5) Fazer com que o ambiente seja disponibilizado como um kernel.
```bash
python -m ipykernel install --user --name=lsdb_env
```

6) Instalar a extensão "jupyter-bokeh" no menu de extensões do Jupyter Lab (barra lateral direita, símbolo de quebra-cabeças) e dar um refresh na página.

7) Instalar a extensão "pyviz-comms" no menu de extensões do Jupyter Lab (barra lateral direita, símbolo de quebra-cabeças) e dar um refresh na página.

8) Rodar o notebook.

Obs.: Se os gráficos não reenderizarem de primeira ao rodar o notebook, recomento que reinicie o seu servidor (STOP SERVER / START SERVER) e repita os passos 6, 7 e 8.