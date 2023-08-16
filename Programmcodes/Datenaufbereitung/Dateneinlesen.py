import numpy as np
import pandas as pd
from datetime import date, timedelta
# Produktionstermine werden eingelesen
a = 10  # Länge der Materialnummern
b = 0  # Anzahl der Ziffern die aus der Materialnummer entfernt werden (Bspw. 7777)
c = 1  # Wie viele Nachkommastellen bei den Startterminen entfernt werden sollen
Date = '2023-03-25' #Für den Test hier nur ein beispielhafter Tag
Date = pd.to_datetime(Date) #Zeile 9 und 10 können hinterher gelöscht werden und Zeile 11 aktiviert
#Date = date.today()  # Aktueller Tag wird gespeichert
# NextDate = Date + timedelta(days=14) #In den nächsten 14 Tagen wird geschaut, was ansteht
NextDate = Date + timedelta(days=280)
# Starttermine Produktionsaufträge G20
Starttermine = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Starttermine G20 - 2023.xlsx')  # Einlesen der Excel Liste für die Produktionstermine
Starttermine['Gebäude'] = "G20"
Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str.replace('.', '')  # Punkte aus der Materialnummer entfernen
if b > 0:
    Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str[
                               :-b]  # hier werden die Materialnummern um die letzten Ziffern gekürzt
Starttermine.rename(columns={'Offene Menge': 'Menge', 'Beginn (terminiert)': 'Start', 'Ende (terminiert)': 'Ende',
                             'Produktionsmengeneinheit': 'Me'}, inplace=True)
Starttermine.set_index(['Start'], inplace=True)  # Index setzen
# Hier noch alle löschen, die Zulässig eingeplant FALSE haben
Starttermine.drop(columns=['Ansatznummer',
                           'Status',
                           'Farbe',
                           'Rezept',
                           'Fertigungsversion',
                           'Zulässig eingeplant',
                           'Ursprüngliches Ende',
                           'Material Verfügbar',
                           'Langtext',
                           'Kampagnen-ID',
                           'ATP einstufig (%)',
                           'ATP Hauptkomponente (dynamisch)',
                           'ATP Restliche Materialien (dynamisch)',
                           'FMAT',
                           'MABS',
                           'Disponent',
                           'Fertigungssteuerer Mat.stamm',
                           'Fertigungssteuerer Pr-Auf',
                           'Hersteller',
                           'Hersteller Pr-Auf',
                           'Hersteller Mat.stamm',
                           'Kommentar',
                           'Tage - Reichweite',
                           'Auftragsart',
                           'Werk',
                           'Lagerort',
                           'Erstellungsdatum im ERP-System',
                           'Erstellt von',
                           'Änderungsdatum im ERP-System',
                           'Geändert von'], inplace=True)
Starttermine = Starttermine.sort_values(by='Start')  # Index nach Datum sortieren

Next = Starttermine[Date:NextDate]  # Filtern des Betrachtungszeitraums!
# Starttermine Produktionsaufträge G1
Starttermine = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Produktion_G1.xlsx',
    header=1)  # Einlesen der Excel-Liste G1'
Starttermine['Gebäude'] = "G1"
Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str.replace('.', '')  # Punkte aus der Materialnummer entfernen
if b > 0:
    Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str[
                               :-b]  # hier werden die Materialnummern um die letzten Ziffern gekürzt
Starttermine.rename(columns={'Anfo': 'Auftrags-Nr.', 'EH': 'Me'}, inplace=True)
Starttermine.drop(columns=['Status',
                           'Dispo',
                           'FS',
                           'Hersteller'], inplace=True)
Starttermine.set_index(['Start'], inplace=True)  # Index setzen
Starttermine = Starttermine.sort_values(by='Start')
Next2 = Starttermine[Date:NextDate]

# Startlisten zusammenführen
Next = Next.reset_index()
Next2 = Next2.reset_index()
Next = pd.merge(Next, Next2, how='outer')
Next.sort_values(by='Start', inplace=True)
Next.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Nächsten Produktionstermine.xlsx')

# Stücklisten werden eingelesen
List1 = pd.read_csv(r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\STUELI_EL-DOD-4.TXT',
                    names=['Werk',
                           'Material',
                           'Al',
                           'Kurztext',
                           'Basismenge',
                           'Me',
                           'Mart',
                           'Ss',
                           'Pos.',
                           'E-Material',
                           'Prodh.',
                           'P',
                           'Komponentenmng.',
                           'Me2',
                           'Kurztext2',
                           'Losgr.von',
                           'Losgr.bis',
                           'Fev',
                           'Dis',
                           'Lab'], sep='#', encoding='windows-1252')  # Einlseen der txt und encoding
List2 = pd.read_csv(r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Stückliste G1.TXT',
                    names=['Werk',
                           'Material',
                           'Al',
                           'Kurztext',
                           'Basismenge',
                           'Me',
                           'Mart',
                           'Ss',
                           'Pos.',
                           'E-Material',
                           'Prodh.',
                           'P',
                           'Komponentenmng.',
                           'Me2',
                           'Kurztext2',
                           'Losgr.von',
                           'Losgr.bis',
                           'Fev',
                           'Dis',
                           'Lab'], sep='#', encoding='windows-1252')  # Einlseen der txt und encoding
List2 = List2.dropna(subset=['Kurztext'])  # Hier werden die deleted entfernt

#List1['Gebäude'] = "G20"
#List1.drop(labels=0, axis=0, inplace=True)
#List2["Gebäude"] = "G1"
#List2.drop(labels=0, axis=0, inplace=True)
List = pd.merge(List1, List2, how='outer')  # Die beiden Stücklisten werden zusammengefügt
Stueli = pd.DataFrame(List)
Stueli.drop(labels=0, axis=0, inplace=True)  # hier wird die erste Zeile gedropt
Stueli.drop(columns=['Werk',
                     'Ss',
                     'P',
                     'Losgr.von',
                     'Losgr.bis',
                     'Dis',
                     'Lab'], inplace=True)  # hier werden alle unwichtigen Spalten gelöscht
