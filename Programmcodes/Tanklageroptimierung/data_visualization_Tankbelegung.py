import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

#Laden der Daten
Auswertung_final_f_ztr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\f_ztr.xlsx', header = 0)
Auswertung_final_a_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\auftaege_zr.xlsx', header = 0)

#Datenaufbereitung
Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['value'] > 0]
Auswertung_final_f_ztr['Tank'] = Auswertung_final_f_ztr['Tank'].astype('category')
sns.scatterplot(data = Auswertung_final_f_ztr, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_ylabel('Tank')
ax.set_xlabel('Zeit in 8 Stunden Intervallen')
plt.yticks(Auswertung_final_f_ztr['Tank'][::1])
plt.title('Tankbelegungsentwicklung der Rohstoffe', y = 1.05)

#Mögliche Beschriftung mit Pfeilen
"""plt.annotate('Tankreinigung', xy = (), xytext = (), 
             arrowprops=dict(facecolor='black', arrowstyle='->'))"""

#Datenvisualisierung
#Achsengröße um 10% minimieren, um Platz für Legende zu schaffen
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

#Legende unter den Graph
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol = 6)

plt.show()
