import urllib
import os
import json
import csv
import datetime

import requests

def get_file_name(url):
    path=urllib.parse.urlparse(url).path
    return os.path.split(path)[-1]

def download_file(url):
    file_name=get_file_name(url)

    response=requests.get(url)
    if response.status_code!=requests.codes.ok:
        raise Exception("status_code!=200")
    response.encoding=response.apparent_encoding

    with open(file_name,"wb") as f:
        f.write(response.content)
    return file_name

def daterange(start_date,end_date):
    """
    start_date(含む)からend_date(含む)まで
    """
    for n in range(int((end_date-start_date).days)+1):
        yield start_date+datetime.timedelta(n)

def main():
    #福岡県のopendata
    url="https://ckan.open-governmentdata.org/dataset/8a9688c2-7b9f-4347-ad6e-de3b339ef740/resource/765d78d5-6754-43eb-850e-a658b086469b/download/400009_pref_fukuoka_covid19_patients.csv"
    file_name=download_file(url)
    #日付とその日の陽性者数をセットしていく
    data={}
    with open(file_name,encoding="utf-8") as f:
        reader=csv.reader(f)
        _=next(reader) #headerは飛ばす
        
        for  row in reader:
            #空白があるので飛ばす no.1311など
            if row[4]=="":
                continue
            date=datetime.datetime.strptime(row[4],"%Y/%m/%d").date()
            date=date.strftime("%Y-%m-%d")
            if date in data:
                data[date]+=1
            else:
                data[date]=1

    #json形式にするためにフォーマット整える
    #初めて陽性者が確認された日から後の日付で、陽性者が確認されていない日は 0を記入する。
    date_list=sorted(data.keys(),key=lambda x: datetime.date.fromisoformat(x))
    first_date=datetime.date.fromisoformat(date_list[0])
    last_date=datetime.date.fromisoformat(date_list[-1])
    print("日付(最初):",first_date)
    print("日付(最後):",last_date)

    result=[]
    for d in daterange(first_date,last_date):
        date=d.isoformat()
        count=data[date] if  (date in data) else 0
        item={
            "date":date,
            "count":count
        }
        result.append(item)

    #jsonに書きだし
    data={
        "data":result
    }
    print(data)

    with open("fukuoka_data.json","w") as f:
        json.dump(data,f,indent=4)

if __name__ == "__main__":
    main()