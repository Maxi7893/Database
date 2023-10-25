import numpy as np
import pandas as pd
from datetime import date, timedelta

class AbpackerReader:
    Abpacker = pd.read_excel(r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Abpacker\Kalkulationen 2023.xlsx')
    print(Abpacker)

    print("Klappt!")