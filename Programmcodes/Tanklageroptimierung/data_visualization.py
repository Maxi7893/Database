import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn.objects as so


Auswertung_a = pd.read_excel(
    r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Tanklageroptimierung\Auswertung\Testversuche\Testversuch_a\u_ztr.xlsx', header = 0)
print(Auswertung_a)
Auswertung_a = Auswertung_a[Auswertung_a['value'] == 1]
Auswertung_a = Auswertung_a[Auswertung_a['Time'] > 0]
Auswertung_a['Tank'] = Auswertung_a['Tank'].astype('int')



plt.figure(figsize = (8, 2.5))
sns.scatterplot(data = Auswertung_a, x = 'Time', y = 'Tank', hue = 'Material', alpha = 0.2, palette = 'bright', marker = 's', s = 10)
plt.xlim(left = 0)
ax = plt.gca()
ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
plt.show()

