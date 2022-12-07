#import numpy
import pandas as pd

#Produktionstermine werden eingelesen
a = 10
b = 4
StarttermineDOD4 = pd.read_excel('Dateien\Starttermine DOD-4_07.07.2022.xlsx')
StarttermineDOD4 = StarttermineDOD4[StarttermineDOD4['Mat.-Nr.'].notna()] #Sobald eine Zeile in diesem Bereich Leer ist, wird diese gelöscht
StarttermineDOD4['Mat.-Nr.'] = StarttermineDOD4['Mat.-Nr.'].str.replace('.' , '').str[:-b]
StarttermineDOD4['Mat.-Nr.'].astype(float)
StarttermineDOD4.set_index(['Mat.-Nr.','Start', 'Menge'], inplace=True)

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
Stueli.set_index(['Material','Kurztext', 'Basismenge'], inplace=True)  #hier wird die Materialnummer der Index




print(StarttermineDOD4)
print('test')
print(Stueli)

