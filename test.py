import pandas as pd
import os 
import openpyxl

dir_path = 'C:\\Users\\MREKHA3\\Downloads\\'

for filename in os. listdir(dir_path):     
       if filename. endswith(' xIsx'):         
                file_path = os.path. join (dir_path, filename)         
                workbook = openpyx1. load_-workbook(file_path)        
                # Do something with the workbook


#path = 'C:/Users/MREKHA3/Downloads/Source Name and IT Connect Queue.xlsx/'
#path.replace("\\", "\\\\")
#df = pd.DataFrame(data)

#dataframe1 = pd.read_excel('path')
#print(dataframe1)