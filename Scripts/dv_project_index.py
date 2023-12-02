from flask import Flask,render_template,url_for,request,jsonify
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np
import pandas as pd
import csv
import json
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
import plotly
import plotly.express as px
from plotly.subplots import make_subplots
import requests

app = Flask(__name__)
country_mapping=dict()
mappings_csv=open('country_vs_code.csv','r')
reader=csv.DictReader(mappings_csv)
for row in reader:
  print(row)
  country_mapping[row['Country']]=row['Code']
print("country mappings")
print(country_mapping)
default_country='United States'
default_year=2021
default_type='Export'
default_from_year=1988
default_to_year=2021


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
  #plotting with default filters here
  valuesTosend=dict()
  valuesTosend['country']=default_country
  valuesTosend['timeFrame']=str(default_year)
  valuesTosend['Export_Import']=default_type
  root_url = request.url_root
  #return requests.post(root_url+'/display_bar_chart',json=valuesTosend)
  temp_str=requests.post(root_url+'/display_plot',valuesTosend)
  print(f"temp_str : {temp_str} , type : {type(temp_str)}, text : {temp_str.text.index('graphs')}, substring_obtained : {temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].strip()}")
  graphJSON=json.loads(temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].strip()[:-1])

  return render_template("country_analysis.html",country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':str(x)} for x in range(1988,2022)],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=False,timeVal='2021',typeVal='Export',countryVal='United States',
                        graphJSON=json.dumps(graphJSON,cls=plotly.utils.PlotlyJSONEncoder)
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
    df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv')
    df=df.fillna('0')
    product_vs_values=dict()
    for index in df.index:
      if df['Indicator Type'][index]==type_val:
        if (df['Product categories'][index]!='All Products') and ((df['Indicator Type'][index]=='Export' and df['Indicator'][index]=='Export(US$ Mil)') or (df['Indicator Type'][index]=='Import' and df['Indicator'][index]=='Import(US$ Mil)')):
          product_cat=df['Product categories'][index]
          if float(df[year_val][index])!=0.0:
            if product_cat in product_vs_values:
              product_vs_values[product_cat]=product_vs_values[product_cat]+float(df[year_val][index])
            else:
              product_vs_values[product_cat]=float(df[year_val][index])
    sizes=[]
    labels=[]
    labels2=[]
    for x in product_vs_values:
      sizes.append(product_vs_values[x])
      labels.append(x+"\n"+str(product_vs_values[x]))
      labels2.append(x)
    #saving csv intermediately
    products_transformed_df=pd.DataFrame.from_dict({'Product Category':labels2,'Net Indicator Value':sizes})
    products_transformed_df.to_csv('en_'+country_mapping[country_val]+'AllYears_WITS_Trade_Summary_transformed_treemap_task.csv')
    print(product_vs_values)
    print(f"sizes : {sizes}")
    if len(sizes)>0:
      parents=[]
      for x in labels:
        parents.append("")
      fig=go.Figure(go.Treemap(labels=labels,values=sizes,parents=parents,marker_colorscale='Blues'))
      fig.update_layout(
      title=dict(text="Tree map showing indicator values for various product categories "+type_val+"ed by "+country_val +" in the year " + year_val,automargin=True,yref='container'),
      font=dict(
        size=8,
        color="RebeccaPurple"
    )
    ) 
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    else:
      fig=go.Figure()
      fig.add_annotation(x=0.5,y=0.5,text="No data to show for selected filters")
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    print(f"{len(sizes)}")
    return render_template("country_analysis.html",country_names=[{'cname':x} for x in country_mapping],
                         timeVal=year_val,typeVal=type_val,years=[{'year':str(x)} for x in range(1988,2022)],
                        indicator_types=[{'type_val':'Export'},{'type_val':'Import'}],show_plot=True,countryVal=country_val,graphJSON=graphJSON
                         )

@app.route('/bar_chart')
def bar_chart():
  #displaying the default viz with default filters
  valuesTosend=dict()
  valuesTosend['country_name']=default_country
  root_url = request.url_root
  #return requests.post(root_url+'/display_bar_chart',json=valuesTosend)
  temp_str=requests.post(root_url+'/display_bar_chart',valuesTosend)
  print(f"temp_str : {temp_str} , type : {type(temp_str)}, text : {temp_str.text.index('graphs')}, substring_obtained : {json.loads(temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].rstrip()[:-1])}")
  graphJSON=json.loads(temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].rstrip()[:-1])
  #print(requests.post(root_url+'/display_bar_chart',valuesTosend))

  return render_template('bar_chart.html',
                         show_plot=False,
                         country_names=[{'cname':x} for x in country_mapping],
                         countryName='United States',
                         graphJSON=json.dumps(graphJSON,cls=plotly.utils.PlotlyJSONEncoder)
                         )

