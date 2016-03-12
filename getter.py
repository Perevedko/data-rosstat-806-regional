from datetime import date
import pandas as pd
import os

from xls_read import read_sheet, read_by_definition, yearmon
from regions import Regions

filter_region_name = Regions.filter_region_name
reference_region_names = Regions.names()
rf_name = Regions.rf_name()
district_names = Regions.district_names()
summable_regions = Regions.summable_regions()

def get_dataframe(datapoints_stream):
    """Return dataframe corresponding to datapoints stream."""        
    list_of_dicts = [{'val':x[0], 'region':x[1], 'dates':x[2]} for x in datapoints_stream]
    df = pd.DataFrame(list_of_dicts)
    # note: may also need to change index class to DateIndex 
    # pd.DatetimeIndex(df.dates, freq = "M")
    return df.pivot(columns='region', values='val', index='dates')[reference_region_names] 

def get_dataframe_by_definition(def_dict):
    """Return dataframe corresponding to definition dict."""   
    file_path = os.path.join(def_dict['folder'], def_dict['filename'])
    if 'anchor' in def_dict.keys():
        gen = read_sheet(file_path, def_dict['sheet'], def_dict['anchor']) 
    else:
        gen = read_sheet(file_path, def_dict['sheet'])
    df = get_dataframe(gen)[Regions.names()]
    df.insert(0, 'varname', def_dict['varname'])
    return df 
    
def get_regions_dataframe(def_dict):
    """Return pandas DataFrame containing variable from *def_dict* by REGION"""
    return get_dataframe_by_definition(def_dict)[summable_regions]
    
def get_okrug_dataframe(def_dict):
    """Return pandas DataFrame containing variable from *def_dict* by FEDERAL DISTRICT (okrug)"""
    return get_dataframe_by_definition(def_dict)[district_names]
    
def get_rf_dataframe(def_dict):
    """Return pandas DataFrame containing variable from *def_dict* by RUSSIA TOTAL"""
    return get_dataframe_by_definition(def_dict)[rf_name]

def to_excel(def_dict):
    df = get_dataframe_by_definition(def_dict)
    # check must not overwrite
    filename = def_dict['varname'] + ".xls"
    df.transpose().to_excel(filename)
    
if __name__ == "__main__":

    def_dict_1 = {'varname':'PPI_PROM_ytd', 
     'folder':'xl_sample', 
   'filename':'industrial_prices.xls',
      'sheet':'пром.товаров',
     'anchor':'B5', 'anchor_value': 96.6}

    df = get_dataframe_by_definition(def_dict_1)
    to_excel(def_dict_1)
    
    # make definition for shipments.xls + tests below      
    def_dict_2 = {'varname':'SHIPMENTS', 
     'folder':'xl_sample', 
   'filename':'shipment.xls',
      'sheet':'Млн.рублей',
     'anchor':'B6', 'anchor_value': 5331853.711}     

    reg = get_regions_dataframe(def_dict_2)
    okr = get_okrug_dataframe(def_dict_2)
    rf  = get_rf_dataframe(def_dict_2)

    # + test_anchor()    
    
# tests to pass:
# 3.1 for summable values summ by regions equals Russian Federation total 
    p = abs(reg.sum(axis = 1) - rf)
    print(p[p > 0.1]) 
    
# 3.2 for summable values summ by districts equals Russian Federation total 
    z = abs(okr.sum(axis = 1) - rf)
    print(z[z > 0.1])
    
# 3.3 with summation matrix for summable values summ by region in district equals district total
    # todo: need summation matrix by region
