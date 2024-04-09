# Treat2p

Made to be used with suite2p, to extend it's capabilities with treatment one, on top of the nice extraction features of suite2p.

**Made after the matlab developments of Pierre Marie Gardères.**

## Getting started

To install this package, you simply need to hop into your own virtual / anaconda environment and run :

```
pip install git+https://gitlab.pasteur.fr/haisslab/analysis-packages/treat2p.git
```

It is as simple as that. 

In case there is some messages telling you about import errors when you import treat2p, (please don't hesitate to report problems with [the issues tracker](https://gitlab.pasteur.fr/haisslab/analysis-packages/treat2p/-/issues)) the necessary packages to install by yourself are :

- numpy
- joblib (a famous library to parallelize processings easily in python, usedc by scipy)
- scipy
- tqdm (a famous progress tracker, used by pandas)

## How to use :

In short, to run on a suite2p plane/channel :

```python
import treat2p
suite2p_path = r"C:\Users\yourname\Desktop\suite2p"
outputs, stats, ops = treat2p.run_treat2p(suite2p_path, plane = 0, chan = 1)
```

For a bit more explanations, please see the jupyter notebook tutorial [here](https://gitlab.pasteur.fr/haisslab/analysis-packages/treat2p/-/blob/main/treat2p_tuto.ipynb).
