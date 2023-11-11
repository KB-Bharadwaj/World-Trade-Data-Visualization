from flask import Flask,render_template,url_for,request
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import pandas as pd
import csv
import json
#from anytree import PostOrderIter
#from anytree.importer import DictImporter
#import ipywidgets as widgets
import plotly
import plotly.graph_objs as go
import squarify
import os
import math
import pySankey.sankey as sankey
import networkx as nx
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import pandas as pd

app = Flask(__name__)
country_mapping=dict()
mappings_csv=open('country_vs_code.csv','r')
reader=csv.DictReader(mappings_csv)
for row in reader:
  print(row)
  country_mapping[row['Country']]=row['Code']
print("country mappings")
print(country_mapping)


matplotlib.use('agg')
#with open('flare.json') as f:
#    js_data = json.loads(f.read())
#importer = DictImporter()
#root = importer.import_(js_data)


@app.route("/")
def hello():
  return render_template('index.html')
@app.route("/country_analysis")
def country_analysis():
  return render_template("country_analysis.html",country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=False,timeVal='2021',typeVal='Export',countryVal='United States'
                         )
#@app.route('/display_treemap', methods='GET', 'POST'])
#def display_treemap():
#    if request.method=='POST':
#        year_val=request.form['timeFrame']
#        country_val=request.form['country']
#        type_val=request.form['Export_Import']
#        print(f"year : {year_val} , country:{country_val}, type: {type_val}")
#        df=pd.read_csv('en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
#        df=df.fillna('0')
#        parent = []
#        child = []
#        for i in df.i:
#            if (df['Indicator Type'][i]==type_val):
#                if (df['Parent'][i] not in parent):
#                    parent.append(df['Parent'][i])

@app.route('/display_plot',methods=['GET','POST'])
def display_plot():
  plt.clf()
  plt.cla()
  print("in display plot")
  if request.method=='POST':
    year_val=request.form['timeFrame']
    country_val=request.form['country']
    type_val=request.form['Export_Import']
    print(f"year : {year_val} , country:{country_val}, type: {type_val}")
    df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
    df=df.fillna('0')
    product_vs_values=dict()
    for index in df.index:
      if df['Indicator Type'][index]==type_val:
        if (df['Indicator Type'][index]=='Export' and df['Indicator'][index]=='Export(US$ Mil)') or (df['Indicator Type'][index]=='Import' and df['Indicator'][index]=='Import(US$ Mil)'):
          product_cat=df['Product categories'][index]
          if product_cat in product_vs_values:
            product_vs_values[product_cat]=product_vs_values[product_cat]+df[year_val][index]
          else:
            product_vs_values[product_cat]=df[year_val][index]
    sizes=[]
    labels=[]
    for x in product_vs_values:
      sizes.append(product_vs_values[x])
      labels.append(x+"\n"+str(product_vs_values[x]))
    print(product_vs_values)
    print(f"sizes : {sizes}")
    plt.figure(figsize=(10, 10))
    plt.grid(False)
    plt.axis("off")
    plt.title("Tree map for proportions of categories of "+country_val +" in the year " + year_val + ": "+type_val)
    #plt.pie(sizes,labels=labels)
    #squarify.plot(sizes=sizes, color=sb.color_palette("tab20", len(sizes)), pad=1, text_kwargs={'fontsize': 14})
    squarify.plot(sizes=sizes, label=labels, color=sb.color_palette("tab20", len(sizes)), pad=1, text_kwargs={'fontsize': -1})
    #squarify.plot(sizes=sizes,label = labels,text_kwargs = {'fontsize': 7, 'color': 'white'},pad=0.2)
    #sankey(left=df['Reporter'],right=df['Partner'],rightWeight=df['2021'])
    print(f"{len(sizes)}")
    #plt.bar(labels,sizes)
    #plt.text(wrap=True)
    plt.legend(loc = 'center left', bbox_to_anchor = (1, .5), ncol = 2)
    if os.path.exists('static/treemap.png'):
        print("entered")
        print(os.remove('static/treemap.png'))
    #if os.path.exists('static/treemap_legend.png'):
     #   print("entered")
      #  print(os.remove('static/treemap_legend.png'))
    #plt.colorbar()
    plt.savefig(os.path.join('static','treemap2.png'), bbox_inches='tight')
    #legend.savefig(os.path.join('static', 'treemap_legend.png'))
    return render_template("country_analysis.html",country_names=[{'cname':x} for x in country_mapping],
                         timeVal=year_val,typeVal=type_val,years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=True,countryVal=country_val
                         )