@app.route('/display_bar_chart',methods=['GET','POST'])
def display_bar_chart():
  if request.method=='POST':
    country_name=request.form['country_name']
    df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary.csv',encoding="latin")
    df_filtered=df[df['Indicator Type'].isin(['Import','Export']) & df['Indicator'].isin(['Export(US$ Mil)','Import(US$ Mil)','Trade (US$ Mil)-Top 5 Import Partner','Trade (US$ Mil)-Top 5 Export Partner'])]
    df_filtered=df_filtered.fillna('0') #filling missing values with zeros
    #saving filtered intermediately
    df_filtered.to_csv('en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary_filtered_bar_chart_task.csv')
    productVsValue=dict()
    for index in df_filtered.index:
      multiplier=1
      total=0
      if df_filtered['Indicator Type'][index]=='Import':
        multiplier=-1
      for i in range(1988,2022):
        total+=(multiplier*float(df_filtered[str(i)][index]))
      if df_filtered['Product categories'][index] in productVsValue:
        productVsValue[df_filtered['Product categories'][index]]=productVsValue[df_filtered['Product categories'][index]]+total
      else:
        productVsValue[df_filtered['Product categories'][index]]=total
    products=[]
    values=[]
    for x in productVsValue:
      products.append(x)
      values.append(productVsValue[x])
    df_products_summ=pd.DataFrame.from_dict({'Products':products,'Values':values})
    df_products_summ.sort_values(by=['Values'],ascending=False,inplace=True)
    df_products_summ.to_csv('en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary_transformed_bar_chart_task.csv')
    top_num=min(len(df_products_summ),5)
    print(f"top_num is : {top_num}")
    top_products=[]
    count=0
    for i in df_products_summ.index:
      top_products.append(df_products_summ['Products'][i])
      count+=1
      if count>=top_num:
        break
    df_top_products_summary=df_filtered[df_filtered['Product categories'].isin(top_products)]
    df_top_products_summary=df_top_products_summary[['Product categories','Indicator Type','Indicator','2017','2018','2019','2020','2021']]
    df_top_products_summary.to_csv('en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary_transformed_filtered_stage_2_bar_chart_task.csv')
    product_sum_dict=dict()
    for index in df_top_products_summary.index:
      multiplier=1
      if df_top_products_summary['Indicator Type'][index]=='Import':
        multiplier=-1
      if df_top_products_summary['Product categories'][index] in product_sum_dict:
        temp=product_sum_dict[df_top_products_summary['Product categories'][index]]
        for i in range(2017,2022):
          temp[i-2017]=temp[i-2017]+(multiplier*float(df_top_products_summary[str(i)][index]))
        product_sum_dict[df_top_products_summary['Product categories'][index]]=temp
      else:
        temp=[]
        for i in range(2017,2022):
          temp.append(multiplier*float(df_top_products_summary[str(i)][index]))
        if len(temp)>0:
          product_sum_dict[df_top_products_summary['Product categories'][index]]=temp
    if len(product_sum_dict)==0:
      fig=go.Figure()
      fig.add_annotation(x=0,y=0,text="No imports/exports of top 5 products in 2017-2022")
      fig.update_layout(yaxis_range=[-10,10],xaxis_range=[-10,10])
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('bar_chart.html',
                         country_names=[{'cname':x} for x in country_mapping],
                         countryName=country_name,
                         graphJSON=graphJSON
                        )


    print(f"product_sum_dict is {product_sum_dict}")
    products_array=[]
    array_2017=[]
    array_2018=[]
    array_2019=[]
    array_2020=[]
    array_2021=[]
    specs=[]
    for x in product_sum_dict:
      products_array.append(x)
      specs.append([{'type':'xy','rowspan':2}])
      specs.append([None])
      array_2017.append(product_sum_dict[x][0])
      array_2018.append(product_sum_dict[x][1])
      array_2019.append(product_sum_dict[x][2])
      array_2020.append(product_sum_dict[x][3])
      array_2021.append(product_sum_dict[x][4])
    product_sum_df=pd.DataFrame.from_dict({'Product category':products_array,'2017':array_2017,
                                           '2018':array_2018,'2019':array_2019,
                                           '2020':array_2020,'2021':array_2021})
    fig=make_subplots(rows=1,cols=1,shared_xaxes ='all')
    atleast_once=False
    for index in product_sum_df.index:
      temp_bool=False
      temp_vals=[product_sum_df[str(year)][index] for year in range(2017,2022)]
      for z in temp_vals:
        if z!=0.0:
          temp_bool=True
          atleast_once=True
          break
      if temp_bool:
        fig.add_trace(go.Bar(x=[year for year in range(2017,2022)],y=[product_sum_df[str(year)][index] for year in range(2017,2022)],showlegend=True,name=product_sum_df['Product category'][index]))
        fig.update_traces( marker={"line": {"width": 3, "color": "rgb(0,0,0)"}})
    if not(atleast_once):
      fig=go.Figure()
      fig.add_annotation(x=0,y=0,text="No imports/exports of top 5 products in 2017-2022")
      fig.update_layout(yaxis_range=[-10,10],xaxis_range=[-10,10])
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('bar_chart.html',
                         country_names=[{'cname':x} for x in country_mapping],
                         countryName=country_name,
                         graphJSON=graphJSON
                        )
    
    fig.update_layout(
      title="Bar chart showing the net indicator values of top-5 products for "+country_name+" from years 2017 to 2021",
      xaxis_title="Year",
      yaxis_title="Net indicator value in millions of USD",
      font=dict(
        size=8,
        color="RebeccaPurple"
    )
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('bar_chart.html',
                         country_names=[{'cname':x} for x in country_mapping],
                         countryName=country_name,
                         graphJSON=graphJSON
                        )
@app.route('/display_line_chart')
def display_line_chart():
  root_url = request.url_root
  temp_str=requests.post(root_url+'/plot_line_chart',{'country2':default_country,'timeFrame1':'1988','timeFrame2':'2021'})
  print(f"temp_str : {temp_str.text}")
  graphJSON=json.loads(temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].rstrip()[:-1])

  time_frames=[]
  for i in range(1988,2022):
    time_frames.append(i)
  return render_template('LineChart.html',country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':str(x)} for x in time_frames],
                         timeValFrom=str(default_from_year),
                         timeValTo=str(default_to_year),
                         countryVal=default_country,
                         graphJSON=json.dumps(graphJSON, cls=plotly.utils.PlotlyJSONEncoder)
                         )

