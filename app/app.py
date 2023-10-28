import streamlit as st
import pandas as pd
import plotly.express as px
from geojson import Feature, FeatureCollection
from shapely import wkt
import json


def hexagons_dataframe_to_geojson(df_hex, hex_id_field, geometry_field, value_field, file_output=None):

    list_features = []

    for i, row in df_hex.iterrows():
        feature = Feature(geometry = row[geometry_field],
                          id = row[hex_id_field],
                          properties = {"value": row[value_field]})
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)
    else :
        return feat_collection

#===================================================================================
# Загрузка данных из csv файла
region = pd.read_csv('app/data/df_region.csv')
region['geometry'] = region['geometry'].apply(wkt.loads) 

choice_value = 'Сетей теплоснабжения'

geojson_obj = (hexagons_dataframe_to_geojson(region, hex_id_field='district', value_field=choice_value, geometry_field='geometry'))

fig = (px.choropleth_mapbox(
                    region, 
                    geojson=geojson_obj, 
                    locations='district', 
                    color=choice_value,
                    color_continuous_scale="Viridis",
                    #range_color=(0, itog_table_g['count'].mean()),                  
                    mapbox_style='carto-positron',
                    zoom=5,
                    center = {"lat": 58.02968, "lon": 56.26679},
                    opacity=0.7,
                    labels={'count'}))

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.title('Географическая карта региона')
st.plotly_chart(fig, use_container_width=True, width=1000, height=800)
