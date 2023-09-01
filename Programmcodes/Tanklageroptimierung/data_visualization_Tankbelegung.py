import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

Auswertung_final_f_ztr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\f_ztr.xlsx', header = 0)
Auswertung_final_a_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\auftaege_zr.xlsx', header = 0)


Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['value'] > 0]
Auswertung_final_f_ztr['Tank'] = Auswertung_final_f_ztr['Tank'].astype('category')
sns.scatterplot(data = Auswertung_final_f_ztr, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10, label = "Tankbelegungsentwicklung der Rohstoffe")
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_ylabel('Tank')
ax.set_xlabel('Zeit in 8 Stunden Intervallen')

"""plt.annotate('Tankreinigung', xy = (), xytext = (),
             arrowprops=dict(facecolor='black', arrowstyle='->'))"""

plt.show()