@app.route('/plot_line_chart',methods=['GET','POST'])
def plot_line_chart():
  time_frames=[]
  for i in range(1988,2022):
    time_frames.append(i)
  if request.method=='POST':
    country_name=request.form['country2']
    start_year=request.form['timeFrame1']
    end_year=request.form['timeFrame2']
    if int(start_year)>=int(end_year):
      fig=go.Figure()
      fig.add_annotation(x=0.5,y=0.5,text="Start year should be strictly less than end year")
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('LineChart.html',country_names=[{'cname':x} for x in country_mapping],
                             countryVal=country_name,
                         years=[{'year':str(x)} for x in time_frames],
                         timeValFrom=start_year,
                         timeValTo=end_year,
                         graphJSON=graphJSON)
    else:
      df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary.csv',encoding="latin")
      net_vals_dict=dict()
      for i in range(int(start_year),int(end_year)+1):
        net_vals_dict[i]=0
      for index in df.index:
        if (df['Indicator Type'][index]=='Export' or df['Indicator Type'][index]=='Import') and (df['Indicator'][index]=='Export(US$ Mil)' or df['Indicator'][index]=='Import(US$ Mil)'):
          for x in range(int(start_year),int(end_year)+1):
            if df[str(x)][index]!=None and not(pd.isna(df[str(x)][index])):
              print(f"strindx : {str(x)}{df[str(x)][index]}")
              if df['Indicator Type'][index]=='Import':
                net_vals_dict[x]-=int(df[str(x)][index])
              else:
                net_vals_dict[x]+=int(df[str(x)][index])
      x_vals=[]
      y_vals=[]
      for y in range(int(start_year),int(end_year)+1):
        x_vals.append(y)
        y_vals.append(net_vals_dict[y])
      #saving csv intermediately
      pd.DataFrame.from_dict({'Year':x_vals,'Net indicator value':y_vals}).to_csv('en_'+country_mapping[country_name]+'_AllYears_WITS_Trade_Summary_transformed_line_task.csv')
      fig=px.line(x=x_vals,y=y_vals,labels={
        "x":"Year",
        "y":"Net indicator value in millions of USD"
      },
      title="Line chart showing the trend of Net indicator values of "+country_name+" from years "+start_year+" to "+end_year)
      fig.update_layout(
        autosize=True,
        width=800,
        height=800,
      xaxis = dict(
          tickmode = 'linear',
          tick0 = x_vals[0],
          dtick = 1
      ),font=dict(
        size=8,
        color="RebeccaPurple"
    )
    )
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('LineChart.html',country_names=[{'cname':x} for x in country_mapping],
                             countryVal=country_name,
                         years=[{'year':str(x)} for x in time_frames],
                         timeValFrom=start_year,
                         timeValTo=end_year,
                         graphJSON=graphJSON)
    

