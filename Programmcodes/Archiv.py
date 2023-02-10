import numpy as np
import pandas as pd
from datetime import date, timedelta

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
print(Next)