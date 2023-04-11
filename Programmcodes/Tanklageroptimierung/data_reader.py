import csv

import numpy as np
import pandas as pd


class DataReader:
    def __init__(self, raster_zeitschritte):
        self.raster_zeitschritte = raster_zeitschritte
        self.rohstoffe = pd.read_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung'
            r'\Simulation\Tanklagerverbrauch mit neuer Belegung.xlsx')

        self.rohstoff_mapping = self.__read_rohstoff_mapping()
        self.rohstoffkosten_r = self.__read_rohstoffkosten()  # pro KG
        self.abfallkosten_r = self.__read_abfallkosten()  # pro KG
        self.reinigungskosten_rohstoffgebinde_r = self.__read_reinigungskosten()

        self.anzahl_zeitpunkte = 0
        self.anzahl_tanks = 0
        self.anzahl_rohstoffe = len(self.rohstoffkosten_r)

        bahnkesselwagen = self.__read_bahnkesselwagen()
        self.kapazitaet_bahnkesselwagen_r = bahnkesselwagen[0]
        self.kosten_bahnkesselwagen_r = bahnkesselwagen[1]

        self.auftraege_zr = self.__read_auftraege()
        self.time_mapping = self._read_time_mapping()
        self.gebindegroessen_r = self.__read_gebinde_groesse()

        tanks = self.__read_tanks()
        self.maximale_fuellmengen_tr = tanks[0]  # Maximale Füllmengen aller Kombinationen
        self.initiale_tankfuellung_tr = tanks[1]

        # TODO
        '''
        set index numpy geplante Aufträge / Geplante Aufträge anpassen
        Rohstoffkosten wieder auf Abhängigkeit des Rohstoffs anpassen!
        Abfallkosten wieder auf Abhängigkeit des Rohstoffes anpassen!
        '''

    def __read_rohstoff_mapping(self) -> pd.DataFrame:
        rohstoff_mapping = pd.DataFrame(self.rohstoffe["E-Material"].unique())
        rohstoff_mapping['r'] = rohstoff_mapping.index
        rohstoff_mapping.rename({0: "E-Material"}, axis=1, inplace=True)
        return rohstoff_mapping

    def __read_rohstoffkosten(self) -> np.ndarray:
        rohstoffkosten = self.rohstoffe[["E-Material", "Kosten (KG für IBC)"]].fillna(0)
        rohstoffkosten = pd.merge(rohstoffkosten, self.rohstoff_mapping, how="inner").drop_duplicates()
        kosten_rohstoff_r: pd.DataFrame = rohstoffkosten[["Kosten (KG für IBC)"]].reset_index(drop=True)
        return kosten_rohstoff_r.values.flatten()

    def __read_abfallkosten(self) -> np.ndarray:
        abfallkosten = self.rohstoffe[["E-Material", "Kosten (KG für Tank)"]].fillna(0)
        abfallkosten = pd.merge(abfallkosten, self.rohstoff_mapping, how="inner").drop_duplicates()
        kosten_abfall_r: pd.DataFrame = abfallkosten[["Kosten (KG für Tank)"]].reset_index(drop=True)
        return kosten_abfall_r.values.flatten()

    def __read_reinigungskosten(self) -> np.ndarray:
        reinigungskosten = self.rohstoffe[["E-Material", "Preis pro Gebinde"]].fillna(0)
        reinigungskosten = pd.merge(reinigungskosten, self.rohstoff_mapping, how="inner").drop_duplicates()
        reinigungskosten_r: pd.DataFrame = reinigungskosten[["Preis pro Gebinde"]].reset_index(drop=True)
        return reinigungskosten_r.values.flatten()

    def __read_gebinde_groesse(self) -> np.ndarray:
        groesse_gebinde = self.rohstoffe[["E-Material", "Gebindegröße LOME"]].fillna(0)
        groesse_gebinde = pd.merge(groesse_gebinde, self.rohstoff_mapping, how="inner").drop_duplicates()
        groesse_gebinde_r: pd.DataFrame = groesse_gebinde[["Gebindegröße LOME"]].reset_index(drop=True)
        return groesse_gebinde_r.values.flatten()

    def __read_bahnkesselwagen(self) -> (np.ndarray, np.ndarray):
        bahnkesselwagen = self.rohstoffe[["E-Material",
                                          "Kapazität Bahnkesselwagen (m³)",
                                          'Dichte (kg/m³)',
                                          'Kosten (KG für Tank)']].fillna(0)

        bahnkesselwagen['Kapazität (kg)'] = (bahnkesselwagen["Kapazität Bahnkesselwagen (m³)"] *
                                             bahnkesselwagen["Dichte (kg/m³)"])

        bahnkesselwagen['Kosten (BW)'] = (bahnkesselwagen['Kapazität (kg)'] *
                                          bahnkesselwagen['Kosten (KG für Tank)'])

        kap_bahnkesselwagen = pd.merge(bahnkesselwagen, self.rohstoff_mapping, how="inner").drop_duplicates()
        kap_bahnkesselwagen_r: pd.DataFrame = kap_bahnkesselwagen[['Kapazität (kg)']].reset_index(drop=True)
        bahnkesselwagen_kosten_r: pd.DataFrame = kap_bahnkesselwagen[['Kosten (BW)']].reset_index(drop=True)

        return kap_bahnkesselwagen_r.values.flatten(), bahnkesselwagen_kosten_r.values.flatten()

    def __read_auftraege(self) -> np.ndarray:
        date = pd.to_datetime('2023-03-25')  # Für den Test hier nur ein beispielhafter Tag
        auftraege = self.rohstoffe[["E-Material", 'Komponentenmng.', 'Start']]
        auftraege['Start'] = (auftraege['Start'] - date) / np.timedelta64(1, 'h')
        auftraege = pd.merge(auftraege, self.rohstoff_mapping, how="inner")

        geplante_auftraege = auftraege[['r', 'Start', 'Komponentenmng.']]
        geplante_auftraege.sort_values(by='Start', inplace=True, ignore_index=True)
        geplante_auftraege['Start'] = geplante_auftraege['Start'].astype(int)

        self.anzahl_zeitpunkte = int(geplante_auftraege['Start'][len(geplante_auftraege) - 1] /
                                     self.raster_zeitschritte) + 1

        geplante_auftraege_zr = np.full(shape=(self.anzahl_zeitpunkte, self.anzahl_rohstoffe),
                                        dtype=float,
                                        fill_value=0.0)

        for i in range(len(geplante_auftraege)):
            value = geplante_auftraege['Komponentenmng.'][i]
            rohstoff = geplante_auftraege['r'][i]
            beginn = geplante_auftraege['Start'][i] - 1
            geplante_auftraege_zr[int(beginn / self.raster_zeitschritte)][rohstoff] += abs(value)

        return geplante_auftraege_zr

    def _read_time_mapping(self) -> np.ndarray:
        date = pd.to_datetime('2023-03-25')  # Für den Test hier nur ein beispielhafter Tag
        auftraege = self.rohstoffe[["E-Material", 'Komponentenmng.', 'Start']]
        auftraege['Start'] = (auftraege['Start'] - date) / np.timedelta64(1, 'h')
        auftraege = pd.merge(auftraege, self.rohstoff_mapping, how="inner")

        geplante_auftraege = auftraege[['r', 'Start', 'Komponentenmng.']]
        geplante_auftraege.sort_values(by='Start', inplace=True, ignore_index=True)
        geplante_auftraege['Start'] = geplante_auftraege['Start'].astype(int)

        anzahl_zeitpunkte = int(geplante_auftraege['Start'][len(geplante_auftraege) - 1] /
                                     self.raster_zeitschritte) + 1

        Initial_time = np.full(shape=(anzahl_zeitpunkte, 1),
                                        dtype=float,
                                        fill_value=0.0)
        for i in range(len(Initial_time)):
            Initial_time[i] = self.raster_zeitschritte*i
        Initial_time = pd.DataFrame(Initial_time)
        Initial_time.rename(columns={0:"Model Time"}, inplace=True)
        return Initial_time



    def __read_tanks(self) -> (np.ndarray, np.ndarray):
        tanks = pd.read_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx',
            sheet_name=0)

        tank_dichte = pd.DataFrame(tanks)
        tanks['Artikelnummer'] = tanks['Artikelnummer'].astype(str)
        tanks['Artikelnummer'] = tanks['Artikelnummer'].str[:-2]
        tanks['Ausgangsfüllstand'] = (tanks['Tankvolumen Vn  (m³)'] * tanks['Dichte (kg/m³)'])

        tanks.rename(columns={'Artikelnummer': "E-Material"}, inplace=True)
        tanks.drop(tanks.loc[tanks['Tank-Nr.'].str.contains('Neu') | tanks['Tank-Nr.'].str.contains('Alt') | tanks[
            'E-Material'].str.contains('n')].index, inplace=True)
        tank_mapping = tanks["Tank-Nr."].unique()
        tank_mapping = pd.DataFrame(tank_mapping)
        tank_mapping.rename({0: "Tank-Nr."}, axis=1, inplace=True)
        tank_mapping['t'] = tank_mapping.index

        self.rohstoff_mapping['E-Material'] = self.rohstoff_mapping['E-Material'].astype(str)
        rohstoff_dichte = pd.merge(tank_dichte, self.rohstoff_mapping, how="inner")
        rohstoff_dichte = rohstoff_dichte[['E-Material', 'Dichte (kg/m³)', 'r']]
        rohstoff_dichte.drop_duplicates(subset='E-Material', inplace=True)
        rohstoff_dichte.sort_values(by='r', inplace=True, ignore_index=True)

        # Anzahl Tanks incl. initialer Tankfüllung
        ausgangszustand_tanks = pd.merge(tanks, self.rohstoff_mapping, how="inner")
        ausgangszustand_tanks: pd.DataFrame = ausgangszustand_tanks[["Tank-Nr.", "r", "Ausgangsfüllstand"]]
        ausgangszustand_tanks.sort_values(by='Tank-Nr.', inplace=True)
        ausgangszustand_tanks.reset_index(inplace=True, drop=True)

        self.anzahl_tanks = len(ausgangszustand_tanks)
        ausgangszustand_tanks_tr = np.full(shape=(self.anzahl_tanks, self.anzahl_rohstoffe),
                                           dtype=float,
                                           fill_value=0.0)

        for i in range(self.anzahl_tanks):
            value = ausgangszustand_tanks['Ausgangsfüllstand'][i]
            rohstoff = ausgangszustand_tanks['r'][i]
            ausgangszustand_tanks_tr[i][rohstoff] += abs(value)

        # Maximale Füllmengen aller Alternativen in DataFrame
        tanklager_alt = pd.read_excel(
            r'C:\Users\Gruppeplansim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx',
            sheet_name=3).fillna(0)
        tanklager_alt.iloc[:, 2:] = tanklager_alt.iloc[:, 2:].astype(int)
        tanklager_alt.rename(columns={'Artikelnummer': "E-Material"}, inplace=True)
        tanklager_alt['E-Material'] = tanklager_alt['E-Material'].astype(str)
        tanklager_alt = pd.merge(tanklager_alt, self.rohstoff_mapping, how="inner")
        tanklager_alt.drop(columns=['Lösemittel', 'E-Material'], inplace=True)
        tanklager_alt = pd.merge(tanklager_alt, tank_mapping, how="inner")
        tanklager_alt = pd.merge(tanks, tanklager_alt, left_on='Tank-Nr.', right_on='Tank-Nr.', how="inner")
        tanklager_alt: pd.DataFrame = tanklager_alt[["r", 't', 'Tankvolumen Vn  (m³)']]
        tanklager_alt = pd.merge(tanklager_alt, rohstoff_dichte, left_on='r', right_on='r', how="inner")
        tanklager_alt['Volumen für diesen Tank'] = (tanklager_alt['Tankvolumen Vn  (m³)'] *
                                                    tanklager_alt['Dichte (kg/m³)'])

        alternativen_tanklager_tr = np.full(shape=(self.anzahl_tanks, self.anzahl_rohstoffe),
                                            dtype=float,
                                            fill_value=0.0)

        for i in range(len(tanklager_alt)):
            value = tanklager_alt['Volumen für diesen Tank'][i]
            alternate_tank = tanklager_alt['t'][i]
            material = tanklager_alt['r'][i]
            alternativen_tanklager_tr[alternate_tank][material] = value

        return alternativen_tanklager_tr, ausgangszustand_tanks_tr

    # region read data for recursion
    @staticmethod
    def einlesen() -> list:
        array = []
        first_row = True
        with open(r"Auftraege.csv") as file:
            csv_reader_object = csv.reader(file, delimiter=';')
            for row in csv_reader_object:
                if not first_row:
                    # noinspection PyTypeChecker
                    row[9] = int(row[9][5]) * 300 + int(row[9][6]) * 30 + int(row[9][8]) * 10 + int(row[9][9])
                    array.append([int(row[5]), float(row[6].replace(',', '.')), int(row[15]), row[9]])
                else:
                    first_row = False
        return array

    @staticmethod
    def einlesen_kann_in_tank() -> list:
        array = []
        with open(r"Tanklager.csv") as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                array.append(row)

        return array
    # endregion