@app.route('/network_graph')
def network_graph():
  return render_template("network_graph.html",#country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],timeVal='2021',countryVal='United States',show_plot=False,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal='Import')
@app.route('/display_network_graph',methods=['GET','POST'])
def display_network_graph():
  if request.method=='POST':
    plt.clf()
    plt.cla()
    year_val=request.form['timeFrame2']
    country_val=request.form['country2']
    impoorexp=request.form['ImportOrExport']
    df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
    df=df.fillna(0)
    g=nx.DiGraph()#export graph
    g2=nx.DiGraph()#import graph
    nodes=set()#export nodes
    nodes_import=set()#import nodes
    exports_values=dict()
    import_values=dict()
    import_annotations=dict()
    export_annotations=dict()
    for index in df.index:
      if (df[year_val][index]!=0.0 ) and (df['Indicator Type'][index]=='Export') and (df['Indicator'][index]=='Export(US$ Mil)' or df['Indicator'][index]=='Trade (US$ Mil)-Top 5 Export Partner'):
        nodes.add(df['Reporter'][index])
        nodes.add(df['Partner'][index])
        if df['Partner'][index] in exports_values:
          exports_values[df['Partner'][index]]=exports_values[df['Partner'][index]]+df[year_val][index]
        else:
          exports_values[df['Partner'][index]]=df[year_val][index]
      if(df[year_val][index]!=0.0) and (df['Indicator Type'][index]=='Import') and (df['Indicator'][index]=='Import(US$ Mil)' or df['Indicator'][index]=='Trade (US$ Mil)-Top 5 Import Partner'):
        nodes_import.add(df['Partner'][index])
        nodes_import.add(df['Reporter'][index])
        if df['Partner'][index] in import_values:
          import_values[df['Partner'][index]]=import_values[df['Partner'][index]]+df[year_val][index]
        else:
          import_values[df['Partner'][index]]=df[year_val][index]
    colors=[]
    for x in nodes:
      print(f"node is {x}")
      g.add_node(x)
      if x==country_val:
        colors.append('red')#target country
      else:
        colors.append('blue')#other countries
    colors2=[]
    for x in nodes_import:
      print(f"import node is {x}")
      g2.add_node(x)
      if x==country_val:
        colors2.append('red')#target country
      else:
        colors2.append('blue')#other countries
    sizes_1=[]
    for x in nodes:
      if x in exports_values:
        g.add_edge(country_val,x,length=5)
        #g.add_edges_from([(country_val,x)])
        sizes_1.append(exports_values[x]/1000)
      else:
        sizes_1.append(500)
    sizes_2=[]
    for x in nodes_import:
      if x in import_values:
        #g2.add_edges_from([(x,country_val)])
        g2.add_edge(x,country_val,length=5)
        sizes_2.append(import_values[x]/1000)
      else:
        sizes_2.append(500)
    
    options = {
    'edge_color': 'black',
    'width': 1,
    'with_labels': False,
    'font_weight': 'regular',
    } 
    plt.clf()
    plt.figure(figsize=(9,9))
    plt.axis('off')
    #plt.subplot(121)
    pos_exp=nx.circular_layout(g,center=(0,0))
    pos_imp=nx.circular_layout(g2)
    print(f"nodes positions : {pos_exp}")
    if impoorexp=='Export':
      plt.clf()
      plt.cla()
      ax=plt.gca()
      nx.draw(g,node_color=colors,pos=pos_exp,node_size=sizes_1,**options)
      for x in nodes:
        if x in exports_values:
          export_annotations[x]={'text':x+'\n'+'Total Export Value : '+'\n'+str(exports_values[x]),'pos':pos_exp[x]}
        else:
          export_annotations[x]={'text':x,'pos':pos_exp[x]}
      print(f"annotations : {export_annotations}")
      for x in export_annotations:
        ax.annotate(export_annotations[x]['text'],xy=export_annotations[x]['pos'],xytext=(0, 30), textcoords='offset points',
          arrowprops=dict(facecolor='black', shrink=0.10),  
          bbox=dict(boxstyle="round", fc="cyan"))
      print(g)
      plt.title('Network graph of '+country_val+' \'s'+' exports in year '+year_val,y=-0.01)
    else:
      plt.clf()
      plt.cla()
      ax=plt.gca()
      nx.draw(g2,node_color=colors2,pos=pos_imp,node_size=sizes_2,**options)
      for x in nodes_import:
        if x in import_values:
          import_annotations[x]={'text':x+'\n'+'Total Import Value: '+'\n'+str(import_values[x]),'pos':pos_imp[x]}
        else:
          import_annotations[x]={'text':x,'pos':pos_imp[x]}
      for x in import_annotations:
        ax.annotate(import_annotations[x]['text'],xy=import_annotations[x]['pos'],xytext=(0,30),textcoords='offset points',
                     arrowprops=dict(facecolor='black', shrink=0.10),  
          bbox=dict(boxstyle="round", fc="cyan"))
      plt.title('Network graph of '+country_val+' \'s'+' imports in year '+year_val,y=-0.01)
   
    print(f"*****{impoorexp} ******* {import_annotations}**** {import_values}")
    print(exports_values)
    #plt.tight_layout(pad=3.0)
    plt.savefig(os.path.join('static','networkgraph.png'))
    return render_template("network_graph.html",country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],timeVal=year_val,countryVal=country_val,show_plot=True,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal=impoorexp)

