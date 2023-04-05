import csv
from decimal import *
import time
from datetime import date, timedelta, datetime

import numpy as np
import pandas as pd
from datetime import date, timedelta

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
    # region data implementation
    # rohstoffmapping
    rohstoffe = pd.read_excel(
        r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Tanklagerverbrauch mit neuer Belegung.xlsx')
    rohstoff_mapping = rohstoffe["E-Material"].unique()
    rohstoff_mapping = pd.DataFrame(rohstoff_mapping)
    rohstoff_mapping['r'] = rohstoff_mapping.index
    rohstoff_mapping.rename({0: "E-Material"}, axis=1, inplace=True)

    # region RohstoffkostenIBC/Abfallkosten
    rohstoffkosten = rohstoffe[["E-Material", "Kosten (KG für IBC)"]].fillna(0)
    rohstoffkosten = pd.merge(rohstoffkosten, rohstoff_mapping, how="inner").drop_duplicates()
    kosten_rohstoff_r: pd.DataFrame = rohstoffkosten[["Kosten (KG für IBC)"]].reset_index(drop=True)
    # endregion

    abfallkosten = rohstoffe[["E-Material", "Kosten (KG für Tank)"]].fillna(0)
    abfallkosten = pd.merge(abfallkosten, rohstoff_mapping, how="inner").drop_duplicates()
    kosten_abfall_r: pd.DataFrame = abfallkosten[["Kosten (KG für Tank)"]].reset_index(drop=True)

    # Reinigungskosten und Gebindegrößen einlesen
    reinigungskosten = rohstoffe[["E-Material", "Preis pro Gebinde"]].fillna(0)
    reinigungskosten = pd.merge(reinigungskosten, rohstoff_mapping, how="inner").drop_duplicates()
    reinigungskosten_r: pd.DataFrame = reinigungskosten[["Preis pro Gebinde"]].reset_index(drop=True)
    groessegebinde = rohstoffe[["E-Material", "Gebindegröße LOME"]].fillna(0)
    groessegebinde = pd.merge(groessegebinde, rohstoff_mapping, how="inner").drop_duplicates()
    groeßegebinde_r: pd.DataFrame = groessegebinde[["Gebindegröße LOME"]].reset_index(drop=True)

    # Kapazität Bahnkesselwagen inkl. Kosten
    kap_bahnkesselwagen = rohstoffe[
        ["E-Material", "Kapazität Bahnkesselwagen (m³)", 'Dichte (kg/m³)', 'Kosten (KG für Tank)']].fillna(0)
    kap_bahnkesselwagen['Kapazität (kg)'] = (
            kap_bahnkesselwagen["Kapazität Bahnkesselwagen (m³)"] * kap_bahnkesselwagen["Dichte (kg/m³)"])
    kap_bahnkesselwagen['Kosten (BW)'] = (
            kap_bahnkesselwagen['Kapazität (kg)'] * kap_bahnkesselwagen['Kosten (KG für Tank)'])
    kap_bahnkesselwagen = pd.merge(kap_bahnkesselwagen, rohstoff_mapping, how="inner").drop_duplicates()
    kap_bahnkesselwagen_r: pd.DataFrame = kap_bahnkesselwagen[['Kapazität (kg)']].reset_index(drop=True)
    bahnkesselwagen_kosten_r: pd.DataFrame = kap_bahnkesselwagen[['Kosten (BW)']].reset_index(drop=True)

    # Gplante Aufträge einlesen
    # Date = datetime.today()
    Date = '2023-03-25'  # Für den Test hier nur ein beispielhafter Tag
    Date = pd.to_datetime(Date)
    aufraege = rohstoffe[["E-Material", 'Komponentenmng.', 'Start']]
    aufraege['Start'] = (aufraege['Start'] - Date)
    aufraege['Start'] = aufraege['Start'] / np.timedelta64(1, 'h')
    aufraege = pd.merge(aufraege, rohstoff_mapping, how="inner")
    geplante_auftraege = aufraege[['r', 'Start', 'Komponentenmng.']]
    geplante_auftraege.sort_values(by='Start', inplace=True, ignore_index=True)
    geplante_auftraege['Start'] = geplante_auftraege['Start'].astype(int)
    z = geplante_auftraege['Start'][len(geplante_auftraege) - 1]
    r = len(reinigungskosten_r.to_numpy())
    geplante_auftraege_zr = np.full(shape=(z, r), dtype=float, fill_value=0.0)
    i = 0
    laenge = len(geplante_auftraege)
    while i < laenge:
        value = geplante_auftraege['Komponentenmng.'][i]
        rohstoff = geplante_auftraege['r'][i]
        beginn = geplante_auftraege['Start'][i] - 1
        geplante_auftraege_zr[beginn][rohstoff] += abs(value)
        i = i + 1

    # rohstoffdichte zuweisen
    tanks = pd.read_excel(
        r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx',
        sheet_name=0)
    tank_dichte = pd.DataFrame(tanks)
    tanks['Artikelnummer'] = tanks['Artikelnummer'].astype(str)
    tanks['Artikelnummer'] = tanks['Artikelnummer'].str[:-2]
    tanks['Ausgangsfüllstand'] = (tanks['Tankvolumen Vn  (m³)'] * tanks['Dichte (kg/m³)'])
    rohstoff_mapping['E-Material'] = rohstoff_mapping['E-Material'].astype(str)
    tanks.rename(columns={'Artikelnummer': "E-Material"}, inplace=True)
    tanks.drop(tanks.loc[tanks['Tank-Nr.'].str.contains('Neu') | tanks['Tank-Nr.'].str.contains('Alt') | tanks[
        'E-Material'].str.contains('n')].index, inplace=True)
    tank_mapping = tanks["Tank-Nr."].unique()
    tank_mapping = pd.DataFrame(tank_mapping)
    tank_mapping.rename({0: "Tank-Nr."}, axis=1, inplace=True)
    tank_mapping['t'] = tank_mapping.index

    rohstoff_dichte = pd.merge(tank_dichte, rohstoff_mapping, how="inner")
    rohstoff_dichte = rohstoff_dichte[['E-Material', 'Dichte (kg/m³)', 'r']]
    rohstoff_dichte.drop_duplicates(subset='E-Material', inplace=True)
    rohstoff_dichte.sort_values(by='r', inplace=True, ignore_index=True)
    # Anzahl Tanks inkl. initialer Tankfüllung
    ausgangszustand_tanks = pd.merge(tanks, rohstoff_mapping, how="inner")
    ausgangszustand_tanks: pd.DataFrame = ausgangszustand_tanks[["Tank-Nr.", "r", "Ausgangsfüllstand"]]
    ausgangszustand_tanks.sort_values(by='Tank-Nr.', inplace=True)
    ausgangszustand_tanks.reset_index(inplace=True, drop=True)
    t = len(ausgangszustand_tanks)
    ausgangszustand_tanks_tr = np.full(shape=(t, r), dtype=float, fill_value=0.0)
    i = 0
    while i < t:
        value = ausgangszustand_tanks['Ausgangsfüllstand'][i]
        rohstoff = ausgangszustand_tanks['r'][i]
        ausgangszustand_tanks_tr[i][rohstoff] += abs(value)
        i = i + 1
    # Maximale Füllmengen aller Alternativen in DataFrame
    tanklager_alt = pd.read_excel(
        r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx',
        sheet_name=3).fillna(0)
    tanklager_alt.iloc[:, 2:] = tanklager_alt.iloc[:, 2:].astype(int)
    tanklager_alt.rename(columns={'Artikelnummer': "E-Material"}, inplace=True)
    tanklager_alt['E-Material'] = tanklager_alt['E-Material'].astype(str)
    tanklager_alt = pd.merge(tanklager_alt, rohstoff_mapping, how="inner")
    tanklager_alt.drop(columns=['Lösemittel', 'E-Material'], inplace=True)
    tanklager_alt = pd.merge(tanklager_alt, tank_mapping, how="inner")
    tanklager_alt = pd.merge(tanks, tanklager_alt, left_on='Tank-Nr.', right_on='Tank-Nr.', how="inner")
    tanklager_alt: pd.DataFrame = tanklager_alt[["r", 't', 'Tankvolumen Vn  (m³)']]
    tanklager_alt = pd.merge(tanklager_alt, rohstoff_dichte, left_on='r', right_on='r', how="inner")
    tanklager_alt['Volumen für diesen Tank'] = (tanklager_alt['Tankvolumen Vn  (m³)'] * tanklager_alt['Dichte (kg/m³)'])
    alternativen_tanklager_tr = np.full(shape=(t, r), dtype=float, fill_value=0.0)
    i = 0
    laenge = len(tanklager_alt)
    while i < laenge:
        value = tanklager_alt['Volumen für diesen Tank'][i]
        alternate_tank = tanklager_alt['t'][i]
        material = tanklager_alt['r'][i]
        alternativen_tanklager_tr[alternate_tank][material] = value
        i = i + 1
    # endregion
    t = len(tanks)

    # array = np.ndarray(shape=(t, r), dtype=int)
    # array[5, 6] = 3000
    # TODO
    '''
    set index numpy geplante Aufträge / Geplante Aufträge anpassen
    Rohstoffkosten wieder auf Abhängigkeit des Rohstoffs anpassen!
    Abfallkosten wieder auf Abhängigkeit des Rohstoffes anpassen!
    '''

    LP(
        rohstoffkosten_r=kosten_rohstoff_r.values.flatten(),  # Rohstoffkosten pro KG
        abfallkosten_r=kosten_abfall_r.values.flatten(),  # Abfallkosten pro KG
        reinigungskosten_rohstoffgebinde_r=reinigungskosten_r.values.flatten(),
        kosten_tankreinigung=4000,
        kosten_bahnkesselwagen=300,
        kosten_gebinde_personal=200,
        kapazitaet_bahnkesselwagen_r=kap_bahnkesselwagen_r.values.flatten(),
        auftraege_zr=geplante_auftraege_zr,
        kosten_bahnkesselwagen_r=bahnkesselwagen_kosten_r.values.flatten(),  # gesamte Kosten für BKW
        maximale_fuellmengen_tr=alternativen_tanklager_tr,  # Maximale Füllmengen aller Kombinationen
        gebindegroessen_r=groeßegebinde_r.values.flatten(),
        initiale_tankfuellung_tr=ausgangszustand_tanks_tr,
        anzahl_zeitpunkte=z,  # TODO #Stundenweise
        anzahl_tanks=t,
        anzahl_rohstoffe=r,
        anzahl_zeitpunkte_tankfuellung=8,
        anzahl_zeitpunkte_reinigung=24,
    ).run()


if __name__ == '__main__':
    start = time.time()
    # run_recursion()
    run_lp()

    print('Gesamtzeit: {:5.3f}s'.format(time.time() - start))
