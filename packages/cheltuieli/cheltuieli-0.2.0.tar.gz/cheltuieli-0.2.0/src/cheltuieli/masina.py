import numpy as np
from mysqlquerys import connect
from mysqlquerys import mysql_rm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import traceback
import sys


class Masina:
    def __init__(self, ini_file):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ini_file = ini_file
        self.conf = connect.Config(self.ini_file)
        self.alimentari = self.sql_rm.Table(self.conf.credentials, 'alimentari')
        self.users = self.sql_rm.Table(self.conf.credentials, 'users')
        self.types_of_costs = ["electric", "benzina", "intretinere", "asigurare", 'impozit', 'TüV']
        try:
            self.dataBase = self.sql_rm.DataBase(self.conf.credentials)
        except Exception as err:
            print(traceback.format_exc())

    @property
    def sql_rm(self):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        if self.conf.db_type == 'mysql':
            sql_rm = mysql_rm
        return sql_rm

    @property
    def default_interval(self):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        startDate = datetime(datetime.now().year - 1, datetime.now().month, datetime.now().day)
        endDate = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
        return startDate, endDate

    @property
    def total_money(self):
        col = self.alimentari.returnColumn('brutto')
        return round(sum(col), 2)

    @property
    def tot_benzina(self):
        matches = [('type', 'benzina')]
        col = self.alimentari.returnCellsWhere('brutto', matches)
        return round(sum(col), 2)

    @property
    def tot_electric(self):
        matches = [('type', 'electric')]
        col = self.alimentari.returnCellsWhere('brutto', matches)
        return round(sum(col), 2)

    @property
    def monthly(self):
        return round((self.monthly_benzina+self.monthly_electric), 2)

    @property
    def monthly_benzina(self):
        matches = [('type', 'benzina')]
        money = self.alimentari.returnCellsWhere('brutto', matches)
        all_dates = self.alimentari.returnColumn('data')
        start_date = min(all_dates)
        finish_date = max(all_dates)
        total_money = round(sum(money), 2)
        days = (finish_date - start_date).days
        average_day_per_month = 365/12
        monthly = (average_day_per_month * total_money) / days
        return round(monthly, 2)

    @property
    def monthly_electric(self):
        matches = [('type', 'electric')]
        money = self.alimentari.returnCellsWhere('brutto', matches)
        all_dates = self.alimentari.returnColumn('data')
        start_date = min(all_dates)
        finish_date = max(all_dates)
        total_money = round(sum(money), 2)
        days = (finish_date - start_date).days
        average_day_per_month = 365/12
        monthly = (average_day_per_month * total_money) / days
        return round(monthly, 2)

    @property
    def db_start_date(self):
        all_dates = self.alimentari.returnColumn('data')
        start_date = min(all_dates)
        return start_date

    @property
    def db_last_record_date(self):
        all_dates = self.alimentari.returnColumn('data')
        finish_date = max(all_dates)
        return finish_date

    @property
    def table_alimentari(self):
        total_alim = self.tot_benzina + self.tot_electric
        arr = [
            ('', 'Alimentari[€]', 'Benzina[€]', 'Electric[€]'),
            ('Monthly', self.monthly, self.monthly_benzina, self.monthly_electric),
            ('Total', total_alim, self.tot_benzina, self.tot_electric),
        ]
        arr = np.atleast_2d(arr)
        return arr

    @property
    def table_totals(self):
        types = ['benzina', 'electric', 'asigurare', 'impozit', 'TüV', 'intretinere']
        table = []
        for year in reversed(range(self.db_start_date.year, self.db_last_record_date.year+1)):
            # print(year)
            dd = {}
            dd['year'] = year
            startTime = datetime(year, 1, 1)
            endTime = datetime(year+1, 1, 1)
            rows = self.alimentari.returnRowsOfYear('data', startTime, 'data', endTime)
            arr = np.atleast_2d(rows)
            tot = 0
            for t in types:
                indx = np.where(arr[:,self.alimentari.columnsNames.index('type')] == t)
                col = arr[indx, self.alimentari.columnsNames.index('brutto')]
                value = sum(col[0])
                value = round(value, 2)
                dd[t] = value
                tot += value
            dd['total/row'] = round(tot, 2)
            table.append(dd)
        table_head = tuple(dd.keys())
        arr = [table_head]
        for tab in table:
            row = []
            for k, v in tab.items():
                row.append(v)
            arr.append(tuple(row))
        arr = np.atleast_2d(arr)
        row_totals = ['totals']
        total_total = 0
        for col in range(1, arr.shape[1]):
            # print(arr[0, col], round(sum(arr[1:, col].astype(float)), 2))
            val = round(sum(arr[1:, col].astype(float)), 2)
            row_totals.append(val)
            total_total += val
        row_tot = np.array(row_totals)
        new_arr = np.insert(arr, 1, row_tot, axis=0)
        return new_arr

    def get_monthly_interval(self, month:str, year):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        mnth = datetime.strptime(month, "%B").month
        startDate = datetime(year, mnth, 1)

        if mnth != 12:
            lastDayOfMonth = datetime(year, mnth + 1, 1) - timedelta(days=1)
        else:
            lastDayOfMonth = datetime(year + 1, 1, 1) - timedelta(days=1)

        return startDate, lastDayOfMonth

    def get_all_alimentari(self):
        alimentari = self.alimentari.returnAllRecordsFromTable()
        return alimentari

    def get_alimentari_for_interval_type(self, selectedStartDate, selectedEndDate, alim_type):
        matches = [('data', (selectedStartDate, selectedEndDate))]
        if alim_type:
            matches.append(('type', alim_type))
        table = self.alimentari.filterRows(matches)

        if table:
            arr = np.atleast_2d(table)
            arr = np.insert(arr, 0, np.array(self.alimentari.columnsNames), axis=0)
        else:
            arr = np.atleast_2d(np.array(self.alimentari.columnsNames))
        return arr

    def insert_new_alim(self, cols, vals):
        self.alimentari.addNewRow(cols, vals)

