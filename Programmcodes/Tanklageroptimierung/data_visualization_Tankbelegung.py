import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

Tankvisualisierung = 10
Rohstoffvisualisierung = 0


Auswertung_final_f_ztr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\f_ztr.xlsx', header = 0)
Auswertung_final_a_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\auftaege_zr.xlsx', header = 0)
Auswertung_final_s_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\s_zr.xlsx', header = 0)






Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['value'] > 0]
Auswertung_final_f_ztr['Tank'] = Auswertung_final_f_ztr['Tank'].astype('category')
sns.scatterplot(data = Auswertung_final_f_ztr, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
plt.show()


Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['Tank'] == Tankvisualisierung]
Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['Material'] == Rohstoffvisualisierung]
Auswertung_final_a_zr = Auswertung_final_a_zr.iloc[:, Rohstoffvisualisierung + 1]
print(Auswertung_final_f_ztr)
print(Auswertung_final_a_zr)

Auswertung_final_f_ztr.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\merged.xlsx')
Auswertung_final_a_zr.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Nachfrage.xlsx')




