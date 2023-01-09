#這支程式是專門用來處理地號查詢的網頁(https://easymap.land.moi.gov.tw/R02/Index)
#運作邏輯為：選縣市->選鄉鎮市區->選段名->輸入地號->在圖釘上點右鍵查詢經緯度
#目的為批次將地號轉為經緯度座標(WGS84)
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from time import sleep
import requests
import pandas as pd
import geopandas as gpd

land_num_split = pd.read_csv('land_num_split.csv', encoding='utf_8')
list_city = list(land_num_split.iloc[:, 0])
list_town = list(land_num_split.iloc[:, 1])
list_sect = list(land_num_split.iloc[:, 2])
list_landno = list(land_num_split.iloc[:, 3])

address_num = 0 #設定初始完成筆數
url = 'https://easymap.land.moi.gov.tw/R02/Index'
resp = requests.get(url)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')
#######################Selenium設定#########################
options = Options()
#options.add_argument('--headless') #啟動無頭模式
options.add_experimental_option('excludeSwitches', ['enable-logging']) #不輸出logging
options.add_argument('--log-level=3') #不輸出log
options.add_argument('--disable-gpu') #windows必須加入此行
webdriver_path = 'D:\暫存\python實驗室\driver\chromedriver.exe'

driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
driver.get(url)
sleep(3) #休息3秒，讓網站載完

list_lat =[]
list_lon =[]
for i, j, k, l in zip(list_city, list_town, list_sect, list_landno):
    sleep(10)
    city_id = Select(driver.find_element_by_id('select_city_id')) #選縣市
    city_id.select_by_visible_text(i.strip())
    sleep(3)
    town_id = Select(driver.find_element_by_id('select_town_id')) #選鄉鎮市區
    town_id.select_by_visible_text(j.strip())
    sleep(3)
    sect_id = Select(driver.find_element_by_id('select_sect_id')) #選地段
    sect_id_options = sect_id.options
    for a in sect_id_options:
        a = a.text
        if a[6:] == k.strip(): #地段選單內的格式為：(xxxx)XX段，因此判斷括號之後的文字若相同，則選擇
            sect_id.select_by_visible_text(a)
    sleep(3)
    landno = driver.find_element_by_id('landno').send_keys(l.strip()) #輸入地號
    driver.find_element_by_id('land_button').click() #點擊查詢
    try:
        sleep(10) #休息一下，不然點右鍵會跑不出選單
        ActionChains(driver).context_click(driver.find_element_by_id('OpenLayers.Layer.Vector_42_svgRoot')).perform() #點擊右鍵
        driver.find_element_by_class_name('context-menu-item.icon.icon-getCoordWGS84byMap').click()
        lat = driver.find_element_by_id('coordDisplayLonLat').text[:7] #取出緯度
        lon = driver.find_element_by_id('coordDisplayLonLat').text[9:] #取出經度
    except: #若查詢不到，經緯度直接給予0
        lat = 0
        lon = 0
    driver.find_element_by_id('landno').clear() #清除原本查詢內容

    list_lat.append(lat)
    list_lon.append(lon)
    latlon_combine = pd.DataFrame(zip(list_lat, list_lon))
    latlon_combine.columns = ['lat', 'lon']
    latlon_combine.to_csv('land_num_convert_to_wgs84.csv', sep = ',', index=False) #輸出csv