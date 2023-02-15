import numpy as np
import pandas as pd
from datetime import date, timedelta

#Produktionstermine werden eingelesen
a = 10 #Länge der Materialnummern
b = 0 #Anzahl der Ziffern die aus der Materialnummer entfernt werden (Bspw. 7777)
c = 1 #Wie viele Nachkommastellen bei den Startterminen entfernt werden sollen
Date = '2023-05-19' #Für den Test hier nur ein beispielhafter Tag
Date = pd.to_datetime(Date) #Zeile 9 und 10 können hinterher gelöscht werden und Zeile 11 aktiviert
#Date = date.today() #Aktueller Tag wird gespeichert
NextDate = Date + timedelta(days=14) #In den nächsten 14 Tagen wird geschaut, was ansteht

#Starttermine Produktionsaufträge G20
Starttermine = pd.read_excel('Dateien\Starttermine G20 - 2023.xlsx') #Einlesen der Excel Liste für die Produktionstermine
Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str.replace('.' , '')  #Punkte aus der Materialnummer entfernen
if b>0:
    Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str[:-b] #hier werden die Materialnummern um die letzten Ziffern gekürzt
Starttermine.rename(columns={'Offene Menge':'Menge', 'Beginn (terminiert)':'Start','Ende (terminiert)':'Ende', 'Produktionsmengeneinheit':'Me' }, inplace=True)
Starttermine.set_index(['Start'], inplace=True) #Index setzen
#Hier noch alle löschen, die Zulässig eingeplant FALSE haben
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
                           'Geändert von'],inplace=True)
Starttermine=Starttermine.sort_values(by='Start') #Index nach Datum sortieren
Next=Starttermine[Date:NextDate] #Filtern des Betrachtungszeitraums!
#Starttermine Produktionsaufträge G1
Starttermine=pd.read_excel('Dateien\Produktion_G1.xlsx', header=1) #Einlesen der Excel-Liste G1'
Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str.replace('.' , '') #Punkte aus der Materialnummer entfernen
if b>0:
    Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str[:-b] #hier werden die Materialnummern um die letzten Ziffern gekürzt
Starttermine.rename(columns={'Anfo':'Auftrags-Nr.','EH':'Me'}, inplace=True)
Starttermine.drop(columns=['Status',
                           'Dispo',
                           'FS',
                           'Hersteller'],inplace=True)
Starttermine.set_index(['Start'], inplace=True) #Index setzen
Starttermine=Starttermine.sort_values(by='Start')
Next2=Starttermine[Date:NextDate]

#Startlisten zusammenführen
Next = Next.reset_index()
Next2 = Next2.reset_index()
Next = pd.merge(Next,Next2, how='outer')
Next.to_excel('Nächsten Produktionstermine.xlsx')
#Stücklisten werden eingelesen
List1 = pd.read_csv('Dateien\STUELI_EL-DOD-4.TXT',names=['Werk',
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
                        'Lab'],sep='#',encoding='windows-1252') #Einlseen der txt und encoding
List2 = pd.read_csv('Dateien\Stückliste G1.TXT',names=['Werk',
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
                        'Lab'],sep='#',encoding='windows-1252') #Einlseen der txt und encoding
List2 = List2.dropna(subset=['Kurztext']) #Hier werden die deleted entfernt
List = pd.merge(List1, List2, how='outer') #Die beiden Stücklisten werden zusammengefügt
Stueli = pd.DataFrame(List)
Stueli.drop(labels=0, axis=0, inplace =True) #hier wird die erste Zeile gedropt
Stueli.drop(columns=['Werk',
                    'Ss',
                    'P',
                    'Losgr.von',
                    'Losgr.bis',
                    'Dis',
                    'Lab'],inplace=True) #hier werden alle unwichtigen Spalten gelöscht
