#!/usr/bin/env python
# coding: utf-8

# In[3]:


import numpy as np
import osmnx as ox, networkx as nx, geopandas as gpd, matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from folium import plugins
from folium.plugins import MarkerCluster
import json
import urllib.request
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from geopy.geocoders import Nominatim
from shapely.geometry import Point, Polygon, LineString
from descartes import PolygonPatch
import requests
import pickle
import streamlit as st
from streamlit_folium import folium_static
import folium
import gzip
import urllib
ox.config(use_cache=True, log_console=True)


# In[4]:


if not st:
    raise importError('streamlit을 설치해 주세요.')


# In[5]:


def getLatLng(addr): #카카오 API를 이용하여 주소를 위도 경도를 반환합니다.
    try:
        url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query='+addr
        headers = {"Authorization": "KakaoAK 84ba6228f2f7a5f35ca89b1c459849ec"}
        result = json.loads(str(requests.get(url,headers=headers).text))
        x = float(result['documents'][0]['x']) # 경도 - x축 기준
        y = float(result['documents'][0]['y']) # 위도 - y축 기준
        return (y,x)
        
    except:
        return -1


# In[2]:


st.title('2020 데이터 청년 캠퍼스 2조 PINEAT 입니다.')
st.header('주제 : 따릉이 예상 이동 경로를 통한 푸드 트럭 입지 선정')
st.subheader('최대 2분 정도의 시간이 소요됩니다. 잠시만 기다려 주세요!')

with gzip.open('서울따릉이프로젝트그래프(압축버전).pickle','rb') as f:
    Seoul_Map = pickle.load(f)

with gzip.open('서울따릉이노드(압축버전).pickle','rb') as f:
    Seoul_node = pickle.load(f)
    
with gzip.open('서울따릉이엣지(압축버전).pickle','rb') as f:
    Seoul_edge = pickle.load(f)
        
start = st.text_input("시작점을 입력하세요")

arrive = st.text_input("도착지를 입력하세요.")

if st.button("확인", key='arrive'):
    result = arrive.title()
    st.success('출발지 : ' + start + '        ' + '도착지 : ' + result)
    a = getLatLng(start)
    b = getLatLng(arrive)

    st.text('계산중입니다.')
    
    m = folium.Map(location=[37.55, 126.97], zoom_start=11.5)
    orig_node = ox.get_nearest_node(Seoul_Map, (a[0], a[1])) #시작점
    dest_node = ox.get_nearest_node(Seoul_Map, (b[0], b[1])) #시작점에서 따릉이 주소
    
    
    path = nx.shortest_path(Seoul_Map, orig_node, dest_node, weight = 'energy')
    path_length = int(sum(ox.utils_graph.get_route_edge_attributes(Seoul_Map, path, 'length')))
    route_graph_map = ox.plot_route_folium(Seoul_Map, path, route_map=m, route_color = 'red', popup_attribute='length')
    
    st.text('최단경로 길이 : %.4fkm' %(path_length/1000))
    st.text('소요 시간 : %.1f분' %((path_length*60)/1000/16.3))
    st.text('이산화탄소 감소량 : %.2fkg' %((path_length/1000) * 0.232))

    folium.Marker(
        [a[0], a[1]]
    ).add_to(m)
    
    folium.Marker(
        [b[0], b[1]]
    ).add_to(m)
    
    folium_static(m)