if b > 0:
    Stueli['Material'] = Stueli['Material'].str[:-b]  # hier werden die Materialnummern um die letzten Ziffern gekürzt
    Stueli['E-Material'] = Stueli['E-Material'].str[:-b]
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace('.', '')  # Punkte aus der Basismenge entfernen
# Stueli['Material'] = Stueli['Material'].astype(int) #Datentyp verändern
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('.', '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(',', '.')
Stueli['Negativ'] = 1
Stueli.loc[Stueli['Komponentenmng.'].str.contains(
    '-'), 'Negativ'] = -1  # Sobald negative Werte vorliegen werden diese gekennzeichnet
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('-',
                                                                  '')  # Die Bindestriche (negativ-Zeichen) werden entfernt
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(' ', '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('null', '0')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].astype(float)  # Mengen werden zu einem Float
Stueli['Basismenge'] = Stueli['Basismenge'].str[:-4]  # Hier werden die Basismengen bis zu dem Komma gekürzt
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace(',',
                                                        '')  # Hier werden die Kommas aus der Mengeneinheit entfernt
Stueli['Basismenge'] = Stueli['Basismenge'].astype(float)  # Basismengen werden zu einem Float umgewandelt
Stueli['Al'] = Stueli['Al'].astype(float)
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'] * Stueli['Negativ']  # Negative Mengen sind jetzt kein String mehr
Stueli.drop(columns='Negativ', inplace=True)  # Die erstelte Spalte wieder entfernt
# Stueli['Rohstoff'] = (Stueli['Komponentenmng.'] > 0) & (Stueli['Me2'].str.contains('KG'))
indexNames = Stueli[(Stueli['Me2'].str.contains(
    'ST'))].index  # Hier wird die Indexnummer gespeichert, welche alle der Einheit Stück angehören
# indexNames =  Stueli[(Stueli['Komponentenmng.'] < 0) | (Stueli['Me2'].str.contains('ST'))].index #Hier wird die Indexnummer gespeichert, welche alle Mengen negativ sind oder der Einheit Stück angehören
FS = pd.DataFrame(Stueli)  # Es wird ein neues DataFrame iniziert
FS.drop(indexNames, inplace=True)  # Es werden alle Abfälle und Stückmengen entfernt
FS.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Stücklisten.xlsx')
# Hier wird die Häufigkeit ermittelt
data = Next['Mat.-Nr.']
data = data.reset_index()
# data.drop(columns='Start',inplace=True)
data.drop(columns='index', inplace=True)
Häufigkeit = pd.Series(data['Mat.-Nr.'])
Häufigkeit = Häufigkeit.value_counts(sort=False)
# Hier wird berechnet, wie oft die Rohstoffe benötigt werden
data = Häufigkeit.to_frame()
data = Häufigkeit.reset_index()
data.columns = ['Mat.-Nr.', 'Häufigkeit']
AnzahlPro = len(data)
i = 0
Auftragsnummer = data['Mat.-Nr.'][i]
Häufigkeit = data['Häufigkeit'][i]
FS['Häufigkeit'] = 0
while i < AnzahlPro:  # Hier wird die Häufigkeit der Produkte in den nächsten zwei Wochen in die Liste eingepflegt
    FS.loc[(FS['Material'] == Auftragsnummer), 'Häufigkeit'] = Häufigkeit
    i = i + 1
    if i < AnzahlPro:
        Auftragsnummer = data['Mat.-Nr.'][i]
        Häufigkeit = data['Häufigkeit'][i]
# Hier werden die benötigten Rohstoffe ausgelesen
Aufträge = len(Next)
i = 0
FS['Mengen- und Materialübereinstimmung'] = False
FS['Materialübereinstimmung'] = False
Materialnummer = Next['Mat.-Nr.'][i]
Menge = Next['Menge'][i]
Auftragsnummer = Next['Auftrags-Nr.'][i]
df = pd.DataFrame
while i < Aufträge:
    FS.loc[(FS['Material'] == Materialnummer) & (FS[
                                                     'Basismenge'] == Menge), 'Mengen- und Materialübereinstimmung'] = True  # Stimmen Mengen und Materialnummer überein
    FS.loc[(FS['Material'] == Materialnummer) & (FS['Basismenge'] == Menge), 'Materialübereinstimmung'] = True
    FS.loc[(FS['Material'] == Materialnummer) & (FS[
                                                     'Basismenge'] != Menge), 'Materialübereinstimmung'] = True  # Stimmen Mengen und Materialnummern nicht überein
    i = i + 1
    if i < Aufträge:
        Materialnummer = Next['Mat.-Nr.'][i]
        Menge = Next['Menge'][i]
        Auftragsnummer = Next['Auftrags-Nr.'][i]
BR = FS.loc[(FS['Mengen- und Materialübereinstimmung'] == True)]
# Hier jetzt kontrollieren, ob es Aufträge gibt, die zwar gefertigt werden müssen aber noch nicht in BR sind!
Test = FS.loc[(FS['Materialübereinstimmung'] == True) & (FS['Mengen- und Materialübereinstimmung'] == False)]
Test = Test.append({'Material': '1220', 'Al': 1235, 'Kurztext': 'Test', 'Basismenge': 1000, 'Me': 'KG'},
                   ignore_index=True)  # Testobjekt
Test['Vorhanden'] = False
Test = Test.reset_index()
Test.drop(columns=['index'], inplace=True)
Länge = len(BR)
i = 0
BR = BR.reset_index()
BR.drop(columns=['index'], inplace=True)
Materialnummer = BR['Material'][i]
while i < Länge:
    Test.loc[(Test['Material'] == Materialnummer), 'Vorhanden'] = True
    i = i + 1
    if i < Länge:
        Materialnummer = BR['Material'][i]
Test = Test[Test['Vorhanden'] == False]
BR = pd.merge(BR, Test,
              how='outer')  # Hier werden die Materialien hinzugefügt, welche noch nicht in der Liste sind und wo die Menge nicht übereinstimmt!

# Hier wird eine Kontroll-Liste erstellt
Kontrolle = BR[
    'Material']  # Beinhaltet die Materialnummer derer Aufträge, bei welcher die Menge mit der Stückliste übereinstimmt
Kontrolle = pd.Series(Kontrolle)
Kontrolle = Kontrolle.value_counts(sort=False)
Kontrolle = Kontrolle.to_frame()
Kontrolle = Kontrolle.reset_index()
Kontrolle.columns = ['Mat.-Nr.', 'Häufigkeit']
Kontrolle.drop(columns=['Häufigkeit'], inplace=True)
# In dem DataFrame Kontrolle sind nun alle Materialien, welche mit der Menge aus der Stückliste ebenfalls übereinstimmen

# Alle Materialien, die nicht in dem DataFraume vorkommen werden gefiltert, sodass jeweils nur noch ein Rezept übrig bleibt
Länge = len(Kontrolle)
BR['Duplikat'] = True
i = 0
BestAl = BR.set_index(['Material'])
Materialnummer = Kontrolle['Mat.-Nr.'][i]
while i < Länge:
    Al = BestAl['Al'][Materialnummer]  # Al 1 nehmen oder höher, falls nicht nur Materialübereinstimmung ist
    Te = Al.min(axis=0)
    BR.loc[(BR['Material'] == Materialnummer) & (BR['Al'] == Te), 'Duplikat'] = False
    i = i + 1
    if i < Länge:
        Materialnummer = Kontrolle['Mat.-Nr.'][i]
BR = BR[BR['Duplikat'] == False]

# Achtung! Stimmen die Mengen-Rezeptverhältnisse?
Länge = len(Next)
i = 0
Auftragsnummer = Next['Auftrags-Nr.'][i]
Materialnummer = Next['Mat.-Nr.'][i]
Materialmenge = Next['Menge'][i]
Start = Next['Start'][i]
BR['Test'] = False
BR['Start'] = pd.to_datetime('1900-01-01')
BR['Auftragsnummer'] = 0
while i < Länge:
    BR.loc[(BR['Material'] == Materialnummer), 'Test'] = True  # Es werden alle Materialien des Auftrags gekennzeichnet
    BR.loc[(BR['Material'] == Materialnummer), 'Start'] = Start
    BR.loc[(BR['Material'] == Materialnummer), 'Auftragsnummer'] = Auftragsnummer
    TempDB = BR[BR['Test'] == True]
    if i == 0:
        Forecast = TempDB
    else:
        Forecast = pd.merge(Forecast, TempDB, how='outer')
    i = i + 1
    BR['Test'] = False  # Hier wird die Kontrollinstanz wieder auf False gesetzt
    if i < Länge:
        Materialnummer = Next['Mat.-Nr.'][i]
        Auftragsnummer = Next['Auftrags-Nr.'][i]
        Start = Next['Start'][i]

BR = Forecast

# Hier werden die Rezepte angepasst, bei denen die Menge nicht übereinstimmt
Länge = len(Next)
i = 0
Auftragsnummer = Next['Auftrags-Nr.'][i]
Materialmenge = Next['Menge'][i]
Start = Next['Start'][i]
BR['Auftragsmenge'] = 0  # Nur Kontrolle, kann gelöscht werden
while i < Länge:
    BR.loc[(BR['Auftragsnummer'] == Auftragsnummer), 'Auftragsmenge'] = Materialmenge
    i = i + 1
    if i < Länge:
        Auftragsnummer = Next['Auftrags-Nr.'][i]
        Materialmenge = Next['Menge'][i]
# Hier wird der Umrechungsfaktor angewandt
BR['Hinweis'] = ''
BR['Umrechnungsfaktor'] = (BR['Auftragsmenge'] / BR['Basismenge'])
BR.loc[(BR['Umrechnungsfaktor'] != 1), 'Hinweis'] = 'Achtung, die Mengen stimmten nicht mit der Stückliste überein'
# Wenn Auftragsmenge und Umrechnungsfakotr nicht übereinstimmen noch mal eine Kontrolle, ob es auch wirklich kein Rezept gibt!
Länge = len(BR)
i = 0
Auftragsnummer = Next['Auftrags-Nr.'][i]
Materialnummer = Next['Mat.-Nr.'][i]
Materialmenge = Next['Menge'][i]
Start = Next['Start'][i]
BR['Vorhanden'] = BR['Vorhanden'].astype(bool)
BR['2nd_Check'] = False
while i < Länge:
    if ((BR['Hinweis'][i] != '') & (BR['Mengen- und Materialübereinstimmung'][i] == True)):
        BR['2nd_Check'][i] = True
    i = i + 1
Unstimmigkeiten = BR[
    BR['2nd_Check'] == True]  # Hier befinden sich alle Materialien, welchen ein falsches Rezept zugeordnet wurde
BR = BR[BR['2nd_Check'] == False]
FS = FS.reset_index(drop=True)

if (len(Unstimmigkeiten) > 0):
    # Hier wird vorab geprüft, ob es diese Auftragsmenge in der Stückliste überhaupt gibt. Wenn nicht, dann werden diese mit dem Umrechungsfaktor wieder in die normale Liste hinzugefügt!
    Länge = len(FS)
    i = 0  # Da der Index bei FS hier bei 1 erst anfängt! Bitte kontrollieren!
    Materialnummer = FS['Material'][i]
    Basismenge = FS['Basismenge'][i]
    Unstimmigkeiten['3rd_Check'] = False
    while i < Länge:
        Unstimmigkeiten.loc[(Unstimmigkeiten['Material'] == Materialnummer) & (Unstimmigkeiten[
                                                                                   'Auftragsmenge'] == Basismenge), '3rd_Check'] = True  # Wenn True, dann gibt es das Rezept ansonsten wieder in BR einfügen!
        i = i + 1
        if i < Länge:
            Materialnummer = FS['Material'][i]
            Basismenge = FS['Basismenge'][i]
    TestErfolglos = Unstimmigkeiten[Unstimmigkeiten['3rd_Check'] == False]
    TestErfolglos.drop(columns=['3rd_Check'], inplace=True)
    BR = pd.merge(BR, TestErfolglos,
                  how='outer')  # Alle Aufträge inkl. Materalien, welche es mit der Baismenge nicht in der Stücklliste gibt wurden wieder hinzugefügt!
    Unstimmigkeiten = Unstimmigkeiten[Unstimmigkeiten['3rd_Check'] == True]
    Unstimmigkeiten.drop(columns=['3rd_Check'], inplace=True)
    print('Es muss angepackt werden!')
    # Jetzt werden alle Auftragsnummern aus der Liste gezogen
    Auftragsnummern = Unstimmigkeiten[['Auftragsnummer', 'Material', 'Auftragsmenge',
                                       'Start']]  # Beinhaltet die Auftragsnummern, Materialnummern und die Auftragsmenge
    Auftragsnummern.drop_duplicates(subset=['Auftragsnummer'], inplace=True)  # Hier noch Duplikate entfernen
    Auftragsnummern = Auftragsnummern.reset_index(drop=True)  # Der Index wird zurückgesetzt
    KL = FS  # Neues Dataframe für die Stückliste wird erstellt
    # Hier jetzt die Rohstoffe raussuchen und entfernen, falls es mir Al-Probleme gibt!
    Länge = len(Auftragsnummern)
    i = 0
    KL['Mengen- und Materialübereinstimmung'] = False
    Materialnummer = Auftragsnummern['Material'][i]
    Menge = Auftragsnummern['Auftragsmenge'][i]
    while i < Länge:
        KL.loc[(KL['Material'] == Materialnummer) & (
                    KL['Basismenge'] == Menge), 'Mengen- und Materialübereinstimmung'] = True
        i = i + 1
        if i < Länge:
            Materialnummer = Auftragsnummern['Material'][i]
            Menge = Auftragsnummern['Auftragsmenge'][i]
    # Hier müssen jetzt die Materialien aus der Liste gesucht werden!
    Unstimmigkeiten = KL[KL[
                             'Mengen- und Materialübereinstimmung'] == True]  # Hier sind alle Rezepte enthalten. Nächster Schritt Al überprüfung!
    # Hier werden jetzt die Aufträge und Rezepte miteinander kombiniert
    Länge = len(Auftragsnummern)
    i = 0
    Auftragsnummer = Auftragsnummern['Auftragsnummer'][i]
    Materialnummer = Auftragsnummern['Material'][i]
    Materialmenge = Auftragsnummern['Auftragsmenge'][i]
    Start = Auftragsnummern['Start'][i]
    Unstimmigkeiten['Test'] = False
    Unstimmigkeiten['Start'] = pd.to_datetime('1900-01-01')
    Unstimmigkeiten['Auftragsnummer'] = 0
    Unstimmigkeiten['Auftragsmenge'] = 0
    while i < Länge:
        Unstimmigkeiten.loc[(Unstimmigkeiten[
                                 'Material'] == Materialnummer), 'Test'] = True  # Es werden alle Materialien des Auftrags gekennzeichnet
        Unstimmigkeiten.loc[(Unstimmigkeiten['Material'] == Materialnummer), 'Start'] = Start
        Unstimmigkeiten.loc[(Unstimmigkeiten['Material'] == Materialnummer), 'Auftragsnummer'] = Auftragsnummer
        Unstimmigkeiten.loc[(Unstimmigkeiten['Material'] == Materialnummer), 'Auftragsmenge'] = Materialmenge
        TempDB = Unstimmigkeiten[Unstimmigkeiten['Test'] == True]
        if i == 0:
            Forecast = TempDB
        else:
            Forecast = pd.merge(Forecast, TempDB, how='outer')
        i = i + 1
        Unstimmigkeiten['Test'] = False  # Hier wird die Kontrollinstanz wieder auf False gesetzt
        if i < Länge:
            Auftragsnummer = Auftragsnummern['Auftragsnummer'][i]
            Materialnummer = Auftragsnummern['Material'][i]
            Materialmenge = Auftragsnummern['Auftragsmenge'][i]
            Start = Auftragsnummern['Start'][i]
    Forecast['Hinweis'] = ''
    Forecast['Umrechnungsfaktor'] = (Forecast['Auftragsmenge'] / Forecast['Basismenge'])
    Forecast.loc[(Forecast[
                      'Umrechnungsfaktor'] != 1), 'Hinweis'] = 'Achtung, die Mengen stimmten nicht mit der Stückliste überein'
    BR = pd.merge(BR, Forecast, how='outer')

BR['Komponentenmng.'] = (BR['Komponentenmng.'] * BR['Umrechnungsfaktor'])
BR['Basismenge'] = BR['Auftragsmenge']
BR.drop(columns=['Al',
                 'Mart',
                 'Pos.',
                 'Fev',
                 'Auftragsmenge',
                 'Umrechnungsfaktor',
                 '2nd_Check'], inplace=True)  # hier werden alle unwichtigen Spalten gelöscht
# Abpacker werden eingelesen
Abpacker = pd.read_excel(r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Abpacker.xlsx',
                         sheet_name=1)  # Abpacker werden aus der Excel-Liste eingelesen
Abpacker.drop(columns=['auch GMP-Abpackungen?',
                       'PSA K16',
                       'Gruppen-BA',
                       'PSA-Schutzstufe nach GloveBox',
                       'PSA-Schutzstufe nach GloveBag',
                       'Kommentar ',
                       'SADT'], inplace=True)  # Unwichtige Spalten werden gelöscht
Abpacker['APN'] = Abpacker['APN'].astype(str)  # Materialnummern der Abpacker werden zu einem String
if b > 0:
    Abpacker['APN'] = Abpacker['APN'].str[:-b]  # Die letzten Ziffern werden entfernt, wenn die Bedingung erfüllt wird

# Abpackgebinde werden eingelesen
Abpackergebinde = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\MARA_G1_G20_Gebinde.xlsx')
Abpackergebinde = Abpackergebinde.iloc[1:]
Abpackergebinde.drop_duplicates(subset=['Materialnummer'], inplace=True)  # Hier noch Duplikate entfernen
Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str.replace('.', '')
if b > 0:
    Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str[
                                        :-b]  # die letzten Ziffern werden entfernt
# Kosten für die Reinigung der Abpackgebinde werden eingelesen
Reinigungskosten = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Kosten_Reinigung_Gebinde.xlsx')
Reinigungskosten.drop(columns=['Materialnummer',
                               'Base UOM',
                               'Kennzeichen für Temperaturbedingung',
                               'Kennzeichen Lose Menge',
                               'Gebindegröße LOME',
                               'Häufigkeit'], inplace=True)
Abpackergebinde = pd.merge(Abpackergebinde, Reinigungskosten, left_on='Verpackungsmaterial',
                           right_on='Verpackungsmaterial')
Abpackergebinde.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Abpackgebinde.xlsx')
AbpackgebindeSim = pd.DataFrame(Abpackergebinde)
AbpackgebindeSim.drop_duplicates(subset=['Verpackungsmaterial'], inplace=True)  # Hier noch Duplikate entfernen
AbpackgebindeSim['Test'] = False
AbpackgebindeSim.loc[(AbpackgebindeSim['Preis pro Gebinde'] == 'wurde aufgelöst'), 'Test'] = True
AbpackgebindeSim = AbpackgebindeSim[AbpackgebindeSim.Test == False]
AbpackgebindeSim.drop(columns=['Materialnummer',
                               'Kennzeichen für Temperaturbedingung',
                               'Kennzeichen Lose Menge',
                               'Mehrweg',
                               'Test'], inplace=True)
AbpackgebindeSim.dropna(subset=['Verpackungsmaterial'], inplace=True)
AbpackgebindeSim.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\AbpackgebindeSim.xlsx')
# Rohstoffe und Gebinde werden in ein DataFrame zusammengefügt

BR = pd.merge(BR, Abpackergebinde, left_on='E-Material', right_on='Materialnummer')
BR.drop(columns=['Materialnummer',
                 'Mengen- und Materialübereinstimmung',
                 'Materialübereinstimmung',
                 'Vorhanden',
                 'Duplikat',
                 'Test',
                 'Prodh.',
                 'Häufigkeit',
                 'Mehrweg'], inplace=True)
BR['Gebindegröße LOME'] = BR['Gebindegröße LOME'].astype(float)
BR['Benötigte Einheiten'] = np.ceil((BR['Komponentenmng.'] / BR['Gebindegröße LOME']))
BenötigtenRohstoffeTanklager = BR  # Hier werden die Rohstoffe für die Tanklagersimulation ausgelesen
Rohstoffe = BR.sort_values(by='Start')
Rohstoffe.set_index(['Start', 'Auftragsnummer'], inplace=True)
Rohstoffe.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Benötigten_Rohstoffe.xlsx')

# Liste wird auf Abpacker reduziert
i = 0
Abpacknummer = Abpacker['APN'][i]
BR['Abpacker'] = False
leng = len(Abpacker)
while i < leng:
    BR.loc[(BR['E-Material'] == Abpacknummer), 'Abpacker'] = True
    i = i + 1
    if i < leng:
        Abpacknummer = Abpacker['APN'][i]
BR = BR[BR.Abpacker == True]
BR.drop(columns=['Abpacker'], inplace=True)

# Abpacker werden ausgegeben in Liste
BR = BR.sort_values(by='Start')
BR.set_index(['Start', 'Auftragsnummer'], inplace=True)
BR.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Geplante_Abpacker.xlsx')

# Hier werden die Stücklisten nach den Materialien für das Tanklager gefiltert
# Zuerst Tanklager einlesen und die Materialnummer um die letzten 4-Ziffern entfernen
Kürzen = 0  # Anzahl der Nummern die von der Materialnummer enfernt werden

## Wenn hier die Test-Datei verwendet wird, dann muss Zeile 505 und 506 wieder eingefügt werden!

Tanklagermaterialien = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager_Neu.xlsx')  # Hier ist die zukünftige Tanklagerbelegung


TanklagermaterialienAkt = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx',
    sheet_name=2)  # Hier ist die aktuelle Tanklagerbelegung
Tanklagermaterialien['Artikelnummer'] = Tanklagermaterialien['Artikelnummer'].astype(str)
TanklagermaterialienAkt['Artikelnummer'] = TanklagermaterialienAkt['Artikelnummer'].astype(str)
# Bei Test-Excel hier 517 und 518 entfernen!
Tanklagermaterialien['Artikelnummer'] = Tanklagermaterialien['Artikelnummer'].str[
                                        :-2]  # Da die Materialnummern bei dieser Liste als Float eingelesen werden
TanklagermaterialienAkt['Artikelnummer'] = TanklagermaterialienAkt['Artikelnummer'].str[:-2]
if Kürzen > 0:
    Tanklagermaterialien['Artikelnummer'] = Tanklagermaterialien['Artikelnummer'].str[:-Kürzen]
    TanklagermaterialienAkt['Artikelnummer'] = TanklagermaterialienAkt['Artikelnummer'].str[:-Kürzen]
    BenötigtenRohstoffeTanklager['E-Material'] = BenötigtenRohstoffeTanklager['E-Material'].str[:-Kürzen]
Tanklagermaterialien.drop_duplicates(subset=['Artikelnummer'], inplace=True)  # Hier noch Duplikate entfernen
TanklagermaterialienAkt.drop_duplicates(subset=['Artikelnummer'], inplace=True)
Tanklagermaterialien.drop(columns=['Neu',
                                   'Tank-Nr.',
                                   'Tankvolumen Vn  (m³)',
                                   'WGK',
                                   'LGK',
                                   'Gefahrensymbol',
                                   'R-Sätze',
                                   'Gefahren-piktogramm',
                                   'Schlagwort',
                                   '2012/18/EU SEVESO III  StörfallV Nr.',
                                   '96/82/EC StörfallV Nr.',
                                   'H-Sätze lt. Kennzeichnungsverordnung 1272/2008',
                                   'Stoffgruppe',
                                   ' Schmelz-punkt °C',
                                   'Siedepunkt  °C',
                                   'Flammpunkt  °C',
                                   'Wasserlöslichkeit (20°C)',
                                   'Zündtemperatur °C'], inplace=True)
TanklagermaterialienAkt.drop(columns=['Tank-Nr.',
                                      'Tankvolumen Vn  (m³)',
                                      'WGK',
                                      'LGK',
                                      'Gefahrensymbol',
                                      'R-Sätze',
                                      'Gefahren-piktogramm',
                                      'Schlagwort',
                                      '2012/18/EU SEVESO III  StörfallV Nr.',
                                      '96/82/EC StörfallV Nr.',
                                      'H-Sätze lt. Kennzeichnungsverordnung 1272/2008',
                                      'Stoffgruppe',
                                      ' Schmelz-punkt °C',
                                      'Siedepunkt  °C',
                                      'Flammpunkt  °C',
                                      'Wasserlöslichkeit (20°C)',
                                      'Zündtemperatur °C'], inplace=True)
Tanklagermaterialien = Tanklagermaterialien[Tanklagermaterialien['Lösemittel'].str.contains(
    'Leer') == False]  # Alle leeren bzw. Reservetanks werden aus der Liste entfernt!
TanklagermaterialienAkt = TanklagermaterialienAkt[TanklagermaterialienAkt['Lösemittel'].str.contains('Leer') == False]
Tanklagermaterialien.reset_index(drop=True, inplace=True)
TanklagermaterialienAkt.reset_index(drop=True, inplace=True)
# Hier werden den Tanklagermaterialien die richtigen Alternativverpackungen zugeordnet
# Jeweils die Gebinde raussuchen und anschließend der Stückliste zuordnen
Tanklagermaterialien = pd.merge(Tanklagermaterialien, AbpackgebindeSim, left_on='Alternative Mehrwegverpackungen',
                                right_on='Verpackungsmaterial')

Tanklagermaterialien.drop(columns=['Alternative Mehrwegverpackungen'], inplace=True)
TanklagermaterialienAkt = pd.merge(TanklagermaterialienAkt, AbpackgebindeSim, left_on='Alternative Mehrwegverpackungen',
                                   right_on='Verpackungsmaterial')
TanklagermaterialienAkt.drop(columns=['Alternative Mehrwegverpackungen'], inplace=True)


Länge = len(TanklagermaterialienAkt)
i = 0
Materialnummer = TanklagermaterialienAkt['Artikelnummer'][i]
Verpackungsmaterial = TanklagermaterialienAkt['Verpackungsmaterial'][i]
Gebindegröße = TanklagermaterialienAkt['Gebindegröße LOME'][i]
Preis = TanklagermaterialienAkt['Preis pro Gebinde'][i]
Stück = TanklagermaterialienAkt['Stück pro Schicht'][i]
while i < Länge:
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Verpackungsmaterial'] = Verpackungsmaterial
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Gebindegröße LOME'] = Gebindegröße
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Preis pro Gebinde'] = Preis
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Stück pro Schicht'] = Stück
    i = i + 1
    if i < Länge:
        Materialnummer = TanklagermaterialienAkt['Artikelnummer'][i]
        Verpackungsmaterial = TanklagermaterialienAkt['Verpackungsmaterial'][i]
        Gebindegröße = TanklagermaterialienAkt['Gebindegröße LOME'][i]
        Preis = TanklagermaterialienAkt['Preis pro Gebinde'][i]
        Stück = TanklagermaterialienAkt['Stück pro Schicht'][i]

Länge = len(Tanklagermaterialien)
i = 0
Materialnummer = Tanklagermaterialien['Artikelnummer'][i]
Verpackungsmaterial = Tanklagermaterialien['Verpackungsmaterial'][i]
Gebindegröße = Tanklagermaterialien['Gebindegröße LOME'][i]
KapazitaetTankwagen = Tanklagermaterialien['Kapazität Bahnkesselwagen (m³)'][i]
Dichte = Tanklagermaterialien['Dichte (kg/m³)'][i]
Preis = Tanklagermaterialien['Preis pro Gebinde'][i]
Stück = Tanklagermaterialien['Stück pro Schicht'][i]
RohstoffkostenIBC = Tanklagermaterialien['Kosten (KG für IBC)'][i]
RohstoffkostenTank = Tanklagermaterialien['Kosten (KG für Tank)'][i]
AbfallkostenIBC = Tanklagermaterialien['Abfallkosten (KG für IBC)'][i]
while i < Länge:
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Verpackungsmaterial'] = Verpackungsmaterial
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Gebindegröße LOME'] = Gebindegröße
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Preis pro Gebinde'] = Preis
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Stück pro Schicht'] = Stück
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Kapazität Bahnkesselwagen (m³)'] = KapazitaetTankwagen
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Dichte (kg/m³)'] = Dichte
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Kosten (KG für IBC)'] = RohstoffkostenIBC
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Kosten (KG für Tank)'] = RohstoffkostenTank
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'Abfallkosten (KG für IBC)'] = AbfallkostenIBC
    i = i + 1
    if i < Länge:
        Materialnummer = Tanklagermaterialien['Artikelnummer'][i]
        Verpackungsmaterial = Tanklagermaterialien['Verpackungsmaterial'][i]
        Gebindegröße = Tanklagermaterialien['Gebindegröße LOME'][i]
        KapazitaetTankwagen = Tanklagermaterialien['Kapazität Bahnkesselwagen (m³)'][i]
        Dichte = Tanklagermaterialien['Dichte (kg/m³)'][i]
        Preis = Tanklagermaterialien['Preis pro Gebinde'][i]
        Stück = Tanklagermaterialien['Stück pro Schicht'][i]
        RohstoffkostenIBC = Tanklagermaterialien['Kosten (KG für IBC)'][i]
        RohstoffkostenTank = Tanklagermaterialien['Kosten (KG für Tank)'][i]
        AbfallkostenIBC = Tanklagermaterialien['Abfallkosten (KG für IBC)'][i]

