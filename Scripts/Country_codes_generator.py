import os
import pandas as pd
import csv
out_file=open('country_vs_code.csv','w+')
headers=['Country','Code']
writer=csv.DictWriter(out_file,fieldnames=headers)
writer.writeheader()
for f in os.listdir('wits_en_at-a-glance_allcountries_allyears (1)'):
    curr={}
    curr_file=open('wits_en_at-a-glance_allcountries_allyears (1)/'+f,encoding="latin")
    curr_name=curr_file.name
    print(curr_name)
    df_curr=pd.read_csv(curr_file)
    index_1=curr_name.index('/en_')
    index_2=curr_name.index('_At-a-Glance.csv')
    country_code=curr_name[index_1+4:index_2]
    if len(df_curr)>0:
        country_name_str=df_curr.iloc[0]['Reporter']
        curr['Country']=country_name_str
        curr['Code']=country_code
        writer.writerow(curr)
out_file.flush()
