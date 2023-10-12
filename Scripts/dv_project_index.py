from flask import Flask,render_template,url_for,request
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

@app.route("/")
def hello():
  return render_template('index.html')
@app.route("/country_analysis")
def country_analysis():
  return render_template("country_analysis.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=False,timeVal='2021',typeVal='Export',countryVal='United States'
                         )
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
    plt.title("Tree map for proportions of categories of "+country_val +":"+type_val)
    plt.pie(sizes,labels=labels)
    #squarify.plot(sizes=sizes,label = labels,text_kwargs = {'fontsize': 7, 'color': 'white'},pad=0.2)
    #sankey(left=df['Reporter'],right=df['Partner'],rightWeight=df['2021'])
    print(f"{len(sizes)}")
    #plt.bar(labels,sizes)
    #plt.text(wrap=True)
    #plt.legend(loc='upper right')
    if os.path.exists('static/treemap.png'):
        print("entered")
        print(os.remove('static/treemap.png'))
    #plt.colorbar()
    plt.savefig(os.path.join('static','treemap2.png')) 
    return render_template("country_analysis.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         timeVal=year_val,typeVal=type_val,years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=True,countryVal=country_val
                         )
@app.route('/network_graph')
def network_graph():
  return render_template("network_graph.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],timeVal='2021',countryVal='United States',show_plot=False)
@app.route('/display_network_graph',methods=['GET','POST'])
def display_network_graph():
  if request.method=='POST':
    plt.clf()
    plt.cla()
    year_val=request.form['timeFrame2']
    country_val=request.form['country2']
    df=pd.read_csv('en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
    df=df.fillna(0)
    g=nx.DiGraph()
    g2=nx.DiGraph()
    nodes=set()
    nodes_import=set()
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
        colors.append('red')
      else:
        colors.append('blue')
    colors2=[]
    for x in nodes_import:
      print(f"import node is {x}")
      g2.add_node(x)
      if x==country_val:
        colors2.append('red')
      else:
        colors2.append('blue')
    sizes_1=[]
    for x in nodes:
      if x in exports_values:
        g.add_weighted_edges_from([(country_val,x,exports_values[x])])
        sizes_1.append(exports_values[x]/1000)
      else:
        sizes_1.append(500)
    sizes_2=[]
    for x in nodes_import:
      if x in import_values:
        g2.add_weighted_edges_from([(x,country_val,import_values[x])])
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
    plt.figure(figsize=(9,10))
    ax=plt.gca()
    plt.axis('off')
    #plt.subplot(121)
    pos_exp=nx.spring_layout(g)
    print(f"nodes positions : {pos_exp}")
    nx.draw(g,node_color=colors,pos=pos_exp,node_size=sizes_1,**options)
    #nx.draw_networkx_labels(g,pos_exp)
    for x in nodes:
      if x in exports_values:
        export_annotations[x]={'text':x+'\n'+'Total Export Value : '+'\n'+str(exports_values[x]),'pos':pos_exp[x]}
    print(f"annotations : {export_annotations}")
    for x in export_annotations:
      ax.annotate(export_annotations[x]['text'],xy=export_annotations[x]['pos'],xytext=(0, 30), textcoords='offset points',
        arrowprops=dict(facecolor='black', shrink=0.10),  
        bbox=dict(boxstyle="round", fc="cyan"))
    print(nx.spring_layout(g))
    print(g)
    '''plt.subplot(122)
    nx.draw(g2,node_color=colors2,pos=nx.spring_layout(g2,iterations=50),node_size=sizes_2,**options)'''
   
    print(import_values)
    print(exports_values)
    plt.title('network graph')
    #plt.tight_layout(pad=3.0)
    plt.savefig(os.path.join('static','networkgraph.png'))
    return render_template("network_graph.html",country_names=[{'cname':'United States'},{'cname':'Australia'}],
                         years=[{'year':'2021'},{'year':'2020'},{'year':'2019'}],timeVal=year_val,countryVal=country_val,show_plot=True)

      
          

if __name__ == "__main__":
  app.run(debug=True)

#test commit