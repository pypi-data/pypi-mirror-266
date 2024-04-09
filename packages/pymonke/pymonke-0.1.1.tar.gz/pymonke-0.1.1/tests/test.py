from pymonke import Fit, FitResult
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.axes import Axes
import numpy as np
from pymonke import transform_dataframe_to_latex_ready
from pymonke.misc.benchmark import timing, bench_compare
from pymonke.mmath.rounding import roundup
import math

from icecream import ic

from pymonke import TexTable
from pprint import pprint

from uncertainties import ufloat, ufloat_fromstr
from pymonke.misc.dataframe import separate_uncertainties, join_uncertainties

# data = pd.read_csv("Cu.csv")
# data["intensity error"] = [np.sqrt(i) * 2 if i != 0 else 0.01 for i in data["intensity"]]
# data["channel error"] = [np.sqrt(i) * 0.01 if i != 0 else 0.01 for i in data["intensity"]]
# data.to_csv("Cu.csv", index=False)
# # data = data[["intensity", "channel", "intensity error", "channel error"]]
# # data.to_csv("Cu.csv", index=False)
#
# #
# # data.query("channel > 100 and channel < 110", inplace=True)
#
#
# data["channel"] = [ufloat(x, err) for x, err in zip(data["channel"], data["channel error"])]
# data.drop("channel error", axis=1, inplace=True)
# data["intensity"] = [ufloat(x, err) for x, err in zip(data["intensity"], data["intensity error"])]
# data.drop("intensity error", axis=1, inplace=True)
# data["product"] = data["channel"] ** 2 * data["intensity"]
# data.to_csv("test.csv", index=False)



# converters = {
#     "intensity": ufloat_fromstr,
#     "channel": ufloat_fromstr,
#     "product": ufloat_fromstr,
# }
# data = pd.read_csv("test.csv", converters=converters)
# meta = json.loads(open("meta.json").read())
# # x = transform_dataframe_to_latex_ready(data, siunitx_column_option=options)
# print(data)
#
# fit = Fit(meta, data)
# out = fit.run()
# print(out["fit1"]["x1"])


#
# res = fit.get_results_as_dict()
# x = json.dumps(res, indent=2)
# with open("result.json", "w") as file:
#     file.write(x)
#
# ic(json.loads(x, cls=PyMonkeJSONDecoder))
