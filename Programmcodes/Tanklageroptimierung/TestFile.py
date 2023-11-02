import csv

import numpy as np
import pandas as pd
import seaborn as sns
from Tanklageroptimierung.data_reader import DataReader

b = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\b_ztr.xlsx', header = 0)

b.drop(b.loc[b['value'] < 0.2].index, inplace=True)
b.drop(columns=["Unnamed: 0"], inplace=True)


b.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\b_ztr_Simulation.xlsx')
