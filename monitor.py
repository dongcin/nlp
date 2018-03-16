# -*-:coding-utf8 -*-
# @Author  : gu_dx
# @Site    :
# @File    : monitor.py
# @Software: PyCharm
"""

"""
import os
import datetime
import pandas as pd
import numpy as np
import time

df_101=[]
df_205=[]


class Monitor():

    def __init__(self):
        self.dat_file = os.path.abspath('.') + "/data/order.dat"
        self.md_101_file = os.path.abspath('.') + "/data/101.csv"
        self.td_205_file = os.path.abspath('.') + "/data/205.csv"

        # self.warning_file = os.path.abspath('.') + "/algo/data/warning.dat"

    def read_memory(self, df_101, df_205):

        # content = "8000000|20180315-14:30:44|    6319590| 9601098| 600050|  0.0|  100|   Open|  Buy"
        print("=============={}".format(len(df_101)))
        price_minus = (df_101['LastPrice(d)'].max()) - (df_101['LastPrice(d)'].min())
        #print(df_101[5].max())
        #price_minus = (df_101[4].max()) - (df_101[4].min())
        fluctuation = float(price_minus) / (df_101['LastPrice(d)'].min())
        print("price changing:",fluctuation)
        if fluctuation > 0.02:
            print("price changed over 2%")
        contents = df_205[['h_nano(l)', 'h_request_id(i)', 'Direction(t)',
                           'InstrumentId(c31)', 'OrderStatus(t)', 'VolumeTotal(i)']]
        data = np.array(contents)
        contents = data.tolist()

        # s = "|".join(content))
        # contents = [x.strip() for x in content.split('|')]
        if df_205['VolumeTotal(i)'].sum() > 100000:
            print("order volume too large")
        Num = df_205['OrderStatus(t)'].count()
        print("order total numer last minute",Num)
        Num_of_tradedOrder = (df_205[df_205['OrderStatus(t)'] == 'AllTraded']['RequestedID(i)'].count())
        print("trade total numer last minute", Num_of_tradedOrder)
        Num_of_CanOrder = (df_205[df_205['OrderStatus(t)'] == 'NoTradeQUeueing']['RequestedID(i)'].count())
        print("cancel total numer last minute", Num_of_CanOrder)
        Num_of_RejOrder = (df_205[df_205['OrderStatus(t)'] == 'Canceled']['RequestedID(i)'].count())
        print("reject total numer last minute", Num_of_RejOrder)
        if Num != 0 and float(Num_of_RejOrder) / Num > 0.2:
            t = Num_of_CanOrder / Num
            print("reject numer too large, try it later")
        elif Num != 0  and float(Num_of_RejOrder) / Num > 0.2:
            print('cancel numer too large, try it later')


        return contents

    def write_db(self, content):
        fp = open(self.dat_file, "a+")
        fp.write(content + "\n")
        fp.flush()
        fp.close()

    # fp_warning = open(self.warning_file, "a+")
    # fp_warning.write(warning + "\n")
    # fp_warning.flush()
    # fp_warning.close()

    def run(self):

        start_time = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(minutes=-1), '%Y%m%d-%H:%M:%S')
        end_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d-%H:%M:%S')
        os.system('yjj dump -n MD_XTP -s ' + start_time + ' -e ' + end_time + ' -m 101 -o ' + self.md_101_file)
        # os.system('yjj dump -n TD_XTP -s ' + start_time + ' -e ' + end_time + ' -m 205 -o ' + self.td_205_file)
        # os.system('yjj dump -n TD_XTP -s ' + start_time + ' -e ' + end_time + ' -m 206 -o td_206.csv')
        time.sleep(5)

        df_101 = pd.read_csv(self.md_101_file)
        df_205 = pd.read_csv(self.td_205_file)

        orders = self.read_memory(df_101, df_205)

        content = []
        for content in orders:
            content = map(str, content)
        # print (("|".join(order)))

        self.write_db("|".join(content))

    def judgeTradetime(self):
        nowtime = datetime.datetime.now()
        # current time
        d1 = datetime.date.today()
        tm = datetime.time(9, 30, 0)
        tn = datetime.time(11, 30, 0)
        ta = datetime.time(13, 0, 0)
        tc = datetime.time(15, 0, 0)

        opentime = datetime.datetime.combine(d1, tm)
        noonclotime = datetime.datetime.combine(d1, tn)
        afteroptime = datetime.datetime.combine(d1, ta)
        closetime = datetime.datetime.combine(d1, tc)

        if ((opentime <= nowtime <= noonclotime) or (afteroptime <= nowtime <= closetime)):

            return 1
        else:
            print("not trading time")
            return 0


if __name__ == '__main__':
    monitor = Monitor()
    while monitor.judgeTradetime():

        # monitor = Monitor()
        monitor.run()
        time.sleep(60)

