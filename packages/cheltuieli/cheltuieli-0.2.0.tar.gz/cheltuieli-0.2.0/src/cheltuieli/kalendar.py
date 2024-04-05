from mysqlquerys import connect
from mysqlquerys import mysql_rm
from datetime import datetime, timedelta
import traceback
import sys


class Kalendar:
    def __init__(self, ini_file):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ini_file = ini_file
        self.conf = connect.Config(self.ini_file)
        self.program_table = self.sql_rm.Table(self.conf.credentials, 'program')
        # self.users = self.sql_rm.Table(self.conf.credentials, 'users')

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
    def persons(self):
        return ['Siri', 'Radu', 'Enya']

    def get_rows_that_start_after_selected_start_date(self, selectedStartDate):
        rows = self.program_table.returnRowsYoungerThan('start', selectedStartDate)
        return rows

    def get_appointments_in_interval(self, person, selectedStartDate, selectedEndDate):
        # rows = self.get_rows_that_start_after_selected_start_date(selectedStartDate)
        # for i in rows:print(i)
        all_appointments = [tuple(self.program_table.columnsNames[1:])]
        rows = self.program_table.returnRowsInInterval('start', selectedStartDate, 'finish', selectedEndDate)
        for row in rows:
            # print(i)
            all_appointments.append(tuple(row[1:]))
        rows = self.program_table.returnRowsOutsideInterval('start', selectedStartDate, 'finish', selectedEndDate)
        for row in rows:
            all_appointments.append(tuple(row[1:]))
            # print(i)
        return all_appointments

    def insert_new_termin(self, cols, vals):
        self.program_table.addNewRow(cols, vals)



    # @property
    # def total_money(self):
    #     col = self.alimentari.returnColumn('brutto')
    #     return round(sum(col), 2)
    #
    # @property
    # def tot_benzina(self):
    #     matches = [('type', 'benzina')]
    #     col = self.alimentari.returnCellsWhere('brutto', matches)
    #     return round(sum(col), 2)
    #
    # @property
    # def tot_electric(self):
    #     matches = [('type', 'benzina')]
    #     col = self.alimentari.returnCellsWhereDiffrent('brutto', matches)
    #     return round(sum(col), 2)
    #
    # @property
    # def db_pass(self):
    #     matches = [('name', 'radu')]
    #     col = self.users.returnCellsWhere('password', matches)[1]
    #     return col
    #
    # def get_monthly_interval(self, month:str):
    #     # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
    #     mnth = datetime.strptime(month, "%B").month
    #     startDate = datetime(datetime.now().year, mnth, 1)
    #
    #     if mnth != 12:
    #         lastDayOfMonth = datetime(datetime.now().year, mnth + 1, 1) - timedelta(days=1)
    #     else:
    #         lastDayOfMonth = datetime(datetime.now().year + 1, 1, 1) - timedelta(days=1)
    #
    #     return startDate, lastDayOfMonth
    #
    # def get_all_alimentari(self):
    #     alimentari = self.alimentari.returnAllRecordsFromTable()
    #     return alimentari
    #
    # def get_alimentari_for_interval_type(self, selectedStartDate, selectedEndDate, alim_type):
    #     matches = [('data', (selectedStartDate, selectedEndDate))]
    #     if alim_type:
    #         matches.append(('type', alim_type))
    #     table = self.alimentari.filterRows(matches)
    #     return table
    #
    # def insert_new_alim(self, cols, vals):
    #     self.alimentari.addNewRow(cols, vals)