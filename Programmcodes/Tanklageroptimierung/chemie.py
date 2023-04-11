from decimal import *
import time

from Tanklageroptimierung.data_reader import DataReader
from Tanklageroptimierung.data_evaluation import DataEvaluation
from lp import LP
from recursion import Recursion

getcontext().prec = 3500


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
    kann_in_tank = DataReader.einlesen_kann_in_tank()
    eingelesene_auftraege = DataReader.einlesen()

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
    raster_zeitschritte = 8  # Summiere immer 8h Zeitfenster auf

    data = DataReader(raster_zeitschritte)
    dataevaluation = DataEvaluation()

    LP(
        rohstoffkosten_r=data.rohstoffkosten_r,  # pro KG
        abfallkosten_r=data.abfallkosten_r,  # pro KG
        reinigungskosten_rohstoffgebinde_r=data.reinigungskosten_rohstoffgebinde_r,
        kosten_tankreinigung=4000,
        kosten_bahnkesselwagen=300,
        kosten_gebinde_personal=200,
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
    ).run(time_limit=3000) # Zeitlimit in Minuten!


if __name__ == '__main__':
    start = time.time()
    # run_recursion()
    run_lp()

    print('Gesamtzeit: {:5.3f}s'.format(time.time() - start))
