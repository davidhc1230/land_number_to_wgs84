#將完整的地號按縣市、鄉鎮市區、段名、地號號碼進行拆分，以便於進行地號轉座標的工作

import pandas as pd
import re

land_num_raw = pd.read_csv('land_num_raw.csv', header=None)
land_num_raw = pd.DataFrame.to_string(land_num_raw)
land_num_split = re.findall('(.{,3}[縣市])(.{,3}[鄉鎮市區])(.*段)(\d+-*\d*)', land_num_raw)  # 將地址分段
land_num_split = pd.DataFrame(land_num_split, columns=['縣市', '鄉鎮市區', '段名', '地號'])
land_num_split.to_csv('land_num_split.csv', sep = ',', index=False, encoding='utf_8_sig') #輸出csv