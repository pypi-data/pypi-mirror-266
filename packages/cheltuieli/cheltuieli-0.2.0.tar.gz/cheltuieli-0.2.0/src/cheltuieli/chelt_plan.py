import csv
import os.path
import traceback
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import sys
from mysqlquerys import connect
from mysqlquerys import mysql_rm

np.set_printoptions(linewidth=250)
__version__ = 'V5'


def calculate_last_day_of_month(mnth, year):
    if mnth < 12:
        # lastDayOfMonth = datetime(datetime.now().year, mnth + 1, 1) - timedelta(days=1)
        lastDayOfMonth = datetime(year, mnth + 1, 1) - timedelta(days=1)
        lastDayOfMonth = lastDayOfMonth.day
    elif mnth == 12:
        lastDayOfMonth = 31
    return lastDayOfMonth


def default_interval():
    # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
    startDate = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
    if datetime.now().month != 12:
        mnth = datetime.now().month + 1
        lastDayOfMonth = datetime(datetime.now().year, mnth, 1) - timedelta(days=1)
    else:
        lastDayOfMonth = datetime(datetime.now().year + 1, 1, 1) - timedelta(days=1)

    return startDate, lastDayOfMonth


def get_monthly_interval(month:str, year):
    # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
    mnth = datetime.strptime(month, "%B").month
    startDate = datetime(year, mnth, 1)

    if mnth != 12:
        lastDayOfMonth = datetime(year, mnth + 1, 1) - timedelta(days=1)
    else:
        lastDayOfMonth = datetime(year + 1, 1, 1) - timedelta(days=1)

    return startDate.date(), lastDayOfMonth.date()