BenötigtenRohstoffeTanklager['Benötigte Einheiten'] = np.ceil(
    (BenötigtenRohstoffeTanklager['Komponentenmng.'] / BenötigtenRohstoffeTanklager['Gebindegröße LOME']))



# Jetzt BenötigtenRohstoffeTanklager mit der Tanklagermaterialien abgleichen
Länge = len(Tanklagermaterialien)
BenötigtenRohstoffeTanklager['ImTanklagerZukunft'] = False
BenötigtenRohstoffeTanklager['ImTanklager'] = False
i = 0
Materialnummer = Tanklagermaterialien['Artikelnummer'][i]
while i < Länge:
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'ImTanklagerZukunft'] = True
    i = i + 1
    if i < Länge:
        Materialnummer = Tanklagermaterialien['Artikelnummer'][i]

print(BenötigtenRohstoffeTanklager)

Länge = len(TanklagermaterialienAkt)
i = 0
Materialnummer = TanklagermaterialienAkt['Artikelnummer'][i]
while i < Länge:
    BenötigtenRohstoffeTanklager.loc[
        (BenötigtenRohstoffeTanklager['E-Material'] == Materialnummer), 'ImTanklager'] = True
    i = i + 1
    if i < Länge:
        Materialnummer = TanklagermaterialienAkt['Artikelnummer'][i]