if b>0:
    Stueli['Material'] = Stueli['Material'].str[:-b]#hier werden die Materialnummern um die letzten Ziffern gekürzt
    Stueli['E-Material'] = Stueli['E-Material'].str[:-b]
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace('.' , '') #Punkte aus der Basismenge entfernen
#Stueli['Material'] = Stueli['Material'].astype(int) #Datentyp verändern
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('.' , '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(',' , '.')
Stueli['Negativ'] = 1
Stueli.loc[Stueli['Komponentenmng.'].str.contains('-'), 'Negativ'] = -1 #Sobald negative Werte vorliegen werden diese gekennzeichnet
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('-', '') #Die Bindestriche (negativ-Zeichen) werden entfernt
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(' ', '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('null', '0')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].astype(float) #Mengen werden zu einem Float
Stueli['Basismenge'] = Stueli['Basismenge'].str[:-4] #Hier werden die Basismengen bis zu dem Komma gekürzt
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace(',', '') #Hier werden die Kommas aus der Mengeneinheit entfernt
Stueli['Basismenge'] = Stueli['Basismenge'].astype(float) #Basismengen werden zu einem Float umgewandelt
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.']*Stueli['Negativ'] #Negative Mengen sind jetzt kein String mehr
Stueli.drop(columns='Negativ',inplace=True) #Die erstelte Spalte wieder entfernt
#Stueli['Rohstoff'] = (Stueli['Komponentenmng.'] > 0) & (Stueli['Me2'].str.contains('KG'))
indexNames =  Stueli[(Stueli['Komponentenmng.'] < 0) | (Stueli['Me2'].str.contains('ST'))].index #Hier wird die Indexnummer gespeichert, welche alle Mengen negativ sind oder der Einheit Stück angehören
FS = pd.DataFrame(Stueli) #Es wird ein neues DataFrame iniziert
FS.drop(indexNames, inplace=True) #Es werden alle Abfälle und Stückmengen entfernt

#Hier wird die Häufigkeit ermittelt
data = Next['Mat.-Nr.']
data = data.reset_index()
#data.drop(columns='Start',inplace=True)
data.drop(columns='index',inplace=True)
Häufigkeit = pd.Series(data['Mat.-Nr.'])
Häufigkeit = Häufigkeit.value_counts(sort=False)  #Hier wird berechnet, wie oft die Rohstoffe benötigt werden
data = Häufigkeit.to_frame()
data = Häufigkeit.reset_index()
data.columns = ['Mat.-Nr.', 'Häufigkeit']
print(data)
AnzahlPro = len(data)
i=0
Auftragsnummer = data['Mat.-Nr.'][i]
Häufigkeit = data['Häufigkeit'][i]
FS['Häufigkeit'] = 0

while i < AnzahlPro: #Hier wird die Häufigkeit der Produkte in den nächsten zwei Wochen in die Liste eingepflegt
    FS.loc[(FS['Material'] == Auftragsnummer), 'Häufigkeit'] = Häufigkeit
    i = i+1
    if i < AnzahlPro:
        Auftragsnummer = data['Mat.-Nr.'][i]
        Häufigkeit = data['Häufigkeit'][i]

#Hier werden die benötigten Rohstoffe ausgelesen
Aufträge = len(Next)
i = 0
#Al 1 nehmen oder höher, falls nicht nur Materialübereinstimmung ist
FS['Materialübereinstimmung'] = 0
FS['Mengenübereinstimmung'] = 0
FS['Mengen- und Materialübereinstimmung'] = False
Auftragsnummer = Next['Mat.-Nr.'][i]
Menge = Next['Menge'][i]
while i < (Aufträge): #Hier werden die Materialien ausgelesen, welche benötigt werden
    FS.loc[(FS['Material'] == Auftragsnummer), 'Materialübereinstimmung'] = 1
    FS.loc[(FS['Basismenge'] == Menge), 'Mengenübereinstimmung' ] = 1
    FS.loc[(FS['Materialübereinstimmung'] == 1) & FS['Mengenübereinstimmung']==1,'Mengen- und Materialübereinstimmung'] = True
    i = i+1
    if i < Aufträge:
        Auftragsnummer = Next['Mat.-Nr.'][i]
        Menge = Next['Menge'][i] #wurde hinzugefüt, da Neben der Materialnummer ebenfalls die Menge stimmen muss!

#Was ist, wenn es kein Rezept gibt, bei welchem die Menge übereinstimmt
Test = FS.loc[(FS['Materialübereinstimmung'] == 1) & (FS['Mengen- und Materialübereinstimmung'] ==False)]
Test.to_excel('Benötigten_Rohstoff.xlsx')
BR = FS.loc[(FS['Materialübereinstimmung'] == 1) & (FS['Mengenübereinstimmung'] == 1)]
BR.drop(columns=['Al',
                 'Mart',
                 'Pos.',
                 'Fev',
                 'Materialübereinstimmung',
                 'Mengenübereinstimmung'],inplace=True) #hier werden alle unwichtigen Spalten gelöscht

#Abpacker werden eingelesen
Abpacker = pd.read_excel('Dateien\Abpacker.xlsx', sheet_name=1) #Abpacker werden aus der Excel-Liste eingelesen
Abpacker.drop(columns=['auch GMP-Abpackungen?',
                       'PSA K16',
                       'Gruppen-BA',
                       'PSA-Schutzstufe nach GloveBox',
                       'PSA-Schutzstufe nach GloveBag',
                       'Kommentar ',
                       'SADT'],inplace=True) #Unwichtige Spalten werden gelöscht
Abpacker['APN'] = Abpacker['APN'].astype(str) #Materialnummern der Abpacker werden zu einem String
if b>0:
    Abpacker['APN'] = Abpacker['APN'].str[:-b] # Die letzten Ziffern werden entfernt, wenn die Bedingung erfüllt wird
#Liste wird auf Abpacker reduziert
i=0
Abpacknummer = Abpacker['APN'][i]
BR['Abpacker'] = False
len = len(Abpacker)
while i< len:
    BR.loc[(BR['E-Material'] == Abpacknummer), 'Abpacker'] = True
    i=i+1
    if i < len:
        Abpacknummer = Abpacker['APN'][i]
BR = BR[BR.Abpacker == True]
BR.drop(columns=['Abpacker'],inplace=True)

#Abpackgebinde werden eingelesen
Abpackergebinde = pd.read_excel('Dateien\MARA_G1_g20_Gebinde.xlsx')
Abpackergebinde = Abpackergebinde.iloc[1:]
Abpackergebinde.drop_duplicates(subset=['Materialnummer'],inplace=True)#Hier noch Duplikate entfernen
Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str.replace('.' , '')
if b>0:
    Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str[:-b] #die letzten Ziffern werden entfernt

#Abpacker und Gebinde werden in ein DataFrame zusammengefügt
BR = pd.merge(BR, Abpackergebinde, left_on='E-Material',right_on='Materialnummer') #Hier gehen noch einige Sachen verloren!

BR.drop(columns=['Materialnummer'],inplace=True)
BR['Gebindegröße LOME']=BR['Gebindegröße LOME'].astype(float)
BR['Benötigte Einheiten'] = np.ceil((BR['Komponentenmng.']/BR['Gebindegröße LOME']))*BR['Häufigkeit']
print(BR)
BR.to_excel('Benötigten_Rohstoffe.xlsx')

#Es müssen noch kontrolliert werden, ob die Mengen übereinstimmen! Aktuell werden die Aufträge, bei denen die Mengen nicht stimmen nicht berücksichtigt
