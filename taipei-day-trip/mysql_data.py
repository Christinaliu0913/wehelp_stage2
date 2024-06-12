import json
import mysql.connector
import datetime 
import re

#connect to mySQL
con=mysql.connector.connect(
    host='localhost',
    user="root",
    password="ASdf1234.",
    database='taipei'
)
#過濾png/jpg的檔案
def filter_images(file_str):
    images = file_str.split('http')
    valid_images = [f"http{img.strip()}" for img in images if re.search(r'\.(jpg|jpeg|png)$', img.strip(),re.IGNORECASE)]
    return ','.join(valid_images) if valid_images else None


def read_json(file_path):
    with open (file_path, "r", encoding='utf-8') as taipei_file:
        data = json.load(taipei_file)
        for i in data['result']['results']:
            name = i.get('name',None)
            rate = int(i.get('rate',None))
            lng = float(i['longitude'])
            lat = float(i['latitude'])
            description = i['description']
            transport = i.get('direction',None)
            date = datetime.datetime.strptime(i.get('date',None),'%Y/%m/%d').date()
            images = filter_images(i.get('file', None))
            serial_no = i.get('SERIAL_NO',None)
            address = i.get('address',None)
            ref_wp = i.get('REF_WP', None)
            avBegin = datetime.datetime.strptime(i.get('avBegin',None),'%Y/%m/%d').date()
            avEnd = datetime.datetime.strptime(i.get('avEnd',None),'%Y/%m/%d').date()
            langinfo = i.get('langinfo',None)
            mrt = i.get('MRT',None)
            rowNumber= int(i.get('RowNumber',None))
            category = i.get('CAT',None)
            memo_time = i.get('MEMO_TIME',None)
            poi = i.get('POI',None)
            idpt= i.get('idpt',None)
            
            if images: 
                cursor=con.cursor()
                cursor.execute('''
                    INSERT INTO attraction (
                               name, rate, lng, transport, lat, description, date, images,
                               serial_no, address, ref_wp, avBegin, avEnd, langinfo, mrt, rowNumber, category, memo_time, poi, idpt
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
                ''', (name, rate, lng, transport, lat, description, date, images,
                      serial_no, address, ref_wp, avBegin, avEnd, langinfo, mrt, rowNumber, category, memo_time, poi, idpt))
                con.commit()
                cursor.close()





if __name__ == '__main__':
    file_path = 'data/taipei-attractions.json'
    read_json(file_path)
    con.close()