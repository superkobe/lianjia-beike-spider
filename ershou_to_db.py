#!/usr/bin/env python
# coding=utf-8
# author: zengyuetian
# 此代码仅供学习与交流，请勿用于商业用途。
# read data from csv, write to database
# database includes: mysql/mongodb/excel/json/csv

import os
import pymysql
from lib.utility.path import DATA_PATH
from lib.zone.city import *
from lib.utility.date import *
from lib.utility.version import PYTHON_3
from lib.spider.base_spider import SPIDER_NAME

pymysql.install_as_MySQLdb()


def create_prompt_text():
    city_info = list()
    num = 0
    for en_name, ch_name in cities.items():
        num += 1
        city_info.append(en_name)
        city_info.append(": ")
        city_info.append(ch_name)
        if num % 4 == 0:
            city_info.append("\n")
        else:
            city_info.append(", ")
    return 'Which city data do you want to save ?\n' + ''.join(city_info)

def create_detail(detail):
    floor = ''
    year = ''
    house_type = ''
    size = ''
    orientation = ''
    dt_list = detail.split('  ')
    for dt in dt_list:
        if dt.strip() == '':
            continue
        elif dt.count('|') > 0:
            for d in dt.split('|'):
                if d.strip() == '':
                    continue
                elif '室' in d.strip() or '厅' in d.strip():
                    house_type = d.strip()
                elif '平' in d.strip() or '米' in d.strip():
                    size = d.strip()
                elif '南' in d.strip() or '北' in d.strip() or '东' in d.strip() or '西' in d.strip():
                    orientation = d.strip()
                elif '年' in d.strip():
                    year = d.strip()
                elif '层' in d.strip() or '楼' in d.strip():
                    floor = d.strip()
        elif '室' in dt.strip() or '厅' in dt.strip():
            house_type = dt.strip()
        elif '平' in dt.strip() or '米' in dt.strip():
            size = dt.strip()
        elif '南' in dt.strip() or '北' in dt.strip() or '东' in dt.strip() or '西' in dt.strip():
            orientation = dt.strip()
        elif '年' in dt.strip():
            year = dt.strip()
        elif '层' in dt.strip() or '楼' in d.strip():
            floor = dt.strip()
    return floor, year, house_type, size, orientation