TanklagerZukunft = BenötigtenRohstoffeTanklager[BenötigtenRohstoffeTanklager[
                                                    'ImTanklagerZukunft'] == True]  # Hier weden alle Tanklagerprodukte gefiltert für den Forecast
RohstoffeZukunft = BenötigtenRohstoffeTanklager[BenötigtenRohstoffeTanklager[
                                                    'ImTanklagerZukunft'] == False]  # Hier sind alle Rohstoffe ohne Tanklager für den Forecast
Tanklager = BenötigtenRohstoffeTanklager[BenötigtenRohstoffeTanklager[
                                             'ImTanklager'] == True]  # Hier sind alle Tanklagerprodukte mit der aktuellen Tanklagerbelegung
RohstoffeAktuell = BenötigtenRohstoffeTanklager[BenötigtenRohstoffeTanklager[
                                                    'ImTanklager'] == False]  # Hier sind alle Rohstoffe mit der aktuellen Tanklagerbelegung


# Hier werden noch jeweils alle Materialnummern der neuen Materialien zusammengefasst.
# Bspw. für Methyl-THF 821093 und 202781
SammlungMaterialnummern = pd.read_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Dateien\Belegung Tanklager.xlsx', sheet_name=1)
SammlungMaterialnummern['Basisnummer'] = SammlungMaterialnummern['Basisnummer'].astype(str)
SammlungMaterialnummern['Alternativen'] = SammlungMaterialnummern['Alternativen'].astype(str)
Länge = len(SammlungMaterialnummern)
i = 0
Basisnummer = SammlungMaterialnummern['Basisnummer'][i]
Alternativnummer = SammlungMaterialnummern['Alternativen'][i]
while i < Länge:
    TanklagerZukunft.loc[(TanklagerZukunft['E-Material'] == Alternativnummer), 'E-Material'] = Basisnummer
    i = i + 1
    if i < Länge:
        Basisnummer = SammlungMaterialnummern['Basisnummer'][i]
        Alternativnummer = SammlungMaterialnummern['Alternativen'][i]
