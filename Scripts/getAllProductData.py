import os
import csv
import json
#here just wrote all the products from trade data website
all_product_categories=['All products',
                        'Animal','Vegetable','Food Products',
                        'Minerals','Fuels','Chemicals','Plastic or Rubber','Hides and Skins',
                        'Wood','Textiles and Clothing','Footwear','Stone and Glass',
                        'Metals','Mach and Elec','Transportation','	Miscellaneous',
                        'All Products','Capital goods','Consumer goods','Intermediate goods','Raw materials',
                        'Agricultural Raw Materials','Chemical','Food','Fuel','Manufactures',
                        'Ores and Metals','Textiles','Machinery and Transport Equipment']
#now for each product, I will iterate through all country summary files and get product summary
#product name ; year ;Reporter;partner; import/export ; indicator type (million $ or top-5 export/import partner etc.); indicator value
all_products_dict=dict()
for f in os.listdir('wits_en_trade_summary_allcountries_allyears'):
    with open('wits_en_trade_summary_allcountries_allyears/'+f,encoding="latin") as currfile:
        reader=csv.DictReader(currfile)
        for row in reader:
            indicatorType=row['Indicator Type']
            indicator=row['Indicator']
            prod_cat=row['Product categories']
            if indicatorType!=None and (indicatorType=='Export' or indicatorType=='Import') and prod_cat!=None and prod_cat!='...':
                if indicator!=None and (indicator=='Export(US$ Mil)' or indicator=='Trade (US$ Mil)-Top 5 Export Partner' or indicator=='Import(US$ Mil)' or indicator=='Trade (US$ Mil)-Top 5 Import Partner'):
                    for year in range(1988,2022):
                        if row[str(year)]!=None and row[str(year)]!="":
                            if prod_cat not in all_products_dict:
                                all_products_dict[prod_cat]=[[row['Reporter'],row['Partner'],str(year),indicatorType,indicator,row[str(year)].strip()]]
                            else:
                                temp=all_products_dict[prod_cat]
                                temp.append([row['Reporter'],row['Partner'],str(year),indicatorType,indicator,row[str(year)].strip()])
                                all_products_dict[prod_cat]=temp
with open("product_summaries.json",'w') as outfile:
    json.dump(all_products_dict,outfile)

                        

    