if __name__ == '__main__':
    # 设置目标数据库
    ##################################
    # mysql/mongodb/excel/json/csv
    # database = "mysql"
    # database = "mongodb"
    # database = "excel"
    # database = "json"
    database = "mysql"
    ##################################
    db = None
    collection = None
    workbook = None
    csv_file = None
    datas = list()

    if database == "mysql":
        import records
        db = records.Database('mysql://root:Root123.@localhost/house?charset=utf8', encoding='utf-8')
    elif database == "mongodb":
        from pymongo import MongoClient
        conn = MongoClient('localhost', 27017)
        db = conn.lianjia  # 连接lianjia数据库，没有则自动创建
        collection = db.xiaoqu  # 使用xiaoqu集合，没有则自动创建
    elif database == "excel":
        import xlsxwriter
        workbook = xlsxwriter.Workbook('xiaoqu.xlsx')
        worksheet = workbook.add_worksheet()
    elif database == "json":
        import json
    elif database == "csv":
        csv_file = open("ershou.csv", "w")
        line = "{0};{1};{2};{3};{4};{5};{6}\n".format('city_ch', 'date', 'district', 'area', 'xiaoqu', 'price', 'sale')
        csv_file.write(line)

    city = get_city()
    # 准备日期信息，爬到的数据存放到日期相关文件夹下
    date = get_date_string()
    # 获得 csv 文件路径
    # date = "20180331"   # 指定采集数据的日期
    # city = "sh"         # 指定采集数据的城市
    city_ch = get_chinese_city(city)
    csv_dir = "{0}/{1}/ershou/{2}/{3}".format(DATA_PATH, SPIDER_NAME, city, date)

    files = list()
    if not os.path.exists(csv_dir):
        print("{0} does not exist.".format(csv_dir))
        print("Please run 'python ershou.py' firstly.")
        print("Bye.")
        exit(0)
    else:
        print('OK, start to process ' + get_chinese_city(city))
    for csv in os.listdir(csv_dir):
        data_csv = csv_dir + "/" + csv
        # print(data_csv)
        files.append(data_csv)

    # 清理数据
    count = 0
    row = 0
    col = 0
    for csv in files:
        with open(csv, 'r') as f:
            for line in f:
                count += 1
                text = line.strip()
                try:
                    # 如果小区名里面没有逗号，那么总共是10项
                    # if text.count(',') == 9:
                    #     date, district, area, title, price, detail, pic1, pic2, pic3, pic4 = text.split(',')
                    #     floor, size, orientation = detail.split('|')
                    #     floor = floor.strip()
                    #     size = size.strip()
                    #     orientation = orientation.strip()
                    #     title = ''
                    #     house_type = ''
                    # elif text.count(',') == 10:
                    #     date, district, area, title1, title2, price, detail, pic1, pic2, pic3, pic4 = text.split(',')
                    #     floor, year, house_type, size, orientation = detail.split('|')
                    #     floor = floor.strip()
                    #     size = size.strip()
                    #     year = year.strip()
                    #     house_type = house_type.strip()
                    #     orientation = orientation.strip()
                    #     title = title1 + title2
                    # elif text.count(',') == 11:
                    #     date, district, area, title1, title2, title3, price, detail, pic1, pic2, pic3, pic4 = text.split(',')
                    #     floor, year, house_type, size, orientation = detail.split('|')
                    #     floor = floor.strip()
                    #     size = size.strip()
                    #     year = year.strip()
                    #     house_type = house_type.strip()
                    #     orientation = orientation.strip()
                    #     title = title1 + title2 + title3
                    if text.count(',') == 7:
                        date, district, area, title, price, detail, pic, url = text.split(',')
                        floor = ''
                        year = ''
                        house_type = ''
                        size = ''
                        orientation = ''
                        if text.split(',')[5].count('  ') > 0:
                            floor, year, house_type, size, orientation = create_detail(text.split(',')[5])
                    elif text.count(',') < 5:
                        continue
                    else:
                        fields = text.split(',')
                        date = fields[0]
                        district = fields[1]
                        area = fields[2]
                        xiaoqu = ','.join(fields[3:-2])
                        price = fields[-2]
                        sale = fields[-1]
                except Exception as e:
                    print(text)
                    print(e)
                    continue
                # sale = sale.replace(r'套在售二手房', '')
                price = price.replace(r'暂无', '0')
                price = price.replace(r'元/m2', '')
                price = price.replace(r'万', '0000')
                if price.count('.') == 1:
                    price = int(float(price))
                # sale = int(sale)
                else:
                    price = int(price)
                print("{0} {1} {2} {3} {4} {5} {6} {7}".format(date, district, area, title, house_type, floor, size, orientation, price, url))
                # 写入mysql数据库
                if database == "mysql":
                    db.query('INSERT INTO ershou (city, date, district, area, title, house_type, floor, size, orientation, price, url) '
                             'VALUES(:city, :date, :district, :area, :title, :house_type, :floor, :size, :orientation, :price, :url)',
                             city=city_ch, date=date, district=district, area=area, title=title, house_type=house_type, floor=floor, size=size, orientation=orientation, price=price, url=url)
                # 写入mongodb数据库
                elif database == "mongodb":
                    data = dict(city=city_ch, date=date, district=district, area=area, xiaoqu=xiaoqu, price=price,
                                sale=sale)
                    collection.insert(data)
                elif database == "excel":
                    if not PYTHON_3:
                        worksheet.write_string(row, col, unicode(city_ch, 'utf-8'))
                        worksheet.write_string(row, col + 1, date)
                        worksheet.write_string(row, col + 2, unicode(district, 'utf-8'))
                        worksheet.write_string(row, col + 3, unicode(area, 'utf-8'))
                        worksheet.write_string(row, col + 4, unicode(xiaoqu, 'utf-8'))
                        worksheet.write_number(row, col + 5, price)
                        worksheet.write_number(row, col + 6, sale)
                    else:
                        worksheet.write_string(row, col, city_ch)
                        worksheet.write_string(row, col + 1, date)
                        worksheet.write_string(row, col + 2, district)
                        worksheet.write_string(row, col + 3, area)
                        worksheet.write_string(row, col + 4, xiaoqu)
                        worksheet.write_number(row, col + 5, price)
                        worksheet.write_number(row, col + 6, sale)
                    row += 1
                elif database == "json":
                    data = dict(city=city_ch, date=date, district=district, area=area, xiaoqu=xiaoqu, price=price,
                                sale=sale)
                    datas.append(data)
                elif database == "csv":
                    line = "{0};{1};{2};{3};{4};{5};{6}\n".format(city_ch, date, district, area, xiaoqu, price, sale)
                    csv_file.write(line)

    # 写入，并且关闭句柄
    if database == "excel":
        workbook.close()
    elif database == "json":
        json.dump(datas, open('xiaoqu.json', 'w'), ensure_ascii=False, indent=2)
    elif database == "csv":
        csv_file.close()

    print("Total write {0} items to database.".format(count))
