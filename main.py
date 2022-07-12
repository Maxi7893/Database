import pandas as pd
a = 10
df = pd.read_excel('Dateien\Starttermine DOD-4_07.07.2022.xlsx')
df['Mat.-Nr.'] = df['Mat.-Nr.'].str.replace('.' , '').str[:-4]
df.set_index('Mat.-Nr.' , inplace=True)
print (df)
#print(df.dtypes)
#print(df.loc[2804970000, 'Start'])

#print(df.to_json(indent= 4)) # wird in json umgewandelt

