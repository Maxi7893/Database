from decimal import *
import time

from Tanklageroptimierung.data_reader import DataReader
from Tanklageroptimierung.data_evaluation import DataEvaluation
from lp_2023_10_09 import LP

def run_lp():
    raster_zeitschritte = 8  # Summiere immer 8h Zeitfenster auf
    data = DataReader(raster_zeitschritte)
    #dataevaluation = DataEvaluation(raster_zeitschritte)
    #print(" ")
    print("Data analysis completed!")
    LP(
        rohstoffkosten_r=data.rohstoffkosten_r,  # pro KG
        abfallkosten_r=data.abfallkosten_r,  # pro KG
        reinigungskosten_rohstoffgebinde_r=data.reinigungskosten_rohstoffgebinde_r,
        kosten_tankreinigung= 6000, # 48 Stunden mit einem Stundensatz von 125€/h
        kosten_bahnkesselwagen= 750, # 6 Stunden mit einem Stundensatz von 125€/h #Auffüllen des Tanks
        # Auffüllen des Tanks Sandra Seebald bzgl. längere Standkosten fragen!
        # Materialende 0000 Kosten beinhalten Kosten des Einkaufs, Handling etc.
        # Materialende 8889/8888 Kosten beinhalten jetzt Abpackungen
        # Kosten Bahnkesselwagen schieben etc.
        # Kosten bei Gebinde für das Handling ist nicht drin!
        kosten_gebinde_personal= 32.50,  # Daten werden durch die Simulation bestimmt! #125€/h # 10 Minuten
        # Platzkosten IBC -> Im Werkslager: 20 € pro Monat
        kapazitaet_bahnkesselwagen_r=data.kapazitaet_bahnkesselwagen_r,
        auftraege_zr=data.auftraege_zr,
        kosten_bahnkesselwagen_r=data.kosten_bahnkesselwagen_r,  # gesamte Kosten für BKW
        maximale_fuellmengen_tr=data.maximale_fuellmengen_tr,  # Maximale Füllmengen aller Kombinationen
        gebindegroessen_r=data.gebindegroessen_r,
        initiale_tankfuellung_tr=data.initiale_tankfuellung_tr,
        anzahl_zeitpunkte=data.anzahl_zeitpunkte,  # TODO #Stundenweise
        anzahl_tanks=data.anzahl_tanks,
        anzahl_rohstoffe=data.anzahl_rohstoffe,
        anzahl_zeitpunkte_tankfuellung=int(8 / raster_zeitschritte),
        anzahl_zeitpunkte_reinigung=int(24 / raster_zeitschritte),
    ).run(time_limit=5000) # Zeitlimit in Minuten! 7000
    DataEvaluation(raster_zeitschritte)
    print(" ")
    print("Data analysis completed!")
    print(" ")


if __name__ == '__main__':
    start = time.time()
    # run_recursion()
    run_lp()

    print('Gesamtzeit: {:5.3f}s'.format(time.time() - start))
