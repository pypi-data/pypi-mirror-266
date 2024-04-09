import unittest

import pandas as pd

from src.pymonke.latex.tex_table import TexTable
from src.pymonke.latex.tex_tabular import TexTabular

# TODO table_test.py not up to date

class MyTestCase(unittest.TestCase):
    def test_base_table(self):
        string = r"""\begin{table}[htbp]
    \centering
    \caption{Tabelle}
    \label{tab:tabelle}
    \begin{tabular}{c|c}
        \toprule
        Zahl1 & Zahl2 \\
        \midrule
        \tablenum{1} & \tablenum{1.0} \\
        \tablenum{2} & \tablenum{2.0} \\
        \tablenum{3} &   \\
        \bottomrule
    \end{tabular}
\end{table}"""
        data = pd.DataFrame(data={
            "Zahl1": [1, 2, 3],
            "Zahl2": [1, 2, None],
        })
        table = TexTable(tabular=[TexTabular(data=data, alignment="c|c", caption="Tabelle", label="tab:tabelle",
                                             h_lines=[0, 1, 4], filler=" ", booktabs=True)])
        self.assertEqual(string, str(table))

    def errors(self):

        with self.assertRaises(ValueError):
            table = TexTable(tabular=[TexTabular(), TexTabular()], widths=[0.34])
            print(table)


if __name__ == '__main__':
    unittest.main()