class Income:
    def __init__(self, ini_file):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ini_file = ini_file
        pth2src = os.path.dirname(__file__)
        # self.taxes_file = r"static\taxes.csv"
        self.taxes_file = os.path.join(pth2src, 'static', 'taxes.csv')
        self.tax_array, self.tax_header = self.conv_csv_to_np(skipHeader=1)
        self.conf = connect.Config(self.ini_file)
        self.income_table = mysql_rm.Table(self.conf.credentials, 'income')
        self.selectedStartDate = None
        self.selectedEndDate = None
        self.conto = None
        self.tableHead = None
        self.income = None

    def apply_taxes_to_salary(self):
        for inc in self.incomes_for_time_interval:
            if inc.is_salary:
                print('####', inc.id, inc.name, inc.payments_for_interval)
                inc.basic_brutto_35h_salary = inc.value
                other_incomes_with_salary = self.find_other_incomes_with_salary_tax()
                brutto = inc.basic_brutto_35h_salary
                # print('******inc.basic_brutto_35h_salary', inc.basic_brutto_35h_salary)
                for i in other_incomes_with_salary:
                    if i.value:
                        brutto += i.value
                    else:
                        brutto += inc.basic_brutto_35h_salary * float(i.proc)
                inc.monthly_35h_brutto_salary = brutto
                # print('******inc.monthly_35h_brutto_salary', inc.monthly_35h_brutto_salary)
                taxes = ['lohnsteuer', 'rentenvers', 'arbeitslosvers', 'krankenvers', 'privatvers']
                for tax in taxes:
                    res = round(self.calculate_tax(inc, tax), 2)
                    exec('inc.{} = {}'.format(tax, res))
                inc.brutto = round(inc.brutto_monthly_salary, 2)

        for inc in self.incomes_for_time_interval:
            if inc.tax == 'bonus':
                for payday in inc.payments_for_interval:
                    income_with_same_payday = self.find_salary_with_same_payday(payday)
                    if not income_with_same_payday:
                        print(inc.id, inc.name, payday)
                    inc.steuerklasse = income_with_same_payday.steuerklasse
                    if not inc.value:
                        inc.value = float(inc.proc) * income_with_same_payday.brutto_monthly_salary
                    inc.brutto = round(float(inc.value), 2)

                    taxes = ['lohnsteuer', 'rentenvers', 'arbeitslosvers']
                    for tax in taxes:
                        res = self.calculate_tax(inc, tax)
                        exec('inc.{} = {}'.format(tax, res))
            elif not inc.tax:
                inc.brutto = round(float(inc.value), 2)

    def find_salary_with_same_payday(self, payday):
        for inc in self.incomes_for_time_interval:
            if inc.is_salary:
                if payday in inc.payments_for_interval:
                    return inc

    def calculate_tax(self, income, steuer):
        indx_row = np.where((self.tax_array[:, self.tax_header.index('tax')] == income.tax) &
                            (self.tax_array[:, self.tax_header.index('steuerklasse')].astype(int) == income.steuerklasse))

        lohnteuer_proc = self.tax_array[indx_row, self.tax_header.index(steuer)]
        lohnteuer_proc = float(lohnteuer_proc[0,0])/100

        if income.is_salary:
            lohnteuer = float(income.brutto_monthly_salary) * lohnteuer_proc
        else:
            lohnteuer = float(income.value) * lohnteuer_proc
        return round(lohnteuer, 2)

    def convert_to_tabel(self):
        table = [('table', 'name', 'brutto', 'taxes', 'netto', 'myconto', 'payDay', 'freq')]
        for income in self.incomes_for_time_interval:
            for datum in income.payments_for_interval:
                if not income.brutto and not income.gesetzliche_abzuge and not income.netto:
                    continue
                tup = (income.table, income.name, income.brutto, income.gesetzliche_abzuge, income.netto, income.myconto, datum.date(), income.freq)
                table.append(tup)
        table = np.atleast_2d(table)
        return table

    def convert_to_salary_tabel(self):
        table = [('table', 'name', 'brutto', 'lohnsteuer', 'rentenvers', 'arbeitslosvers', 'gesetzliche_abzuge',
                  'netto', 'krankenvers', 'privatvers', 'abzuge', 'uberweisung', 'myconto', 'payDay', 'freq')]
        brutto = 0
        taxes = 0
        netto = 0
        abzuge = 0
        uberweisung = 0
        for income in self.incomes_for_time_interval:
            if not income.in_salary:
                print('++++++not in salary', income.name)
                continue
            for datum in income.payments_for_interval:
                if not income.brutto and not income.gesetzliche_abzuge and not income.netto:
                    continue
                tup = (income.table,
                       income.name,
                       income.brutto,
                       income.lohnsteuer,
                       income.rentenvers,
                       income.arbeitslosvers,
                       income.gesetzliche_abzuge,
                       income.netto,
                       income.krankenvers,
                       income.privatvers,
                       income.abzuge,
                       income.uberweisung,
                       income.myconto,
                       datum.date(),
                       income.freq)
                table.append(tup)
                try:
                    brutto += income.brutto
                    if income.gesetzliche_abzuge:
                        taxes += income.gesetzliche_abzuge
                    if income.abzuge:
                        abzuge += income.abzuge
                    netto += float(income.netto)
                    uberweisung += float(income.uberweisung)
                except:
                    print(income.name, income.brutto, income.netto)
        table = np.atleast_2d(table)
        return table, brutto, round(taxes, 2), netto, abzuge, uberweisung

    def convert_to_total_income_tabel(self):
        table = [('table', 'name', 'brutto', 'lohnsteuer', 'rentenvers', 'arbeitslosvers', 'gesetzliche_abzuge',
                  'netto', 'krankenvers', 'privatvers', 'abzuge', 'uberweisung', 'myconto', 'payDay', 'freq',
                  'in_salary')]
        salary_brutto = 0
        salary_gesetzliche_abzuge = 0
        salary_netto = 0
        salary_abzuge = 0
        salary_uberweisung = 0
        brutto = 0
        taxes = 0
        netto = 0
        abzuge = 0
        uberweisung = 0
        for income in self.incomes_for_time_interval:
            for datum in income.payments_for_interval:
                if not income.brutto and not income.gesetzliche_abzuge and not income.netto:
                    continue
                tup = (income.table,
                       income.name,
                       income.brutto,
                       income.lohnsteuer,
                       income.rentenvers,
                       income.arbeitslosvers,
                       income.gesetzliche_abzuge,
                       income.netto,
                       income.krankenvers,
                       income.privatvers,
                       income.abzuge,
                       income.uberweisung,
                       income.myconto,
                       datum.date(),
                       income.freq,
                       income.in_salary,
                       )
                table.append(tup)
                try:
                    if income.in_salary:
                        salary_brutto += income.brutto
                        if income.gesetzliche_abzuge:
                            salary_gesetzliche_abzuge += income.gesetzliche_abzuge
                        salary_netto += float(income.netto)
                        if income.abzuge:
                            salary_abzuge += income.abzuge
                        salary_uberweisung += float(income.uberweisung)
                    brutto += income.brutto
                    if income.gesetzliche_abzuge:
                        taxes += income.gesetzliche_abzuge
                    if income.abzuge:
                        abzuge += income.abzuge
                    netto += float(income.netto)
                    uberweisung += float(income.uberweisung)
                except:
                    print(income.name, income.brutto, income.netto)
        table = np.atleast_2d(table)
        result = (table, brutto, round(taxes, 2), netto, abzuge, uberweisung, salary_brutto, salary_gesetzliche_abzuge, salary_netto, salary_abzuge, salary_uberweisung)
        return result

    def conv_csv_to_np(self, delimiter=';', skipHeader=None):
        array = []
        header = []
        with open(self.taxes_file, 'r') as file:
            reader = csv.reader(file, delimiter=delimiter)
            for i, row in enumerate(reader):
                if skipHeader:
                    if i < skipHeader:
                        header.append(row)
                        continue
                array.append(row)
            array = np.atleast_2d(array)
        if skipHeader == 1:
            header = header[0]

        return array, header

    def get_all_income_rows(self):
        vals = self.income_table.returnAllRecordsFromTable()
        all_incomes = []
        for row in vals:
            row = list(row)
            income = Cheltuiala(row, self.income_table.columnsNames)
            income.set_table(self.income_table.tableName)
            all_incomes.append(income)
        return all_incomes

    def filter_income_for_interval(self, all_income_rows):
        incomes_interval = []
        for inc in all_income_rows:
            payments_in_interval = None
            if self.myconto == 'all':
                payments_in_interval = inc.calculate_payments_in_interval(self.selectedStartDate, self.selectedEndDate)
            elif self.myconto == inc.myconto:
                payments_in_interval = inc.calculate_payments_in_interval(self.selectedStartDate, self.selectedEndDate)
            if payments_in_interval:
                inc.payments_for_interval = payments_in_interval
                incomes_interval.append(inc)
        return incomes_interval

    def find_other_incomes_with_salary_tax(self):
        other_incomes_with_salary = []
        for i in self.incomes_for_time_interval:
            if i.tax == 'salary' and i.name != 'Salariu':
                other_incomes_with_salary.append(i)
        return other_incomes_with_salary

    def prepareTablePlan(self, conto, selectedStartDate, selectedEndDate):
        self.selectedStartDate = selectedStartDate
        self.selectedEndDate = selectedEndDate
        self.myconto = conto

        all_income_rows = self.get_all_income_rows()
        self.incomes_for_time_interval = self.filter_income_for_interval(all_income_rows)
        self.apply_taxes_to_salary()
        # table = self.convert_to_tabel()
        result = self.convert_to_total_income_tabel()
        table, self.brutto, self.taxes, self.netto, self.abzuge, self.uberweisung, self.salary_brutto, \
        self.salary_gesetzliche_abzuge, self.salary_netto, self.salary_abzuge, self.salary_uberweisung = result

        self.tableHead, self.income = list(table[0]), table[1:]

    def get_salary_income(self, month):
        self.selectedStartDate, self.selectedEndDate = get_monthly_interval(month)
        self.myconto = 'EC'

        all_income_rows = self.get_all_income_rows()
        self.incomes_for_time_interval = self.filter_income_for_interval(all_income_rows)
        self.apply_taxes_to_salary()
        table, brutto, taxes, netto, abzuge, uberweisung = self.convert_to_salary_tabel()
        return table, brutto, taxes, netto, abzuge, uberweisung

    def get_total_monthly_income(self, month):
        self.selectedStartDate, self.selectedEndDate = get_monthly_interval(month)
        self.myconto = 'all'

        all_income_rows = self.get_all_income_rows()
        self.incomes_for_time_interval = self.filter_income_for_interval(all_income_rows)
        self.apply_taxes_to_salary()
        table, brutto, taxes, netto, abzuge, uberweisung = self.convert_to_total_income_tabel()
        return table, brutto, taxes, netto, abzuge, uberweisung

    def convert_to_display_table(self, tableHead, table, displayTableHead):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        newTableData = np.empty([table.shape[0], len(displayTableHead)], dtype=object)
        for i, col in enumerate(displayTableHead):
            indxCol = tableHead.index(col)
            newTableData[:,i] = table[:, indxCol]

        return displayTableHead, newTableData

    @property
    def monthly_income(self):
        monthly_income = 0
        for row in self.income:
            if row[self.tableHead.index('freq')] == 1:

                monthly_income += float(row[self.tableHead.index('netto')])
        return round(monthly_income, 2)

    @property
    def irregular_income(self):
        irregular_income = 0
        for row in self.income:
            if row[self.tableHead.index('freq')] > 1:
                irregular_income += float(row[self.tableHead.index('netto')])
        return round(irregular_income, 2)


