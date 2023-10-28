import streamlit as st
import pandas as pd
import plotly.express as px
from geojson import Feature, FeatureCollection
from shapely import wkt
import json

st.set_page_config(
    page_title="Прогнозирование опасностей и рисков Пермского края",
    page_icon="🚒", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None,'Report a bug': None,'About': None})

hide_streamlit_style = """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

def hexagons_dataframe_to_geojson(df_hex, hex_id_field, geometry_field, value_field, file_output=None):

    list_features = []
    for i, row in df_hex.iterrows():
        feature = Feature(geometry=row[geometry_field],
                          id=row[hex_id_field],
                          properties={"value": row[value_field]})
        list_features.append(feature)

    feat_collection = FeatureCollection(list_features)

    if file_output is not None:
        with open(file_output, "w") as f:
            json.dump(feat_collection, f)
    else :
        return feat_collection

@st.cache_data
def load_data():
    '''Загрузка файла'''
    region = pd.read_csv('app/data/df_region.csv')
    region['geometry'] = region['geometry'].apply(wkt.loads)
    predict = pd.read_csv('app/data/predict.csv')
    data = predict.merge(region)
    return data

danger = {'Аварии на автомобильном транспорте': 'is_dtp', 'Аварии на прочем транспорте': 'is_transport',
          'Взрывы/пожары': 'is_fire', 'Аварии с выбросом опасных веществ': 'is_toxic',
          'Биологическая опасность': 'is_bio', 'Опасные природные явления': 'is_nature',
          'Аварии на системах жизнеобеспечения': 'is_zkh', 'Прочие опасности': 'is_etc'}

#===================================================================================
# Загрузка данных из csv файла
data=load_data()
dates=data.date.unique().tolist()

choice=st.selectbox('Выберите тип опасности', list(danger.keys()))
choice_value=danger[choice]
choice_date=st.select_slider('Выберите день', options=dates)

df=data[data.date==choice_date]

geojson_obj=(hexagons_dataframe_to_geojson(df, hex_id_field='district', value_field=choice_value,
                                           geometry_field='geometry'))

# Диапазоны для зеленого, желтого и красного
color_scale = [[0, 'green'], [0.33, 'green'],
               [0.34, 'yellow'], [0.67, 'yellow'],
                [0.68, 'red'], [1, 'red']]

fig = (px.choropleth_mapbox(
                    df,
                    geojson=geojson_obj,
                    locations='district',
                    color=choice_value,
                    color_continuous_scale=color_scale,
                    mapbox_style='carto-positron',
                    zoom=5,
                    center={"lat": 59.02968, "lon": 56.26679},
                    opacity=0.7,
                    labels={'count'}))

fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
fig.update_layout(height=800)
st.title('Географическая карта региона')
st.plotly_chart(fig, use_container_width=True, width=800, height=800)
