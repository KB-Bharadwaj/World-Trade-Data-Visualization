from flask import Flask,render_template,url_for,request
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import pandas as pd
#import json
#from anytree import PostOrderIter
#from anytree.importer import DictImporter
#import ipywidgets as widgets
#import plotly.graph_objs as go
import squarify
import os
import math
#import sankey
import networkx as nx
app = Flask(__name__)
country_mapping=dict()
country_mapping['United States']='USA'
country_mapping['Australia']='AUS'
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
  return render_template("country_analysis.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
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
    df=pd.read_csv('en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
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
    return render_template("country_analysis.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         timeVal=year_val,typeVal=type_val,years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=True,countryVal=country_val
                         )
@app.route('/network_graph')
def network_graph():
  return render_template("network_graph.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
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
    df=pd.read_csv('en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
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
    return render_template("network_graph.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],timeVal=year_val,countryVal=country_val,show_plot=True,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal=impoorexp)

      
          
@app.route('/homePage')
def homePage():
  return render_template("index.html")
if __name__ == "__main__":
  app.run(debug=True)

#test commit
