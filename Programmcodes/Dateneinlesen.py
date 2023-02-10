import numpy as np
import pandas as pd
from datetime import date, timedelta

#Produktionstermine werden eingelesen
a = 10 #KLänge der Materialnummern
b = 0 #Anzahl der Ziffern die aus der Materialnummer entfernt werden (Bspw. 7777)
c = 1 #Wie viele Nachkommastellen bei den Startterminen entfernt werden sollen
Date = '2023-01-14' #Für den Test hier nur ein beispielhafter Tag
Date = pd.to_datetime(Date) #Zeile 9 und 10 können hinterher gelöscht werden und Zeile 11 aktiviert
#Date = date.today() #Aktueller Tag wird gespeichert
NextDate = Date + timedelta(days=14) #In den nächsten 14 Tagen wird geschaut, was ansteht

#Starttermine Produktionsaufträge G20
Starttermine = pd.read_excel('Dateien\Starttermine G20 - 2023.xlsx')
Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str.replace('.' , '')
if b>0:
    Starttermine['Mat.-Nr.'] = Starttermine['Mat.-Nr.'].str[:-b]
Starttermine.rename(columns={'Offene Menge':'Menge', 'Beginn (terminiert)':'Start','Ende (terminiert)':'Ende' }, inplace=True)
Starttermine.set_index(['Start'], inplace=True)
Starttermine=Starttermine.sort_values(by='Start')
Next=Starttermine[Date:NextDate]
print(Next)

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
Stueli = pd.DataFrame(List1)
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
data.drop(columns='Start',inplace=True)
Häufigkeit = pd.Series(data['Mat.-Nr.'])
Häufigkeit = Häufigkeit.value_counts(sort=False)  #Hier wird berechnet, wie oft die Rohstoffe benötigt werden
data = Häufigkeit.to_frame()
data = Häufigkeit.reset_index()
data.columns = ['Mat.-Nr.', 'Häufigkeit']
AnzahlPro = len(data)
i=0
Auftragsnummer = data['Mat.-Nr.'][i]
Häufigkeit = data['Häufigkeit'][i]
FS['Häufigkeit'] = 0
while i < (AnzahlPro-1): #Hier wird die Häufigkeit der Produkte in den nächsten zwei Wochen in die Liste eingepflegt
    FS.loc[(FS['Material'] == Auftragsnummer), 'Häufigkeit'] = Häufigkeit
    i = i+1
    Auftragsnummer = data['Mat.-Nr.'][i]
    Häufigkeit = data['Häufigkeit'][i]

#Hier werden die abzupackenden Rohstoffe ausgelesen
Aufträge = len(Next)
i = 0
FS['Materialübereinstimmung'] = 0
FS['Mengenübereinstimmung'] = 0
Auftragsnummer = Next['Mat.-Nr.'][i]
Menge = Next['Menge'][i]
while i < (Aufträge-1): #Hier werden die Materialien ausgelesen, welche benötigt werden
    FS.loc[(FS['Material'] == Auftragsnummer), 'Materialübereinstimmung'] = 1
    FS.loc[(FS['Basismenge'] == Menge), 'Mengenübereinstimmung' ] = 1
    i = i+1
    Auftragsnummer = Next['Mat.-Nr.'][i]
    Menge = Next['Menge'][i] #wurde hinzugefüt, da Neben der Materialnummer ebenfalls die Menge stimmen muss!
    #Es gilt jedoch noch zu berücksichtigen, wenn Auträge sich doppeln, müssen die Mengen ebenfalls verdoppelt werden
   # print('Durlaufnr.', i, 'mit der Materialnummer', Auftragsnummer)
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
while i<(len-1):
    BR.loc[(BR['E-Material'] == Abpacknummer), 'Abpacker'] = True
    i=i+1
    Abpacknummer = Abpacker['APN'][i]
BR = BR[BR.Abpacker == True]
BR.drop(columns=['Abpacker'],inplace=True)
#BR = Benötigten Rohstoffe
#Abpacker = alle abzupackenden Rohstoffe

#Abpackgebinde werden eingelesen
Abpackergebinde = pd.read_excel('Dateien\MARA_G20 Materialien_incl.E-Mat.xlsx')
Abpackergebinde = Abpackergebinde.iloc[1:]
Abpackergebinde.drop(columns=['E-Material'], inplace=True)
Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str.replace('.' , '')
if b>0:
    Abpackergebinde['Materialnummer'] = Abpackergebinde['Materialnummer'].str[:-b] #die letzten Ziffern werden entfernt
#Abpacker und Gebinde werden in ein DataFrame zusammengefügt
BR = pd.merge(BR, Abpackergebinde, left_on='E-Material',right_on='Materialnummer')
BR.drop(columns=['Materialnummer'],inplace=True)
BR['Gebindegröße LOME']=BR['Gebindegröße LOME'].astype(float)
BR['Benötigte Einheiten'] = np.ceil((BR['Komponentenmng.']/BR['Gebindegröße LOME']))*BR['Häufigkeit']
BR.to_excel('Benötigten_Rohstoffe.xlsx')