import numpy as np
import pandas as pd
from datetime import date, timedelta

#Produktionstermine werden eingelesen
a = 10 #KLänge der Materialnummern
b = 0 #Anzahl der Ziffern die aus der Materialnummer entfernt werden (Bspw. 7777)
c = 1 #Wie viele Nachkommastellen bei den Startterminen entfernt werden sollen
Date = '2022-08-14' #Für den Test hier nur ein beispielhafter Tag
Date = pd.to_datetime(Date) #Zeile 9 und 10 können hinterher gelöscht werden und Zeile 11 aktiviert
#Date = date.today() #Aktueller Tag wird gespeichert
NextDate = Date + timedelta(days=14) #In den nächsten 14 Tagen wird geschaut, was ansteht
ST = pd.read_excel('Dateien\Starttermine DOD-4_07.07.2022.xlsx')
ST = ST[ST['Mat.-Nr.'].notna()] #Sobald eine Zeile in diesem Bereich Leer ist, wird diese gelöscht
ST['Mat.-Nr.'] = ST['Mat.-Nr.'].str.replace('.' , '')
if b>0:
    ST['Mat.-Nr.'] = ST['Mat.-Nr.'].str[:-b] #die letzten Ziffern werden entfernt
ST['Menge'] = ST['Menge'].str.replace(',' , '') #Kommas werden entfernt
ST['Menge'] = ST['Menge'].str.replace('.' , ',') #Dezimaltrennung ändern
#ST['Mat.-Nr.'] = ST['Mat.-Nr.'].astype(int) #Materialnummer zu einem Float
Spliting = ST['Menge'].str.split(expand=True) #Datenbank aufsplitten
Spliting.rename(columns={0 : 'Menge', 1: 'Einheit'}, inplace=True) #Datenstrukturen Namen geben
ST.drop(columns='Menge',inplace=True) #Die gesplitteten Spalten aus dem ursprünglichem entfernen
Start = pd.merge(ST,Spliting,left_index=True,right_index=True) #Datenbanken zusammenfügen
Start['Menge'] = Start['Menge'].str.replace(',', '') #Hier werden die Kommas aus der Mengeneinheit entfernt
Start['Menge'] = Start['Menge'].str[:-c] #Hier werden die Nachkommastellen entfernt ACHTUNG: Es wird immmer nur von einer ausgegangen
Start['Menge'] = Start['Menge'].astype(float) #Datentyp Float erstellen
Start['Start'] = pd.to_datetime(Start['Start'])
Start.set_index(['Start'], inplace=True) #Hier wird der Index gesetzt
Start = Start.sort_values(by='Start') #Hier wird die Liste noch nach den Startdaten geordnet
Next = Start[Date:NextDate] #Hier werden die Aufträge der nächsten zwei Wochen ausgelesen
#Next.set_index(['Mat.-Nr.'],inplace=True) #Hier werden die Materialnummern zu einem Index

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
    Stueli['Material'] = Stueli['Material'].str[:-b] #hier werden die Materialnummern um die letzten Ziffern gekürzt
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace('.' , '') #Punkte aus der Basismenge entfernen
#Stueli['Material'] = Stueli['Material'].astype(int) #Datentyp verändern
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('.' , '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(',' , '.')
Stueli['Negativ'] = 1
Stueli.loc[Stueli['Komponentenmng.'].str.contains('-'), 'Negativ'] = -1 #Sobald negative Werte vorliegen werden diese mit gekennzeichnet
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

#Abpacker werden eingelesen
Abpacker = pd.read_excel('Dateien\Abpacker.xlsx', sheet_name=1) #Abpacker werden aus der Excel-Liste eingelesen
Abpacker.drop(columns=['auch GMP-Abpackungen?',
                       'PSA K16',
                       'Gruppen-BA',
                       'PSA-Schutzstufe nach GloveBox',
                       'PSA-Schutzstufe nach GloveBag',
                       'Kommentar ',
                       'SADT'],inplace=True) #Unwichtige Spalten werden gelöscht
Abpacker['APN'] = Abpacker['APN'].astype(str) #Materialnummern der Abpacker werden
if b>0:
    Abpacker['APN'] = Abpacker['APN'].str[:-b]
Abpacker.set_index(['APN'],inplace=True) #Index der Materialnummer wird gesetzt

#Hier werden die abzupackenden Rohstoffe ausgelesen
Aufträge = len(Next)
i = 0
FS['Materialübereinstimmung'] = 0
FS['Mengenübereinstimmung'] = 0
Auftragsnummer = Next['Mat.-Nr.'][i]
Menge = Next['Menge'][i]
while i < (Aufträge-1):
    FS.loc[(FS['Material'] == Auftragsnummer), 'Materialübereinstimmung'] = 999
    FS.loc[(FS['Basismenge'] == Menge), 'Mengenübereinstimmung' ] = 999
    i = i+1
    Auftragsnummer = Next['Mat.-Nr.'][i]
    Menge = Next['Menge'][i] #wurde hinzugefüt, da Neben der Materialnummer ebenfalls die Menge stimmen muss!
    print('Durlaufnr.', i, 'mit der Materialnummer', Auftragsnummer)

BR = FS.loc[(FS['Materialübereinstimmung'] == 999) & (FS['Mengenübereinstimmung'] == 999)]
BR.drop(columns=['Al',
                 'Mart',
                 'Pos.',
                 'Fev',
                 'Kurztext2',
                 'Materialübereinstimmung',
                 'Mengenübereinstimmung'],inplace=True) #hier werden alle unwichtigen Spalten gelöscht
BR.to_excel('Benötigten_Rohstoffe.xlsx')

#Jetzt noch schauen, welche Rohstoffe häufiger benötigt werden und ein Abgleich mit den Abpackern