# Ende des Auslesevorgangs der alternativen Materialnummern


TanklagerZukunft.drop(columns=['ImTanklager',
                               'Abpacker',
                               'ImTanklagerZukunft',
                               'Base UOM',
                               'Kennzeichen für Temperaturbedingung',
                               'Kennzeichen Lose Menge'], inplace=True)
RohstoffeZukunft.drop(columns=['ImTanklager',
                               'ImTanklagerZukunft',
                               'Kennzeichen Lose Menge'], inplace=True)
Tanklager.drop(columns=['ImTanklager',
                        'Abpacker',
                        'ImTanklagerZukunft',
                        'Base UOM',
                        'Kennzeichen für Temperaturbedingung',
                        'Kennzeichen Lose Menge',
                        'Verpackungsmaterial',
                        'Gebindegröße LOME',
                        'Preis pro Gebinde',
                        'Stück pro Schicht',
                        'Benötigte Einheiten'], inplace=True)
RohstoffeAktuell.drop(columns=['ImTanklager',
                               'ImTanklagerZukunft',
                               'Kennzeichen Lose Menge'], inplace=True)


TanklagerZukunft.sort_values(by='Start', inplace=True)
RohstoffeZukunft.sort_values(by='Start', inplace=True)
Tanklager.sort_values(by='Start', inplace=True)
RohstoffeAktuell.sort_values(by='Start', inplace=True)