@app.route('/map_viz')
def map_viz():
  return render_template("map_viz.html",
                         country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                         show_plot=False,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}]
                         )

@app.route('/display_geographic_map',methods=['GET','POST'])
def display_geographic_map():
  if(request.method=='POST'):
    plt.clf()
    plt.cla()
    country_val=request.form['country2']
    year_val=request.form['timeFrame2']
    imp_exp=request.form['ImportOrExport']
    ind_values=dict()
    ind_values['Export']=['Export(US$ Mil)','Trade (US$ Mil)-Top 5 Export Partner']
    ind_values['Import']=['Import(US$ Mil)','Trade (US$ Mil)-Top 5 Import Partner']
    '''for f in os.listdir('wits_en_trade_summary_allcountries_allyears'):
      with open('wits_en_trade_summary_allcountries_allyears/'+f) as currfile:
        df=pd.read_csv(currfile)
        if len(df)>0:
          curr_country_name=df.iloc[0]['Reporter']
          for index in range(len(df)):
            if df.iloc[index]['Indicator Type']==imp_exp and df.iloc[index]['Indicator'] in ind_values[imp_exp] and pd.notnull(df.iloc[index][year_val]) and pd.notna(df.iloc[index][year_val]):
              if curr_country_name in country_prods_dict:
                temp=country_prods_dict[curr_country_name]
                if df.iloc[index]['Product categories'] in temp:
                  temp[df.iloc[index]['Product categories']]=temp[df.iloc[index]['Product categories']]+df.iloc[index][year_val]
                else:
                  temp[df.iloc[index]['Product categories']]=df.iloc[index][year_val]
                country_prods_dict[curr_country_name]=temp
              else:
                country_prods_dict[curr_country_name]={df.iloc[index]['Product categories']:df.iloc[index][year_val]}'''
    products_dict=dict()
    with open('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv') as currfile:
      curr_pd=pd.read_csv(currfile)
      curr_pd=curr_pd.dropna(subset=['Product categories',str(year_val),'Indicator Type','Indicator'])
      print(curr_pd.head())
      if len(curr_pd)>0:
        for i in range(len(curr_pd)):
          if curr_pd.iloc[i]['Indicator Type']==imp_exp and curr_pd.iloc[i]['Indicator'] in ind_values[imp_exp] and pd.notnull(curr_pd.iloc[i][year_val] and pd.notna(curr_pd.iloc[i][year_val])):
            curr_prod_cat=curr_pd.iloc[i]['Product categories']
            if curr_prod_cat in products_dict:
              products_dict[curr_prod_cat]=products_dict[curr_prod_cat]+curr_pd.iloc[i][year_val]
            else:
              products_dict[curr_prod_cat]=curr_pd.iloc[i][year_val]
    countries=[]
    products=[]
    values=[]
    data_san=[]
    labels_san=[]
    labels_san.append(country_val)
    for prod in products_dict:
      countries.append(country_val)
      products.append(prod+":"+"\n"+str(products_dict[prod]))
      labels_san.append(prod)
      values.append(products_dict[prod])
    aggr_data_frame=pd.DataFrame({'Country':countries,'Product':products,'Total value':values})
    print(aggr_data_frame)
    if len(aggr_data_frame)>0:
      sankey.sankey(
          left=aggr_data_frame['Country'], right=aggr_data_frame['Product'], 
          leftWeight= aggr_data_frame['Total value'], rightWeight=aggr_data_frame['Total value'],
          aspect=10,fontsize=7
      )
      data_san.append([go.sankey(
        node=dict(
          pad=15,
          thickness=20,
          line = dict(color = "black", width = 0.5),
          label = aggr_data_frame['Country'],
          color = "blue"
        )
      )])
    else:
      plt.annotate("No data to show for selected year",[0,0])
    plt.axis('off')
    plt.show()
    plt.savefig(os.path.join('static','mapViz.png'))
    
    return render_template('map_viz.html', timeVal=year_val,impVal=imp_exp,countryVal=country_val,
                           years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                           country_names=[{'cname':x} for x in country_mapping],
                           show_plot=True,
                           importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}])
  
