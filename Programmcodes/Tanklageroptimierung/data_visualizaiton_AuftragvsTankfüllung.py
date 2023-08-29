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


Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['Tank'] == Tankvisualisierung]
Auswertung_final_f_ztr = Auswertung_final_f_ztr[Auswertung_final_f_ztr['Material'] == Rohstoffvisualisierung]
Auswertung_final_a_zr = Auswertung_final_a_zr.iloc[:, Rohstoffvisualisierung + 1]

Auswertung_final_f_ztr.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Füllstand nach Tank_Rohstoff.xlsx')
Auswertung_final_a_zr.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Nachfrage.xlsx')


Auswertung_final = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Füllstand nach Tank_Rohstoff.xlsx', header = 0)
Auswertung_Nachfrage = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Nachfrage.xlsx', header = 0)


plot_label = 'Füllstände Tank ' + str(Tankvisualisierung) + ' mit Rohstoff ' + str(Rohstoffvisualisierung) + 'und Auftragsnachfrage von Rohstoff ' + str(Rohstoffvisualisierung)
sns.set(style = "whitegrid")
fig, ax1 = plt.subplots()
sns.lineplot(data = Auswertung_final, x='Time', y='value', ax = ax1, label = plot_label)
plt.xlim(left = 0)
ax1.yaxis.set_major_locator(plt.MaxNLocator(integer = True))

ax2 = ax1.twinx()

sns.barplot(data = Auswertung_Nachfrage, x = Auswertung_Nachfrage.iloc[:, 0], y = Auswertung_Nachfrage.iloc[:, 1], ax = ax2, lw = 0, palette = ['orange' for x in Auswertung_Nachfrage.iloc[:, 1]])
ax1.legend()
ax2.legend()

plt.xticks(Auswertung_final['Time'][::50], Auswertung_final['Time'][::50])
ax1.set_ylim(0)
ax2.set_ylim(0)
plt.show()