TanklagerZukunft.set_index(['Auftragsnummer'], inplace=True)
RohstoffeZukunft.set_index(['Auftragsnummer'], inplace=True)
Tanklager.set_index(['Auftragsnummer'], inplace=True)
RohstoffeAktuell.set_index(['Auftragsnummer'], inplace=True)

RohstoffeZukunft.loc[(RohstoffeZukunft['Verpackungsmaterial'] == ''), 'Verpackungsmaterial'] = 0  # Da in der Simulation

TanklagerZukunft.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Tanklagerverbrauch mit neuer Belegung.xlsx')
RohstoffeZukunft.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Rohstoffverbrauch ohne Tanklager mit neuer Belegung (Sim).xlsx')
Tanklager.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Tanklagerverbrauch mit aktueller Belegung.xlsx')
RohstoffeAktuell.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Rohstoffverbrauch ohne Tanklager mit aktueller Belegung (Sim).xlsx')
#Kombination  Verbrauch Tanklager und Gebinde
TanklagerZukunft.reset_index(drop=False, inplace=True)
RohstoffeZukunft.reset_index(drop=False, inplace=True)
DatenSim = pd.merge(TanklagerZukunft, RohstoffeZukunft, how='outer')
DatenSim.set_index(['Auftragsnummer'], inplace=True)
DatenSim.sort_values(by='Auftragsnummer', inplace=True)
DatenSim.sort_values(by='Start', inplace=True)
DatenSim['Verpackungsmaterial'].fillna(value= '7.92701.9053', inplace=True) #Hier werden alle leeren Gebindezellen aufgeüllt!
DatenSim.loc[DatenSim['Verpackungsmaterial'] == '7.92443.9090', 'Verpackungsmaterial'] = '7.92443.9150'
DatenSim.loc[DatenSim['Gebindegröße LOME'] == 0, 'Preis pro Gebinde'] = 250.26
DatenSim.loc[DatenSim['Gebindegröße LOME'] == 0, 'Gebindegröße LOME'] = 800
DatenSim['Benötigte Einheiten'] = np.ceil(abs(DatenSim['Komponentenmng.']) / DatenSim['Gebindegröße LOME'])
DatenSim.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Rohstoffverbrauch_Gesamt (Sim).xlsx')

