import csv
from decimal import *
import time

import numpy as np
import pandas as pd

from lp import LP
from recursion import Recursion

# ToDo
'''
kg nach liter
30 TageMonat nur Tag betrachtet
Fülle aktuell Tanks immer nur voll und fülle nur einen auf
unterschiedliche Kapazitäten
Abfälle
Alle Tanks einbinden
Gebinde-Preise
'''

getcontext().prec = 3500


# region read data
def einlesen() -> list:
    array = []
    first_row = True
    with open(r"Auftraege.csv") as file:
        csv_reader_object = csv.reader(file, delimiter=';')
        for row in csv_reader_object:
            if not first_row:
                row[9] = int(row[9][5]) * 300 + int(row[9][6]) * 30 + int(row[9][8]) * 10 + int(row[9][9])
                array.append([int(row[5]), float(row[6].replace(',', '.')), int(row[15]), row[9]])
            else:
                first_row = False
    return array


def einlesen_kann_in_tank() -> list:
    array = []
    with open(r"Tanklager.csv") as file:
        reader = csv.reader(file, delimiter=';')
        for row in reader:
            array.append(row)

    return array


# endregion

def run_recursion():
    anzahl_tanks = 30

    kapazitaet_tanks = [20, 20, 32, 0, 32, 32, 32, 32, 32, 0, 32, 32, 32, 32, 16,
                        16, 32, 16, 16, 32, 16, 16, 32, 32, 20, 30, 32, 32, 0, 32]

    # 1. welcher Stoff ist drin; 2. wie viel drin ist, 3. wann zuletzt genutzt
    tankbelegung_anfang = [[2801098888, 0, 0], [2801098888, 0, 0], [2813158888, 0, 0], [0, 0, 0], [2812718888, 0, 0],
                           [2762628888, 0, 0], [2800328888, 0, 0], [2789158888, 0, 0], [2800328888, 0, 0], [0, 0, 0],
                           [2713688888, 0, 0], [2800288888, 0, 0], [2800258888, 0, 0], [2713688888, 0, 0],
                           [2760978888, 0, 0], [2760978888, 0, 0], [2779230000, 0, 0],
                           [2719918888, 0, 0], [2719918888, 0, 0], [2812718888, 0, 0], [2762708888, 0, 0],
                           [2762708888, 0, 0], [2762708888, 0, 0], [2762628888, 0, 0], [2762628888, 0, 0],
                           [2762628888, 0, 0], [2813158888, 0, 0], [2817158888, 0, 0], [0, 0, 0],
                           [2760978888, 0, 0]]

    # Daten einlesen
    # 1. Material 2. Menge 3. Benötigte Einheiten 4. Startzeitpunkt(Tag)
    kann_in_tank = einlesen_kann_in_tank()
    eingelesene_auftraege = einlesen()

    for i in range(anzahl_tanks):
        kapazitaet_tanks[i] *= 1000
        tankbelegung_anfang[i][1] = kapazitaet_tanks[i]
        tankbelegung_anfang[i][1] = 0
        tankbelegung_anfang[i][2] = -99

    Recursion(
        auftraege=eingelesene_auftraege,
        tankbelegung_anfang=tankbelegung_anfang,
        endzeitpunkt=25,  # anzahl schritte max. 1526
        anzahl_tanks=anzahl_tanks,
        kann_in_tank=kann_in_tank,
        kapa_tanks=kapazitaet_tanks,
        abfallpreis_gebinde=250,
        kosten_nachladen=170,  # Kosten wenn Stoff schon im Tank
        kosten_tankreinigung=3000,
        kosten_abfallentsorgung=300,
        kosten_tankleerung_pro_einheit=1. / 300,
        reinigungszeit=25,
    ).run()



def run_lp():
    rohstoffe = pd.read_excel(
        r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Tanklagerverbrauch mit neuer Belegung.xlsx')
    rohstoff_mapping = rohstoffe["E-Material"].unique()
    rohstoff_mapping = pd.DataFrame(rohstoff_mapping)
    rohstoff_mapping['r'] = rohstoff_mapping.index
    rohstoff_mapping.rename({0: "E-Material"}, axis=1, inplace=True)
    reinigungskosten = rohstoffe[["E-Material", "Preis pro Gebinde"]].fillna(0)
    reinigungskosten = pd.merge(reinigungskosten, rohstoff_mapping, how="inner").drop_duplicates()
    reinigungskosten_r: pd.DataFrame = reinigungskosten[["Preis pro Gebinde"]].reset_index(drop=True)
    kap_bahnkesselwagen = rohstoffe[["E-Material", "Kapazität Bahnkesselwagen (m³)",'Dichte (kg/m³)']].fillna(0)
    kap_bahnkesselwagen['Kapazität (kg)'] = (kap_bahnkesselwagen["Kapazität Bahnkesselwagen (m³)"]*kap_bahnkesselwagen["Dichte (kg/m³)"])
    kap_bahnkesselwagen =  pd.merge(kap_bahnkesselwagen, rohstoff_mapping, how="inner").drop_duplicates()
    kap_bahnkesselwagen_r : pd.DataFrame = kap_bahnkesselwagen[['Kapazität (kg)']].reset_index(drop=True)

    LP(
        rohstoffkosten=300,
        abfallkosten=250,
        reinigungskosten_rohstoffgebinde_r=reinigungskosten_r.to_numpy(),
        kosten_tankreinigung=4000,
        kapazitaet_bahnkesselwagen_r=kap_bahnkesselwagen_r.to_numpy(),
        auftraege_zr=None,
        kosten_bahnkesselwagen_r=None,
        maximale_fuellmengen_tr=None,
        gebindegroessen_r=None,
        initiale_tankfuellung_tr=None,
        anzahl_zeitpunkte=25,  # TODO
        anzahl_tanks=30,
        anzahl_rohstoffe=len(reinigungskosten_r.to_numpy()),
        anzahl_zeitpunkte_tankfuellung=8,
        anzahl_zeitpunkte_reinigung=24,
        anteil_bahnkesselwagen_tr=None
        #Moeglichkeiten der Befüllung?
    ).run()


if __name__ == '__main__':
    start = time.time()
    # run_recursion()
    run_lp()

    print('Gesamtzeit: {:5.3f}s'.format(time.time() - start))