class Cheltuiala:
    def __init__(self, row, tableHead):
        # print('#####', tableHead)
        self.tableHead = tableHead
        self.read_row(row)
        self.lohnsteuer = None
        self.rentenvers = None
        self.arbeitslosvers = None
        self.krankenvers = None
        self.privatvers = None
        self.brutto = None

    def read_row(self, row):
        for col in self.tableHead:
            exec('self.{} = row[self.tableHead.index("{}")]'.format(col, col))

        if self.pay_day is None:
            self.pay_day = calculate_last_day_of_month(self.valid_from.month, self.valid_from.year)

        if self.auto_ext is None or self.auto_ext == 0:
            self.auto_ext = False
        else:
            self.auto_ext = True

    def set_table(self, table_name):
        self.table = table_name

    @property
    def first_payment(self):
        try:
            first_payment = datetime(self.valid_from.year, self.valid_from.month, self.pay_day)
        except:
            # print(self.id, self.table, self.name)
            # print(self.valid_from.year, self.valid_from.month, self.pay_day)
            # first_payment = calculate_last_day_of_month(selectedStartDate.month)
            first_payment = datetime(self.valid_from.year, self.valid_from.month, calculate_last_day_of_month(self.valid_from.month, self.valid_from.year))
        return first_payment

    @property
    def is_salary(self):
        if self.name == 'Salariu' and self.freq == 1 and self.value:
            is_salary = True
        else:
            is_salary = False
        return is_salary

    @property
    def basic_brutto_35h_salary(self):
        return self.val

    @basic_brutto_35h_salary.setter
    def basic_brutto_35h_salary(self, income):
        self.val = float(income)

    @property
    def monthly_35h_brutto_salary(self):
        return self.val

    @monthly_35h_brutto_salary.setter
    def monthly_35h_brutto_salary(self, income):
        self.val = float(income)

    @property
    def hourly_salary(self):
        hourly_salary = self.monthly_35h_brutto_salary / 4 / 35
        return hourly_salary

    @property
    def brutto_monthly_salary(self):
        val = self.hourly_salary * self.hours * 4
        return val

    @property
    def gesetzliche_abzuge(self):
        try:
            gesetzliche_abzuge = round(self.lohnsteuer +self.rentenvers + self.arbeitslosvers, 2)
        except:
            return None
        return gesetzliche_abzuge

    @property
    def abzuge(self):
        try:
            abzuge = round(self.krankenvers + self.privatvers, 2)
        except:
            return None
        return abzuge

    @property
    def netto(self):
        if self.gesetzliche_abzuge and self.brutto:
            netto = round(self.brutto - self.gesetzliche_abzuge, 2)
        else:
            netto = self.brutto
        return netto

    @property
    def uberweisung(self):
        if self.netto and self.is_salary:
            uberweisung = round(float(self.netto) - self.abzuge, 2)
        else:
            uberweisung = self.netto
        return uberweisung

    def list_of_payments_valid_from_till_selected_end_date(self, selectedEndDate):
        list_of_payments_till_selected_end_date = []
        if self.valid_from <= self.first_payment.date() <= selectedEndDate:
            list_of_payments_till_selected_end_date.append(self.first_payment)

        next_payment = self.first_payment + relativedelta(months=self.freq)
        if next_payment.day != self.pay_day:
            try:
                next_payment = datetime(next_payment.year, next_payment.month, self.pay_day)
            except:
                next_payment = datetime(next_payment.year, next_payment.month, calculate_last_day_of_month(next_payment.month, next_payment.year))
        if self.valid_from <= next_payment.date() <= selectedEndDate:
            list_of_payments_till_selected_end_date.append(next_payment)

        while next_payment.date() <= selectedEndDate:
            next_payment = next_payment + relativedelta(months=self.freq)
            if next_payment.day != self.pay_day:
                try:
                    next_payment = datetime(next_payment.year, next_payment.month, self.pay_day)
                except:
                    # print('#####', next_payment.year, next_payment.month,
                    #                         calculate_last_day_of_month(next_payment.month, next_payment.year))
                    next_payment = datetime(next_payment.year, next_payment.month,
                                            calculate_last_day_of_month(next_payment.month, next_payment.year))
            if self.valid_from <= next_payment.date() <= selectedEndDate:
                list_of_payments_till_selected_end_date.append(next_payment)
        return list_of_payments_till_selected_end_date

    def cut_all_before_selectedStartDate(self, lista, selectedStartDate):
        new_list = []
        for date in lista:
            if date.date() >= selectedStartDate:
                new_list.append(date)
        return new_list

    def cut_all_after_valid_to(self, lista):
        new_list = []
        for date in lista:
            if date.date() <= self.valid_to:
                new_list.append(date)
        return new_list

    def calculate_payments_in_interval(self, selectedStartDate, selectedEndDate):
        list_of_payments_valid_from_till_selected_end_date = self.list_of_payments_valid_from_till_selected_end_date(selectedEndDate)
        # print(20*'*')
        # for i in list_of_payments_valid_from_till_selected_end_date:
        #     print(i)
        # print(20*'*')

        list_of_payments_selected_start_date_till_selected_end_date = self.cut_all_before_selectedStartDate(list_of_payments_valid_from_till_selected_end_date, selectedStartDate)
        # print(20*'*')
        # for i in list_of_payments_selected_start_date_till_selected_end_date:
        #     print(i)
        # print(20*'*')

        if self.valid_to and self.valid_to < selectedEndDate and not self.auto_ext:
            list_of_payments_selected_start_date_till_selected_end_date = self.cut_all_after_valid_to(list_of_payments_selected_start_date_till_selected_end_date)
            # print(20*'*')
            # for i in list_of_payments_selected_start_date_till_selected_end_date:
            #     print(i)
            # print(20*'*')

        return list_of_payments_selected_start_date_till_selected_end_date

    @property
    def first_payment_date(self):
        first_payment_date = datetime(self.valid_from.year, self.valid_from.month, self.pay_day)
        return first_payment_date

    @property
    def payments_for_interval(self):
        return self.pfi

    @payments_for_interval.setter
    def payments_for_interval(self, payments_days):
        self.pfi= payments_days