#Materialmapping
Materials = DatenSim
Materials.drop_duplicates(subset=['E-Material'], inplace=True) # Hier Duplikate entfernen
Materials.reset_index(inplace=True)
Rohsto = pd.DataFrame(Materials)
Rohsto.drop_duplicates(subset=['Material'], inplace=True) # Hier Duplikate entfernen
Rohsto = Rohsto[['Material', 'Kurztext', 'Me','Abpacker']]
Rohsto['Abpacker'] = False
Rohsto.rename(columns={'Material': 'E-Material','Me' : 'Me2', 'Kurztext' : 'Kurztext2'}, inplace = True)
Rohsto = pd.merge(Rohsto, Abpackergebinde, left_on='E-Material', right_on='Materialnummer', how ='left')
Rohsto = Rohsto[['E-Material', 'Me2', 'Kurztext2',  'Verpackungsmaterial','Gebindegröße LOME', 'Abpacker']]
Rohsto['Verpackungsmaterial'].fillna(value= '7.92701.9053', inplace=True) #Hier werden alle leeren Gebindezellen aufgeüllt!
Materials.drop(columns=['Auftragsnummer',
                        'Material',
                        'Kurztext',
                        'Basismenge',
                        'Me',
                        'Komponentenmng.',
                        'Start',
                        'Hinweis',
                        'Preis pro Gebinde',
                        'Stück pro Schicht',
                        'Benötigte Einheiten',
                        'Kapazität Bahnkesselwagen (m³)',
                        'Kosten (KG für IBC)',
                        'Kosten (KG für Tank)',
                        'Abfallkosten (KG für IBC)',
                        'Base UOM',
                        'Kennzeichen für Temperaturbedingung'], inplace=True)
Materials = pd.merge(Materials, Rohsto, how = "outer")
Materials.loc[Materials['Gebindegröße LOME'] == 0, 'Preis pro Gebinde'] = 250.26
Materials.loc[Materials['Gebindegröße LOME'] == 0, 'Gebindegröße LOME'] = 800
Materials.loc[Materials['Verpackungsmaterial'] == '9.90701.1002', 'Gebindegröße LOME'] = 744
Materials.loc[Materials['Verpackungsmaterial'] == '9.90701.1002', 'Preis pro Gebinde'] = 250.26
Materials.loc[Materials['Verpackungsmaterial'] == '7.92701.9053', 'Gebindegröße LOME'] = 744
Materials.loc[Materials['Verpackungsmaterial'] == '7.92701.9053', 'Preis pro Gebinde'] = 250.26
Materials.to_excel(
    r'C:\Users\mb-itl-sim\Models\Materialflussanalyse_EL-DOD\Database\Programmcodes\Datenaufbereitung\Simulation\Materials (Sim).xlsx')