@app.route('/network_graph')
def network_graph():
  years=[]
  for i in range(1988,2022):
    years.append(i)
  #plotting default map
  values_to_send=dict()
  values_to_send['country2']=default_country
  values_to_send['timeFrame2']=default_year
  values_to_send['ImportOrExport']=default_type
  root_url = request.url_root
  #return requests.post(root_url+'/display_bar_chart',json=valuesTosend)
  temp_str=requests.post(root_url+'/display_network_graph_with_plotly',values_to_send)
  print(f"temp_str : {temp_str} , type : {type(temp_str)}, text : {temp_str.text.index('graphs')}, substring_obtained : {temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].rstrip()[:-1]}")
  graphJSON=json.loads(temp_str.text[temp_str.text.index('graphs =')+8:temp_str.text.index('Plotly')].rstrip()[:-1])
  return render_template("network_graph.html",
                         country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':str(x)} for x in years],timeVal='2021',countryVal='United States',
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal='Export',
                         graphJSON=json.dumps(graphJSON,cls=plotly.utils.PlotlyJSONEncoder))
    
@app.route('/display_network_graph_with_plotly',methods=['GET','POST'])
def display_network_graph_with_plotly():
  years=[]
  for i in range(1988,2022):
    years.append(i)
  if request.method=='POST':
    year_val=request.form['timeFrame2']
    country_val=request.form['country2']
    impoorexp=request.form['ImportOrExport']
    fig=go.Figure()
    fig.layout=go.Layout(title=go.layout.Title(text="Below network graph shows the countries with which "+country_val+' '+impoorexp+'ed '+'in year '+str(year_val)+"\n"+". The text on hovering on node shows the name of country and value of "+impoorexp+" in millions of USD"),  autosize=False,
    width=900,
    height=900)
    outward=False
    if impoorexp=='Export':
      outward=True
    df=pd.read_csv('wits_en_trade_summary_allcountries_allyears/en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary.csv',encoding="latin")
    df=df.fillna(0)
    g=nx.DiGraph()
    indicator_vals_dict=dict()
    nodes=set()
    nodes.add(country_val)
    sizes=dict()
    colors=dict()
    indicator_types_dict=dict()
    indicator_types_dict['Export']=['Export(US$ Mil)','Trade (US$ Mil)-Top 5 Export Partner']
    indicator_types_dict['Import']=['Import(US$ Mil)','Trade (US$ Mil)-Top 5 Import Partner']
    for index in df.index:
      if df[year_val][index]!=0 and df[year_val][index]!=None and not(pd.isna(df[year_val][index])) and df['Indicator Type'][index]==impoorexp and df['Indicator'][index] in indicator_types_dict[impoorexp] and df['Partner'][index]!=None:
        nodes.add(df['Partner'][index])
        if df['Partner'][index] in indicator_vals_dict:
          indicator_vals_dict[df['Partner'][index]]=indicator_vals_dict[df['Partner'][index]]+float(df[year_val][index])
        else:
          indicator_vals_dict[df['Partner'][index]]=float(df[year_val][index])
    if len(indicator_vals_dict)==0:
      fig.add_annotation(x=0.5,y=0.5,text="No data to show for the selected filters")
      graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      return render_template('network_graph.html',country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':str(x)} for x in years],timeVal=year_val,countryVal=country_val,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal=impoorexp,graphJSON=graphJSON)
    print(f"nodes are : {nodes}")
    print(f"indicator values dict is : {indicator_vals_dict}")
    for x in nodes:
      g.add_node(x)
      if x in indicator_vals_dict:
        if outward:
          g.add_edge(country_val,x,length=5)
        else:
          g.add_edge(x,country_val,length=5)
        sizes[x]=math.log(indicator_vals_dict[x])*5
        colors[x]='blue'
      else:
        sizes[x]=50
        colors[x]='red'
    options = {
    'edge_color': 'black',
    'width': 1,
    'with_labels': False,
    'font_weight': 'regular',
    }
    #saving csv intermediately
    csv_col_1=[]
    csv_col_2=[]
    for key in indicator_vals_dict:
      csv_col_1.append(key)
      csv_col_2.append(indicator_vals_dict[key])
    if len(csv_col_1)>0:
      pd.DataFrame.from_dict({'Country':csv_col_1,'Indicator Value':csv_col_2}).to_csv('en_'+country_mapping[country_val]+'_AllYears_WITS_Trade_Summary_transformed_network_graph_task.csv')
    print(f"graph is : {g}")
    pos=nx.circular_layout(g,center=(0,0))
    print(f"positions are : {pos}")
    edge_x=[]
    edge_y=[]
    locations=dict()
    colors_network=[]
    sizes_network=[]
    nodes_annotations=[]
    nodes_text=[]
    for edge in g.edges():
      print(f"current edge is {edge}")
      #x_0,y_0=g.nodes[edge[0]]['pos']
      x_0,y_0=pos[edge[0]]
      print(f"before locations : {x_0},{y_0}")
      locations[str(x_0)+","+str(y_0)]=edge[0]
      #x_1,y_1=g.nodes[edge[1]]['pos']
      x_1,y_1=pos[edge[1]]
      locations[str(x_1)+","+str(y_1)]=edge[1]
      print(f"x_0,y_0,x_1,y_1 are  : {x_0},{y_1},{x_1},{y_1}")
      edge_x.append(x_0)
      edge_x.append(x_1)
      edge_y.append(y_0)
      edge_y.append(y_1)
    print(f"edge_x is {edge_x}")
    print(f"edge_y :{edge_y}")
    print(f"locations are : {locations}")
    for i in range(len(edge_x)):
      temp=str(edge_x[i])+","+str(edge_y[i])
      #print(f"616 : {locations[temp]}")
      colors_network.append(colors[locations[str(edge_x[i])+","+str(edge_y[i])]])
      sizes_network.append(sizes[locations[temp]])
      temp_text=locations[temp]
      nodes_text.append(locations[temp])
      if locations[temp] in indicator_vals_dict:
        temp_text+="\n"
        temp_text+=str(indicator_vals_dict[locations[temp]])
      nodes_annotations.append(temp_text)
      
    edge_trace=[go.Scatter(
      x=edge_x, y=edge_y,mode='markers+lines+text',hoverinfo='text',text=nodes_text,textposition='top right',marker=dict(size=sizes_network,color=colors_network)
    )]
    edge_trace[0].text=nodes_annotations
    print(f"edge_trace is : {edge_trace}")
    for trace1 in edge_trace:
      print(trace1)
      fig.add_trace(trace1)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    fig.update_layout(
      title="Below network graph shows the countries with which "+country_val+' '+impoorexp+'ed '+'in year '+str(year_val),
      font=dict(
        size=8,
        color="RebeccaPurple"
    ),width=800,
    height=800
    )
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('network_graph.html',country_names=[{'cname':x} for x in country_mapping],
                         years=[{'year':str(x)} for x in years],timeVal=year_val,countryVal=country_val,
                         importExportType=[{'imporexp':'Import'},{'imporexp':'Export'}],impVal=impoorexp,graphJSON=graphJSON)
@app.route('/homePage')
def homePage():
  return render_template("index.html")
if __name__ == "__main__":
  app.run(debug=True)

#test commit
