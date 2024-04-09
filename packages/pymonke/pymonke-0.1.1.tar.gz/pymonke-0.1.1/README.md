# Monke
Monke is a python package with helpful tools for scientific reports and data analysis.

+ GitHub Page: https://github.com/GabrielRemi/pymonke

## Installation
```commandline
pip install pymonke
```
---
## Physical Constants 
```python
from pymonke import constants
```
This module contains a few common physical constants in SI units. 

| Symbol               | constant name             | value                           | unit                                |
|----------------------|---------------------------|---------------------------------|-------------------------------------|
| $ c $                | LIGHTSPEED                | $2.99792458 \cdot 10^8$         | $\mathrm{m/s}$                      |
| $e$                  | ELEMENTARY_CHARGE         | $1.602176634 \cdot 10^{-19}$    | $\mathrm{C}$                        |
| $\mu_0$              | VACUUM_PERMEABILITY       | $1.25663706212 \cdot 10^{-6}$   | $\mathrm{N \cdot A^{-2}}$           |
| $\varepsilon_0$      | VACUUM_PERMITTIVITY       | $8.8541878128 \cdot 10^{-12}$   | $\mathrm{F/m}$                      |
| $k_C$                | COULOMB_CONSTANT          | $8.9875517922 \cdot 10^9$       | $\mathrm{N \cdot m^2 \cdot C^{-2}}$ |
| $k_\mathrm{planck}$  | PLANCK_CONSTANT           | $6.62607015 \cdot 10^{-34}$     | $\mathrm{J \cdot s}$                |
| $G$                  | GRAVITATIONAL_CONSTANT    | $6.67430 \cdot 10^{-11}$        | $\mathrm{m^3/kg \cdot s^{-2}}$      |
| $m_\mathrm{planck}$  | PLANCK_MASS               | $2.176434 \cdot 10^{-8}$        | $\mathrm{kg}$                       |
| $l_\mathrm{planck}$  | PLANCK_LENGTH             | $1.616255 \cdot 10^{-35}$       | $\mathrm{m}$                        |
| $t_\mathrm{planck}$  | PLANCK_TIME               | $5.391247 \cdot 10^{-44}$       | $\mathrm{s}$                        |
| $T_\mathrm{planck}$  | PLANCK_TEMPERATURE        | $1.486784 \cdot 10^{32}$        | $\mathrm{K}$                        |
| $k_\mathrm{B} $      | BOLTZMANN_CONSTANT        | $1.380649 \cdot 10^{-23}$       | $\mathrm{J \cdot K^{-1}}$           |
| $\sigma$             | STEFAN_BOLTZMANN_CONSTANT | $5.670374419 \cdot 10^{-8}$     | $\mathrm{W/m^2 \cdot K^{-4}}$       |
| $m_\mathrm{e}$       | ELECTRON_MASS             | $9.1093837015 \cdot 10^{-31}$   | $\mathrm{kg}$                       |
| $\lambda_\mathrm{C}$ | COMPTON_WAVELENGTH        | $2.42631023867 \cdot 10^{-12}$  | $\mathrm{m}$                        |
| $r_\mathrm{e} $      | ELECTRON_RADIUS           | $2.8179403262 \cdot 10^{-15}$   | $\mathrm{m}$                        |
| $R_\infty $          | RYDBERG_CONSTANT          | $1.0973731568160 \cdot 10^7$    | $\mathrm{m^{-1}}$                   |
| $N_\mathrm{A}$       | AVOGADRO_CONSTANT         | $6.02214076 \cdot 10^{23}$      | $\mathrm{mol^{-1}}$                 |
| $R$                  | GAS_CONSTANT              | $8.31446261815324$              | $\mathrm{J/(mol \cdot K)}$          |
| $u$                  | ATOMIC_MASS               | $1.66053906660 \cdot 10^{-27}$  | $\mathrm{kg}$                       |
| $ \alpha$            | FINE_STRUCTURE_CONSTANT   | $7.2973525693 \cdot 10^{-3}$    | $\mathrm{}$                         |




---
## Using the latex features 
The `latex` package contains tools to create latex files out of data with little effort. For now, the 
only feature available is the ability to create latex tables. In order for this to work, the data 
has to be in the form of a pandas DataFrame. The most minimal code with which you can create 
a table looks something like that:

```python
from pandas import DataFrame
from pymonke.latex import TexTabular

data: DataFrame = DataFrame({
 "x": [1, 2, 3, 4],
 "x error": [0.12, 0.4, 0.42, 1],
 "something else": ["some", "other", "data", None],   
}) # create the data here

TexTabular(data=data, alignment="c|c").save("table.tex")
```
This code creates a file with the following content:

```latex
\begin{table}[htbp]
    \centering
    \caption{default Caption}
    \label{default Label}
    \begin{tabular}{c|c}
        x & something else \\
        \hline
        \tablenum{1.00 +- 0.12} & some \\
        \tablenum{2.0 +- 0.4} & other \\
        \tablenum{3.0 +- 0.5} & data \\
        \tablenum{4.0 +- 1.0} & -- \\
    \end{tabular}
\end{table}
```
Because the second column is named `x error`, it is automatically identified as the uncertainty of the first column.
There is more functionality available, like renaming the columns or adding options to the tablenum macro on a column
per column basis. In that case the last code line should be changed in the following way:
```python
tabular = TexTabular(alignment="c|c")
tabular.add_data(data=data, columns={"x":"Number"})
tabular.save("table.tex")
```

This code does the exact same like before, but also renames the column named `x` to `Number`. The `add_data()` method has 
additional keyword arguments for more functionality.
