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
sns.scatterplot(data = Auswertung_final_f_ztr, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
ax.set_ylabel('Tank')
ax.set_xlabel('Zeit in 8 Stunden Intervallen')
plt.yticks(Auswertung_final_f_ztr['Tank'][::1])
plt.title('Tankbelegungsentwicklung der Rohstoffe', y = 1.05)

"""plt.annotate('Tankreinigung', xy = (), xytext = (), 
             arrowprops=dict(facecolor='black', arrowstyle='->'))"""

# Shrink current axis's height by 10% on the bottom
box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

# Put a legend below current axis
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol = 6)

plt.show()


import pandas as pd
import numpy as np

Daten_Montag = pd.read_excel(
    r'C:\Users\mb-itl-sim\PycharmProjects\Database\Programmcodes\Datenzusammenfassung\UL-17.10.2022', header = 0)
Daten_Dienstag = pd.read_excel(
    r'C:\Users\mb-itl-sim\PycharmProjects\Database\Programmcodes\Datenzusammenfassung\UL-18.10.2022', header = 0)
Daten_Mittwoch = pd.read_excel(
    r'C:\Users\mb-itl-sim\PycharmProjects\Database\Programmcodes\Datenzusammenfassung\UL-19.10.2022', header = 0)
Daten_Donnerstag = pd.read_excel(
    r'C:\Users\mb-itl-sim\PycharmProjects\Database\Programmcodes\Datenzusammenfassung\UL-20.10.2022', header = 0)
Daten_Freitag = pd.read_excel(
    r'C:\Users\mb-itl-sim\PycharmProjects\Database\Programmcodes\Datenzusammenfassung\UL-21.10.2022', header = 0)

print(Daten_Montag.shape)
print(Daten_Dienstag.shape)
print(Daten_Mittwoch.shape)
print(Daten_Donnerstag.shape)
print(Daten_Freitag.shape)

combined_df = pd.concat([Daten_Montag, Daten_Dienstag, Daten_Mittwoch, Daten_Donnerstag, Daten_Freitag], ignore_index = True)


print(combined_df)
print(combined_df.shape)