@app.route('/bar_chart')
def bar_chart():
  product_categories=['All products',
                        'Animal','Vegetable','Food Products',
                        'Minerals','Fuels','Chemicals','Plastic or Rubber','Hides and Skins',
                        'Wood','Textiles and Clothing','Footwear','Stone and Glass',
                        'Metals','Mach and Elec','Transportation','	Miscellaneous',
                        'Capital goods','Consumer goods','Intermediate goods','Raw materials',
                        'Agricultural Raw Materials','Chemical','Food','Fuel','Manufactures',
                        'Ores and Metals','Textiles','Machinery and Transport Equipment']
  years_list=[]
  for i in range(1988,2022):
    years_list.append(i)
  return render_template('bar_chart.html',
                         show_plot=False,
                         product_names=[{'pname':x} for x in product_categories],
                         years=[{'year':str(x)} for x in years_list],
                         timeVal='2021',
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],
                         impVal='Export'
                         )

@app.route('/display_bar_chart',methods=['GET','POST'])
def display_bar_chart():
  product_categories=['All products',
                        'Animal','Vegetable','Food Products',
                        'Minerals','Fuels','Chemicals','Plastic or Rubber','Hides and Skins',
                        'Wood','Textiles and Clothing','Footwear','Stone and Glass',
                        'Metals','Mach and Elec','Transportation','	Miscellaneous',
                        'Capital goods','Consumer goods','Intermediate goods','Raw materials',
                        'Agricultural Raw Materials','Chemical','Food','Fuel','Manufactures',
                        'Ores and Metals','Textiles','Machinery and Transport Equipment']
  years_list=[]
  for i in range(1988,2022):
    years_list.append(i)
  if request.method=='POST':
    plt.clf()
    plt.cla()
    product_name=request.form['Product']
    year_val=request.form['timeFrame3']
    imporexp=request.form['ImportOrExport']
    summary_curr_dict=dict()
    with open("product_summaries.json") as json_file:
      product_summary_dict=json.load(json_file)
      #print(f"summary dict is : {product_summary_dict[product_name]}")
      if product_name not in product_summary_dict:
        plt.clf()
        plt.cla()
        plt.annotate('No data to show for selected filters',[0.4,0.4])
        plt.axis('off')
      else:
        list_vals=product_summary_dict[product_name]
        for x in list_vals:
          if x[3]==imporexp and x[2]==str(year_val):
            if x[0] in summary_curr_dict:
              summary_curr_dict[x[0]]=summary_curr_dict[x[0]]+float(x[5])
            else:
              summary_curr_dict[x[0]]=float(x[5])
      if len(summary_curr_dict)==0:
        plt.clf()
        plt.cla()
        plt.annotate('No data to show for selected filters',[0.4,0.4])
        plt.axis('off')
      else:
        #print(f"product summary dictionary is : {summary_curr_dict}")
        all_values=[]
        for x in summary_curr_dict:
          if x.strip()!='World' and len(x)>0:
            if x in summary_curr_dict and summary_curr_dict[x]>0:
              all_values.append((x,summary_curr_dict[x]))
        all_values.sort(key=lambda x:x[1])
        #print(f"all_values : {all_values}")
        if len(all_values)==0:
          plt.clf()
          plt.cla()
          plt.annotate('No data to show for selected filters',[0.4,0.4])
          plt.axis('off')
        elif len(all_values)>0 and len(all_values)<=10:
          x_axis=list(range(len(all_values)))
          heights=[]
          x_vals=[]
          for x in all_values:
            heights.append(x[1])
            x_vals.append(x[0])
          #print(f"heights : {heights}, x_vals: {x_vals},x_axis : {x_axis}")
          plt.bar(x_axis,height=heights)
          plt.xticks(x_axis,x_vals,rotation='vertical',fontsize=10)
        else:
          start=0
          list_ranges=[]
          while start<len(all_values):
            temp=[start,min(start+9,len(all_values)-1)]
            list_ranges.append(temp)
            start=temp[1]+1
          #print(f"list_ranges are : {list_ranges}")
          numrows=math.ceil(len(list_ranges)/3)
          numcols=3
          fig,axs=plt.subplots(numrows,numcols,figsize=(40,40),sharex=True,sharey=True,subplot_kw=dict(projection="polar"))
          axs[0, 0].set_xticks([])
          #print(f"axs : {len(axs)}, type: {type(axs)}")
          for row in range(numrows):
            for col in range(numcols):
              if row*numcols+col<len(list_ranges):
                curr_range_start=list_ranges[row*numcols+col][0]
                curr_range_end=list_ranges[row*numcols+col][1]
                heights_curr=[]
                x_vals=[]
                for ind in range(curr_range_start,curr_range_end+1):
                  x_vals.append(all_values[ind][0])
                  heights_curr.append(all_values[ind][1])
                x_axis=list(range(len(x_vals)))
                #print(f"x_axis values are : {x_axis}, x_vals are : {x_vals}")
                fig.add_subplot(numrows,numcols,row*numcols+col+1)
                plt.bar(x_axis,height=heights_curr)
                plt.xticks(x_axis,x_vals,rotation='vertical',fontsize=20)
              else:
                axs[row,col].remove()
      #axs[0].tick_params(axis='x',visible=False)
      plt.tight_layout()
      plt.suptitle(print("Bar plot shows the {imporexp} of all countries in year {year_val} for product category {product_name} \n Spatial posiion on X-axis encodes country names and spatial position on Y-axis is used to encode {imporexp} value is millions of USD"))
      plt.show()
      plt.savefig(os.path.join('static','bargraph.png'),bbox_inches="tight")
  return render_template('bar_chart.html',show_plot=True,
                         productName=product_name,
                         product_names=[{'pname':x} for x in product_categories],
                         years=[{'year':str(x)} for x in years_list],
                         timeVal=year_val,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],
                         impVal=imporexp
                         )



          
@app.route('/homePage')
def homePage():
  return render_template("index.html")
if __name__ == "__main__":
  app.run(debug=True)

#test commit
