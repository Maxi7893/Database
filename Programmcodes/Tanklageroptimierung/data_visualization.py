import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import seaborn.objects as so

Auswertung_final = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\merged.xlsx', header = 0)
Auswertung_Nachfrage = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Nachfrage.xlsx', header = 0)


sns.set(style = "whitegrid")
fig, ax1 = plt.subplots()
sns.lineplot(data = Auswertung_final, x='Time', y='value', ax = ax1, label = 'Füllstände')
plt.xlim(left = 0)
ax1.yaxis.set_major_locator(plt.MaxNLocator(integer = True))

ax2 = ax1.twinx()

sns.barplot(data = Auswertung_Nachfrage, x = Auswertung_Nachfrage.iloc[:, 0], y = Auswertung_Nachfrage.iloc[:, 1], ax = ax2, lw = 0, palette = ['orange' for x in Auswertung_Nachfrage.iloc[:, 1]])
ax1.legend()
ax2.legend()

plt.xticks(Auswertung_final['Time'][::50], Auswertung_final['Time'][::50])
ax1.set_ylim(0)
ax2.set_ylim(0)


f"""plt.figure(figsize = (8, 2.5))
sns.scatterplot(data = Auswertung_a, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))"""
plt.show()


