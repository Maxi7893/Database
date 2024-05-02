import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

#Laden der Daten
Auswertung_final_u_ztr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\u_ztr.xlsx', header = 0)
Auswertung_final_a_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\auftaege_zr.xlsx', header = 0)

#Datenaufbereitung
Auswertung_final_u_ztr['value'] = Auswertung_final_u_ztr['value'].astype('float')
Auswertung_final_u_ztr = Auswertung_final_u_ztr[Auswertung_final_u_ztr['value'] > 0]
Auswertung_final_u_ztr['Tank'] = Auswertung_final_u_ztr['Tank'].astype('category')
plt.figure(figsize=(14, 4))
sns.scatterplot(data = Auswertung_final_u_ztr, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 50)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_ylabel('Tank', fontsize=12)
ax.set_xlabel('Time in 2 hour intervals', fontsize=12)
plt.title('Occupancy of the tanks', y = 1.05, fontsize=18)
# Set y-axis limits to adjust spacing
plt.ylim(-0.5, 1.5)

# Define custom y-axis ticks
custom_ticks = [0, 1]
plt.yticks(custom_ticks)

#Mögliche Beschriftung mit Pfeilen
"""plt.annotate('Tankreinigung', xy = (), xytext = (), 
             arrowprops=dict(facecolor='black', arrowstyle='->'))"""

#Datenvisualisierung
#Achsengröße um 10% minimieren, um Platz für Legende zu schaffen
ax.set_aspect(aspect=250)

box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

#Legende unter den Graph
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.4), title='Material', title_fontsize='large',
          fancybox=True, shadow=True, ncol = 6)


plt.show()
