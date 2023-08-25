import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

Rohstoffvisualisierung = 0

Auswertung_final_e_zr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\e_zr.xlsx', header = 0)
Auswertung_final_u_ztr = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\u_ztr.xlsx', header = 0)

Auswertung_final_u_ztr = Auswertung_final_u_ztr[Auswertung_final_u_ztr['Material'] == Rohstoffvisualisierung]
Auswertung_final_e_zr = Auswertung_final_e_zr[Auswertung_final_e_zr['Material'] == Rohstoffvisualisierung]

Stuckgutbenutzung = Auswertung_final_e_zr['value'].sum()
Tankbenutzung = Auswertung_final_u_ztr['value'].sum()

labels = 'Stuckgutbenutzung', 'Tankbenutzung'
sizes = [Stuckgutbenutzung, Tankbenutzung]

plt.title('Anteil Stuckgutbenutzung und Tankbenutzung Rohstoff ' + str(Rohstoffvisualisierung))
plt.pie(sizes, labels = labels, autopct = '%1.1f%%')
sns.set()
plt.axis('equal')
plt.show()