class CheltuieliPlanificate:
    def __init__(self, ini_file):
        # print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        self.ini_file = ini_file
        self.conf = connect.Config(self.ini_file)
        self.tableHead = ['id', 'name', 'value', 'myconto', 'freq', 'pay_day', 'valid_from', 'valid_to', 'auto_ext']
        self.myAccountsTable = self.sql_rm.Table(self.conf.credentials, 'banca')
        self.myContos = self.myAccountsTable.returnColumn('name')

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

    def tot_no_of_irregular_expenses(self):
        indxMonthly = np.where(self.expenses[:,self.tableHead.index('freq')] != 1)[0]
        monthly = self.expenses[indxMonthly, self.tableHead.index('value')]
        return monthly.shape[0]

    def tot_val_of_irregular_expenses(self):
        indxMonthly = np.where(self.expenses[:,self.tableHead.index('freq')] != 1)[0]
        monthly = self.expenses[indxMonthly, self.tableHead.index('value')]
        if None in monthly:
            monthly = monthly[monthly != np.array(None)]
        totalMonthly = round(sum(monthly.astype(float)), 2)
        return totalMonthly

    def tot_no_of_monthly_expenses(self):
        indxMonthly = np.where(self.expenses[:,self.tableHead.index('freq')] == 1)[0]
        monthly = self.expenses[indxMonthly, self.tableHead.index('value')]
        return monthly.shape[0]

    def tot_val_of_monthly_expenses(self):
        indxMonthly = np.where(self.expenses[:,self.tableHead.index('freq')] == 1)[0]
        monthly = self.expenses[indxMonthly, self.tableHead.index('value')]
        if None in monthly:
            monthly = monthly[monthly != np.array(None)]
        totalMonthly = round(sum(monthly.astype(float)), 2)
        return totalMonthly

    def tot_no_of_expenses(self):
        allValues = self.expenses[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        return len(allValues)

    def tot_val_of_expenses(self):
        allValues = self.expenses[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = round(sum(allValues.astype(float)), 2)
        return totalVal

    def tot_no_of_income(self):
        allValues = self.income[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        return len(allValues)

    def tot_val_of_income(self):
        allValues = self.income[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = round(sum(allValues.astype(float)), 2)
        return totalVal

    def tot_no_of_expenses_income(self):
        allExpenses = self.expenses[:,self.tableHead.index('value')]
        allIncome = self.income[:,self.tableHead.index('value')]
        tot = len(allExpenses) + len(allIncome)
        return tot

    def tot_val_of_expenses_income(self):
        allValues = self.income[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalIncome = round(sum(allValues.astype(float)), 2)
        allValues = self.expenses[:,self.tableHead.index('value')]
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalExpenses = round(sum(allValues.astype(float)), 2)
        return round(totalIncome + totalExpenses, 2)

    def get_all_sql_vals(self):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        all_chelt = []
        for table in self.dataBase.allAvailableTablesInDatabase:
            if table == 'income':
                continue
            active_table = self.sql_rm.Table(self.conf.credentials, table)
            active_table_head = active_table.columnsNames
            if 'table' in self.tableHead:
                self.tableHead.remove('table')
            if 'payDay' in self.tableHead:
                self.tableHead.remove('payDay')
            check = all(item in active_table_head for item in self.tableHead)
            if check:
                # vals = active_table.returnColumns(self.tableHead)
                vals = active_table.returnAllRecordsFromTable()
                for row in vals:
                    row = list(row)
                    chelt = Cheltuiala(row, active_table.columnsNames)
                    chelt.set_table(table)
                    all_chelt.append(chelt)
        return all_chelt

    def filter_dates(self, all_chelt, selectedStartDate, selectedEndDate):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        remaining = []
        for chelt in all_chelt:
            # print(chelt.table, chelt.name, chelt.id, chelt.pay_day)
            payments_in_interval = chelt.calculate_payments_in_interval(selectedStartDate, selectedEndDate)
            # print(payments_in_interval)
            # if chelt.name == 'Steuererklärung_2022':
            #     print(chelt.table, chelt.name, chelt.id, chelt.pay_day, payments_in_interval)
            if isinstance(payments_in_interval, list):
                chelt.payments_for_interval = payments_in_interval
                # print(chelt.table, chelt.name, chelt.id, chelt.pay_day, chelt.payments_for_interval)
                if chelt.payments_for_interval:
                    remaining.append(chelt)
        return remaining

    def filter_conto(self, chelt_list, conto):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        remaining = []
        for ch in chelt_list:
            if conto == 'all' and ch.table != 'intercontotrans':
                remaining.append(ch)
            elif ch.myconto == conto:
                remaining.append(ch)

        return remaining

    def split_expenses_income(self, chelt):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        arr_expenses = []
        arr_income = []
        for ch in chelt:
            if ch.value == 0:
                continue
            for payment_day in ch.payments_for_interval:
                # if ch.value and ch.value > 0:
                #     incomeTable = self.sql_rm.Table(self.conf.credentials, ch.table)
                #     full_row = list(incomeTable.returnRowsWhere(('id', ch.id))[0])
                #     venit_instance = Income(full_row, incomeTable.columnsNames)
                #     ch.value = venit_instance.calculate_income()

                variables = vars(ch)
                row = [ch.table]
                for col in self.tableHead:
                    val = variables[col]
                    row.append(val)
                # print('######', payment_day, type(payment_day))
                row.append(payment_day.date())
                if ch.value and ch.value > 0:
                    arr_income.append(row)
                else:
                    arr_expenses.append(row)
        arr_expenses = np.atleast_2d(arr_expenses)
        arr_income = np.atleast_2d(arr_income)
        self.tableHead.insert(0, 'table')
        self.tableHead.append('payDay')
        return arr_expenses, arr_income

    def prepareTablePlan(self, conto, selectedStartDate, selectedEndDate):
        #print('Module: {}, Class: {}, Def: {}, Caller: {}'.format(__name__, __class__, sys._getframe().f_code.co_name, sys._getframe().f_back.f_code.co_name))
        print(selectedStartDate, selectedEndDate)
        all_chelt = self.get_all_sql_vals()
        # for i in all_chelt:
        #     print(i.freq)
        # all_chelt = self.get_one_time_transactions(all_chelt)

        chelt_in_time_interval = self.filter_dates(all_chelt, selectedStartDate, selectedEndDate)
        # for chelt in chelt_in_time_interval:
        #     print(chelt.table, chelt.name, chelt.id, chelt.pay_day, chelt.conto, chelt.payments_for_interval)

        chelt_after_contofilter = self.filter_conto(chelt_in_time_interval, conto)
        # for chelt in chelt_after_contofilter:
        #     print(chelt.table, chelt.name, chelt.id, chelt.pay_day, chelt.conto, chelt.payments_for_interval)

        self.expenses, self.income = self.split_expenses_income(chelt_after_contofilter)
        if self.expenses.shape == (1, 0):
            expenses = np.empty((0, len(self.tableHead)))
        if self.income.shape == (1, 0):
            income = np.empty((0, len(self.tableHead)))

    def convert_to_display_table(self, tableHead, table, displayTableHead):
        #print('Module: {}, Class: {}, Def: {}'.format(__name__, __class__, sys._getframe().f_code.co_name))
        newTableData = np.empty([table.shape[0], len(displayTableHead)], dtype=object)
        for i, col in enumerate(displayTableHead):
            indxCol = tableHead.index(col)
            newTableData[:,i] = table[:, indxCol]

        return displayTableHead, newTableData


class CheltPlusIncome:
    def __init__(self, ini_file, conto, dataFrom, dataBis):
        self.income = Income(ini_file)
        self.income.prepareTablePlan(conto, dataFrom, dataBis)

        self.chelt = CheltuieliPlanificate(ini_file)
        self.chelt.prepareTablePlan(conto, dataFrom, dataBis)

    @property
    def summary_table(self):
        total_dif = round(self.income.netto + self.chelt.tot_val_of_expenses(), 2)
        monthly_dif = round(self.income.monthly_income + self.chelt.tot_val_of_monthly_expenses(), 2)
        irregular_dif = round(self.income.irregular_income + self.chelt.tot_val_of_irregular_expenses())
        arr = [('', 'Income', 'Expenses', 'Diff'),
               ('Total', self.income.netto, self.chelt.tot_val_of_expenses(), total_dif),
               ('Monthly', self.income.monthly_income, self.chelt.tot_val_of_monthly_expenses(), monthly_dif),
               ('Irregular', self.income.irregular_income, self.chelt.tot_val_of_irregular_expenses(), irregular_dif),
               ]
        arr = np.atleast_2d(arr)
        return arr