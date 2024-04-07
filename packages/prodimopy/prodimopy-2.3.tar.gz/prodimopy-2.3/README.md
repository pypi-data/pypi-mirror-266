# prodimopy

Python package for reading and plotting ProDiMo results.

Any bug reports or feature requests are very welcome.
If you want to contribute some code please contact me (Christian Rab).

[[_TOC_]]


## Notebook examples
If you want to take a look before installing you can try prodimopy
on the web in a binder environment:

[![prodimopy binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/git/https%3A%2F%2Fgitlab.astro.rug.nl%2Fprodimo%2Fprodimopy/HEAD?labpath=notebooks)

On your left hand side you will see the notebooks, just open one and try it!

## Documentation
Please check out the documentation! Click on the badge!

[![Documentation Status](https://readthedocs.org/projects/prodimopy/badge/?version=latest)](https://prodimopy.readthedocs.io/en/latest/?badge=latest)

## Requirements
prodimopy uses several additional python packages which are commonly used in the astronomical community. 
If you use [anaconda](https://www.anaconda.com/distribution/) all this packages should be available in your python distribution. The following packages are required

* *matplotib*:   required for the plotting part only, version>3 is recommended  
* *astropy*:     version > 4.0 
* *numpy*       version >= 1.17
* *scipy*:       no known special requirements
* *pandas*:      version > 1.4, only required for slab models
* *adjustText*:  version >= 0.8, only required for slab models
* *spectres*:    version >= 2.2.0, only required for slab models

If you use the setup script (see Installation) those packages will be installed automatically if necessary. **We only support python3**.

## Installation

### via pip (for Users)
If you just want a stable version you can also use pip to install the project. Just type in the command line 

```
pip install prodimopy
```

to upgrade to a new version you can also use pip. We recommend to do it this way. 

```
pip install --upgrade --upgrade-strategy only-if-needed prodimopy
```



### from source (for Developers)
I you always want to have the most recent version or if you plan to change the code (you are very welcome) clone this repository and install the package directly from the source: 

* change into a directory of your choice and 
* clone the repository (git will create a new directory called prodimopy)

  ```
  git clone https://gitlab.astro.rug.nl/prodimo/prodimopy.git
  ```    
 
* change into the newly created prodimopy directory and type:

  ```
  pip install -e . 
  ```

  If you do not have root access to install python packages, try this.

  ```
  pip install -e . --user
  ```

This will install the package in your current python environment (should be the one you want to use for ProDiMo). The `-e` options allows to update the python code (e.g. via git) without the need to reinstall the package. To update the code simply type

```
git pull 
```

in the prodimopy directory. You can directly use the updated code (no reinstall required).

