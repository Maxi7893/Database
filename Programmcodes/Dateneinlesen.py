#import numpy
import pandas as pd

#Produktionstermine werden eingelesen
a = 10 #KLänge der Materialnummern
b = 4 #Anzahl der Ziffern die aus der Materialnummer entfernt werden (Bspw. 7777)
c = 1 #Wie viele Nachkommastellen bei den Startterminen entfernt werden sollen
ST = pd.read_excel('Dateien\Starttermine DOD-4_07.07.2022.xlsx')
ST = ST[ST['Mat.-Nr.'].notna()] #Sobald eine Zeile in diesem Bereich Leer ist, wird diese gelöscht
ST['Mat.-Nr.'] = ST['Mat.-Nr.'].str.replace('.' , '')
ST['Mat.-Nr.'] = ST['Mat.-Nr.'].str[:-b] #die letzten Ziffern werden entfernt
ST['Menge'] = ST['Menge'].str.replace(',' , '') #Kommas werden entfernt
ST['Menge'] = ST['Menge'].str.replace('.' , ',') #Dezimaltrennung ändern
ST['Mat.-Nr.'].astype(float) #Materialnummer zu einem Float
Spliting = ST['Menge'].str.split(expand=True) #Datenbank aufsplitten
Spliting.rename(columns={0 : 'Menge', 1: 'Einheit'}, inplace=True) #Datenstrukturen Namen geben
ST.drop(columns='Menge',inplace=True) #Die gesplitteten Spalten aus dem ursprünglichem entfernen
Start = pd.merge(ST,Spliting,left_index=True,right_index=True) #Datenbanken zusammenfügen
Start['Menge'] = Start['Menge'].str.replace(',', '') #Hier werden die Kommas aus der Mengeneinheit entfernt
Start['Menge'] = Start['Menge'].str[:-c] #Hier werden die Nachkommastellen entfernt ACHTUNG: Es wird immmer nur von einer ausgegangen
Start['Menge'].astype(float) #Datentyp Float erstellen
Start.set_index(['Mat.-Nr.', 'Start','Menge'], inplace=True)


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
Stueli['Material'] = Stueli['Material'].str[:-b] #hier werden die Materialnummern um die letzten Ziffern gekürzt
Stueli['Basismenge'] = Stueli['Basismenge'].str.replace('.' , '') #Punkte aus der Basismenge entfernen
Stueli['Material'].astype(float) #Datentyp verändern
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('.' , '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace(',' , '.')
Stueli['Negativ'] = 1
Stueli.loc[Stueli['Komponentenmng.'].str.contains('-'), 'Negativ'] = -1
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].str.replace('-', '')
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.'].astype(float)
Stueli['Komponentenmng.'] = Stueli['Komponentenmng.']*Stueli['Negativ']
Stueli.set_index(['Material', 'Basismenge', 'Komponentenmng.'], inplace=True)  #hier wird die Materialnummer der Index
print(Stueli)



#Negative Mengen aus der Datenbank rauslesen

#for i in Stueli.index:
#    if Stueli.loc[Stueli[i],Stueli['Komponentenmng.']]:
#       print('Test erfolgreich!')


#for-Schleife
Behälter = Stueli[Stueli['Me2'].str.contains('ST')]
Abfall = Stueli[Stueli['Me2'].str.contains('ST')]

#print(DelList)
defNew1 = Stueli[Stueli['Me2'].str.contains('L')]
dfNew = pd.merge(Stueli[Stueli['Me2'].str.contains('ST')], Stueli[Stueli['Me2'].str.contains('L')], left_index=True,right_index=True)

print(dfNew)
