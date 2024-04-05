import decimal

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore
from PyQt5.QtCore import *
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import csv
import sys
import os
import json
import matplotlib.pyplot as plt
from __init__ import __version__ as packVersion
from mysqlquerys import connect

np.set_printoptions(linewidth=250)
__version__ = 'V2'


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        path2src, pyFileName = os.path.split(__file__)
        uiFileName = 'chelt_real.ui'
        path2GUI = os.path.join(path2src, 'GUI', uiFileName)
        Ui_MainWindow, QtBaseClass = uic.loadUiType(path2GUI)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        title = '{}_{}'.format(pyFileName, __version__)
        self.setWindowTitle(title)

        ini_file = r"D:\Python\MySQL\database.ini"
        data_base_name = 'cheltuieli'
        self.dataBase = connect.DataBase(ini_file, data_base_name)
        # self.myAccountsTable = connect.Table(ini_file, data_base_name, 'myaccounts')
        self.myAccountsTable = connect.Table(ini_file, 'myfolderstructure', 'banca')
        self.myContos = self.myAccountsTable.returnColumn('name')
        self.expensesTableReal = connect.Table(ini_file, data_base_name, 'real_expenses')

        self.populateCBConto()
        self.populateDatesInterval()
        self.prepareTableReal()

        self.ui.cbReal.currentIndexChanged.connect(self.prepareTableReal)
        self.ui.DERealFrom.dateTimeChanged.connect(self.prepareTableReal)
        self.ui.DEReaTo.dateTimeChanged.connect(self.prepareTableReal)
        self.ui.realTable.horizontalHeader().sectionClicked.connect(self.sortReal)
        self.ui.realTable.horizontalHeader().sectionDoubleClicked.connect(self.setFilter)

        self.ui.CBOrigTableHead.stateChanged.connect(self.prepareTableReal)
        self.ui.pbImportCSV.clicked.connect(self.importCSV)
        self.ui.PBComp.clicked.connect(self.compare2plan)
        self.ui.PB_resetFilter.clicked.connect(self.reset_filter)
        self.ui.PB_plotTablePie.clicked.connect(self.plotTablePie)
        self.ui.PB_plotNamePie.clicked.connect(self.plotNamePie)

    def populateCBConto(self):
        print(sys._getframe().f_code.co_name)
        # contos = self.myAccountsTable.returnColumn('ContoName')
        # self.ui.cbReal.addItems(contos)
        self.ui.cbReal.addItems(self.myContos)

    def populateDatesInterval(self):
        print(sys._getframe().f_code.co_name)
        self.ui.DERealFrom.setDate(QDate(datetime.now().year - 2,
                                         datetime.now().month,
                                         1))
        self.ui.DEReaTo.setDate(QDate(datetime.now().year,
                                      datetime.now().month,
                                      datetime.now().day))

        self.ui.DERealFrom.setCalendarPopup(True)
        self.ui.DEReaTo.setCalendarPopup(True)

    def prepareTableReal(self):
        print(sys._getframe().f_code.co_name)
        self.defaultFilter = True
        self.filterList = []

        currentConto = self.ui.cbReal.currentText()
        col = 'IBAN'
        matches = ('name', currentConto)
        IBAN = self.myAccountsTable.returnCellsWhere(col, matches)[0]
        match1 = ('AuftragsKonto', IBAN)
        matches = [match1]
        res = self.expensesTableReal.filterRows(matches)
        payments4Interval = self.apply_dates_interval_filter(res)
        payments, income = self.split_expenses_income(payments4Interval)

        # self.realExpenses = np.atleast_2d(payments)
        realExpenses = np.atleast_2d(payments)
        realIncome = np.atleast_2d(income)

        self.populateTableReal(realExpenses)
        self.populateTableIncome(realIncome)
        self.totals()

    def split_expenses_income(self, table):
        print(sys._getframe().f_code.co_name)
        indxValue = self.expensesTableReal.columnsNames.index('Betrag')
        payments = []
        income = []
        for row in table:
            if row[indxValue] > 0:
                income.append(row)
            if row[indxValue] <= 0:
                payments.append(row)
        payments = np.atleast_2d(payments)
        income = np.atleast_2d(income)

        return payments, income

    def apply_dates_interval_filter(self, lista):
        selectedStartDate = self.ui.DERealFrom.date()
        selectedEndDate = self.ui.DEReaTo.date()
        selectedStartDate = selectedStartDate.toPyDate()
        selectedEndDate = selectedEndDate.toPyDate()

        buchungsTagIndx = self.expensesTableReal.columnsNames.index('Buchungstag')
        payments4Interval = []
        for row in lista:
            buchungsTag = row[buchungsTagIndx]
            if selectedStartDate <= buchungsTag <= selectedEndDate:
                payments4Interval.append(row)
        return payments4Interval

    def populateTableReal(self, table):
        print(sys._getframe().f_code.co_name)
        self.ui.realTable.clear()
        # print('*********', self.ui.CBOrigTableHead.isChecked())
        if self.ui.CBOrigTableHead.isChecked():
            self.ui.realTable.setColumnCount(len(self.expensesTableReal.columnsNames))
            self.ui.realTable.setHorizontalHeaderLabels(self.expensesTableReal.columnsNames)
            self.ui.realTable.setRowCount(table.shape[0])
            for col in range(table.shape[1]):
                for row in range(table.shape[0]):
                    if isinstance(table[row, col], int) or isinstance(table[row, col], float):
                        item = QTableWidgetItem()
                        item.setData(QtCore.Qt.DisplayRole, table[row, col])
                    elif isinstance(table[row, col], decimal.Decimal):
                        val = float(table[row, col])
                        item = QTableWidgetItem()
                        item.setData(QtCore.Qt.DisplayRole, val)
                    else:
                        item = QTableWidgetItem(str(table[row, col]))
                    self.ui.realTable.setItem(row, col, item)
        else:
            # header = self.ui.realTable.horizontalHeader()
            predefHeader = ['table_name', 'name', 'value', 'Buchungstag', 'Betrag', 'Buchungstext', 'Beguenstigter',
                            'Verwendungszweck']  # 'Buchungstext',
            newTable = np.empty((table.shape[0], len(predefHeader)), dtype=object)
            if table.shape[1] > 0:
                for i, colName in enumerate(predefHeader):
                    # colName = self.ui.realTable.horizontalHeaderItem(i).text()
                    # predefHeader.append(colName)
                    colValuesIndx = self.expensesTableReal.columnsNames.index(colName)
                    colValues = table[:, colValuesIndx]
                    newTable[:, i] = colValues

            self.ui.realTable.setColumnCount(len(predefHeader))
            self.ui.realTable.setHorizontalHeaderLabels(predefHeader)
            self.ui.realTable.setRowCount(table.shape[0])
            for col in range(newTable.shape[1]):
                for row in range(newTable.shape[0]):
                    if isinstance(newTable[row, col], int) or isinstance(newTable[row, col], float):
                        item = QTableWidgetItem()
                        item.setData(QtCore.Qt.DisplayRole, table[row, col])
                    elif isinstance(newTable[row, col], decimal.Decimal):
                        val = float(newTable[row, col])
                        item = QTableWidgetItem()
                        item.setData(QtCore.Qt.DisplayRole, val)
                    else:
                        item = QTableWidgetItem(str(newTable[row, col]))
                    self.ui.realTable.setItem(row, col, item)

        if table.shape[1] > 0:
            allValues = table[:, self.expensesTableReal.columnsNames.index('Betrag')].astype(float)
            if None in allValues:
                allValues = allValues[allValues != np.array(None)]
            totalVal = sum(allValues)
            self.ui.LEtotalNoExpensesTrans.setText(str(len(table)))
            self.ui.LEtotalExpensesValue.setText(str(totalVal))

    def populateTableIncome(self, table):
        print(sys._getframe().f_code.co_name)
        self.ui.realTableIncome.setColumnCount(len(self.expensesTableReal.columnsNames))
        self.ui.realTableIncome.setHorizontalHeaderLabels(self.expensesTableReal.columnsNames)
        self.ui.realTableIncome.setRowCount(table.shape[0])
        for col in range(table.shape[1]):
            for row in range(table.shape[0]):
                if isinstance(table[row, col], int) or isinstance(table[row, col], float):
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, table[row, col])
                elif isinstance(table[row, col], decimal.Decimal):
                    val = float(table[row, col])
                    item = QTableWidgetItem()
                    item.setData(QtCore.Qt.DisplayRole, val)
                else:
                    item = QTableWidgetItem(str(table[row, col]))
                self.ui.realTableIncome.setItem(row, col, item)

        totalVal = 0
        if table.shape[1] > 0:
            allValues = table[:, self.expensesTableReal.columnsNames.index('Betrag')].astype(float)
            if None in allValues:
                allValues = allValues[allValues != np.array(None)]
            totalVal = sum(allValues)
        self.ui.LEtotalNoIncomeTrans.setText(str(len(table)))
        self.ui.LEtotalIncomeValue.setText(str(totalVal))

    def sortReal(self, logical_index):
        print(sys._getframe().f_code.co_name)
        header = self.ui.realTable.horizontalHeader()
        order = Qt.DescendingOrder
        if not header.isSortIndicatorShown():
            header.setSortIndicatorShown(True)
        elif header.sortIndicatorSection() == logical_index:
            order = header.sortIndicatorOrder()
        header.setSortIndicator(logical_index, order)
        self.ui.realTable.sortItems(logical_index, order)

    def importCSV(self):
        print(sys._getframe().f_code.co_name)
        inpFile, _ = QFileDialog.getOpenFileName(None, 'Select .csv file', '', 'CSV files (*.csv)')
        if not inpFile:
            return
        currentConto = self.ui.cbReal.currentText()

        col = 'banca'
        matches = ('name', currentConto)
        banca = self.myAccountsTable.returnCellsWhere(col, matches)[0]
        if banca == 'Stadtsparkasse München':
            with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
                linereader = csv.reader(csvfile, delimiter=';', quotechar='|')
                for i, row in enumerate(linereader):
                    if i == 0:
                        tableHead = [c.strip('"') for c in row]
                        tabHeadDict = {'Auftragskonto': 'Auftragskonto',
                                       'Buchungstag': 'Buchungstag',
                                       'Valutadatum': 'Valutadatum',
                                       'Buchungstext': 'Buchungstext',
                                       'Verwendungszweck': 'Verwendungszweck',
                                       'Glaeubiger ID': 'Glaeubiger',
                                       'Mandatsreferenz': 'Mandatsreferenz',
                                       'Kundenreferenz (End-to-End)': 'Kundenreferenz',
                                       'Sammlerreferenz': 'Sammlerreferenz',
                                       'Lastschrift Ursprungsbetrag': 'Lastschrift',
                                       'Auslagenersatz Ruecklastschrift': 'Auslagenersatz',
                                       'Beguenstigter/Zahlungspflichtiger': 'Beguenstigter',
                                       'Kontonummer/IBAN': 'IBAN',
                                       'BIC (SWIFT-Code)': 'BIC',
                                       'Betrag': 'Betrag',
                                       'Waehrung': 'Waehrung',
                                       'Info': 'Info'}

                        betragIndx = tableHead.index('Betrag')
                        buchungstagIndx = tableHead.index('Buchungstag')
                        valutadatumIndx = tableHead.index('Valutadatum')
                        verwendungszweckIndx = tableHead.index('Verwendungszweck')
                        ibanIndx = tableHead.index('Kontonummer/IBAN')
                        cols = list(tabHeadDict.values())
                        cols.append('path2inp')
                        for col in tableHead:
                            if col not in tabHeadDict.keys():
                                message = 'column {} new in csv table'.format(col)
                                QMessageBox.warning(self, 'Inconsistent Data', message, QMessageBox.Ok)
                                return ()
                            elif tabHeadDict[col] not in self.expensesTableReal.columnsNames:
                                message = 'column {} missing in SQL table'.format(tabHeadDict[col])
                                QMessageBox.warning(self, 'Inconsistent Data', message, QMessageBox.Ok)
                                return ()
                        continue
                    row = [c.strip('"') for c in row]
                    print('row', row)
                    # modify value to float
                    val = row[betragIndx]
                    val = float(val.replace(",", "."))
                    row[betragIndx] = val
                    # modify date format
                    if row[buchungstagIndx] == "" or row[valutadatumIndx] == "":
                        continue
                    buchungstag = self.expensesTableReal.convertDatumFormat4SQL(row[buchungstagIndx])
                    row[buchungstagIndx] = buchungstag

                    valutadatum = self.expensesTableReal.convertDatumFormat4SQL(row[valutadatumIndx])
                    row[valutadatumIndx] = valutadatum

                    # check if already in table
                    verwendungszweck = row[verwendungszweckIndx]
                    iban = row[ibanIndx]

                    matches = [('Buchungstag', str(buchungstag)),
                               ('Valutadatum', str(valutadatum)),
                               ('Betrag', val),
                               ('IBAN', iban),
                               ('Verwendungszweck', verwendungszweck)]

                    res = self.expensesTableReal.returnCellsWhere('id', matches)
                    if res:
                        message = 'row\n{}\nalready existing...skip'.format(row)
                        print(('Buchungstag', str(buchungstag)),
                              ('Valutadatum', str(valutadatum)),
                              ('Betrag', val),
                              ('Verwendungszweck', verwendungszweck))
                        QMessageBox.warning(self, 'Inconsistent Data', message, QMessageBox.Ok)
                        continue
                    else:

                        row.append(inpFile)
                        self.expensesTableReal.add_row(cols, row)
        if banca == 'DeutscheBank':
            col = 'IBAN'
            matches = ('name', currentConto)
            IBAN = self.myAccountsTable.returnCellsWhere(col, matches)[0]

            with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
                linereader = csv.reader(csvfile, delimiter=';', quotechar='|')
                for i, row in enumerate(linereader):
                    if i < 4:
                        continue
                    elif i == 4:
                        tableHead = [c.strip('"') for c in row]
                        print(tableHead)
                        tabHeadDict = {'Booking date': 'Buchungstag',
                                       'Value date': 'Valutadatum',
                                       'Transaction Type': 'Buchungstext',
                                       'Beneficiary / Originator': 'Beguenstigter',
                                       'Payment Details': 'Verwendungszweck',
                                       'IBAN': 'IBAN',
                                       'BIC': 'BIC',
                                       'Customer Reference': 'Kundenreferenz',
                                       'Mandate Reference': 'Mandatsreferenz',
                                       'Creditor ID': 'Glaeubiger',
                                       # 'Compensation amount': 'Sammlerreferenz',
                                       'Original Amount': 'Sammlerreferenz',
                                       'Ultimate creditor': 'Lastschrift',
                                       'Number of transactions': 'Auslagenersatz',
                                       # 'Number of cheques': 'Auslagenersatz',
                                       # 'Debit': 'Betrag',
                                       # 'Credit': 'Betrag',
                                       'Currency': 'Waehrung'
                                       }
                        continue
                    elif row[0] == 'Account balance':
                        continue
                    row = [c.strip('"') for c in row]
                    cols = ['Auftragskonto', 'path2inp']
                    vals = [IBAN, inpFile]
                    for ir, v in enumerate(row):
                        origColName = tableHead[ir]
                        if (origColName == 'Debit' and v != '') or (origColName == 'Credit' and v != ''):
                            # print(origColName, 'Betrag', v)
                            cols.append('Betrag')
                            vals.append(float(v.replace(",", "")))
                        if origColName in list(tabHeadDict.keys()):
                            # print(origColName, tabHeadDict[origColName], v)
                            cols.append(tabHeadDict[origColName])
                            if (tabHeadDict[origColName] == 'Buchungstag') or (
                                    tabHeadDict[origColName] == 'Valutadatum'):
                                v = self.expensesTableReal.convertDatumFormat4SQL(v)
                            vals.append(v)

                    # check if already in table
                    buchungstag = vals[cols.index('Buchungstag')]
                    valutadatum = vals[cols.index('Valutadatum')]
                    iban = vals[cols.index('IBAN')]
                    verwendungszweck = vals[cols.index('Verwendungszweck')]
                    val = vals[cols.index('Betrag')]
                    matches = [('Buchungstag', str(buchungstag)),
                               ('Valutadatum', str(valutadatum)),
                               ('Betrag', val),
                               ('IBAN', iban),
                               ('Verwendungszweck', verwendungszweck)]
                    res = self.expensesTableReal.returnCellsWhere('id', matches)
                    if res:
                        message = 'row\n{}\nalready existing...skip'.format(row)
                        print(('Buchungstag', str(buchungstag)),
                              ('Valutadatum', str(valutadatum)),
                              ('Betrag', val),
                              ('Verwendungszweck', verwendungszweck))
                        QMessageBox.warning(self, 'Inconsistent Data', message, QMessageBox.Ok)
                        continue
                    else:
                        self.expensesTableReal.add_row(cols, vals)
        if banca == 'N26':
            col = 'IBAN'
            matches = ('name', currentConto)
            IBAN = self.myAccountsTable.returnCellsWhere(col, matches)[0]

            with open(inpFile, 'r', encoding='unicode_escape', newline='') as csvfile:
                linereader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for i, row in enumerate(linereader):
                    if i == 0:
                        tableHead = [c.strip('"') for c in row]
                        print(tableHead)
                        tabHeadDict = {'Date': 'Buchungstag',
                                       'Payee': 'Beguenstigter',
                                       'Account number': 'IBAN',
                                       'Transaction type': 'Buchungstext',
                                       'Payment reference': 'Verwendungszweck',
                                       'Amount (EUR)': 'Betrag',
                                       'Amount (Foreign Currency)': 'Mandatsreferenz',
                                       'Type Foreign Currency': 'Waehrung',
                                       'Exchange Rate': 'Lastschrift'
                                       }
                        continue
                    # print(row, type(row))
                    # continue
                    # row = [c.strip('"') for c in row]
                    cols = ['Auftragskonto', 'path2inp']
                    vals = [IBAN, inpFile]

                    for ir, v in enumerate(row):
                        origColName = tableHead[ir]
                        if origColName in list(tabHeadDict.keys()):
                            cols.append(tabHeadDict[origColName])
                            if tabHeadDict[origColName] == 'Buchungstag':
                                v = self.expensesTableReal.convertDatumFormat4SQL(v)
                            if tabHeadDict[origColName] == 'Betrag':
                                v = float(v)
                            vals.append(v)
                    # check if already in table
                    buchungstag = vals[cols.index('Buchungstag')]
                    # beguenstigter = vals[cols.index('Beguenstigter')]
                    iban = vals[cols.index('IBAN')]
                    verwendungszweck = vals[cols.index('Verwendungszweck')]
                    val = vals[cols.index('Betrag')]
                    matches = [('Buchungstag', str(buchungstag)),
                               ('Betrag', val),
                               # ('Beguenstigter', beguenstigter),
                               ('IBAN', iban),
                               ('Verwendungszweck', verwendungszweck)]
                    # print('matches*******', matches)
                    res = self.expensesTableReal.returnCellsWhere('id', matches)
                    if res:
                        message = 'row\n{}\nalready existing...write?'.format(row)
                        print(('Buchungstag', str(buchungstag)),
                              ('Betrag', val),
                              ('Verwendungszweck', verwendungszweck))
                        buttonReply = QMessageBox.warning(self, 'Inconsistent Data', message, QMessageBox.Yes | QMessageBox.No)
                        if buttonReply == QMessageBox.Yes:
                            self.expensesTableReal.add_row(cols, vals)
                        else:
                            continue
                    else:
                        self.expensesTableReal.add_row(cols, vals)

        self.prepareTableReal()

    def setFilter(self, logical_index):
        print(sys._getframe().f_code.co_name)
        colName = self.expensesTableReal.columnsNames[logical_index]
        colType = self.expensesTableReal.get_column_type(colName)
        if colType == 'int':
            filt = FilterWindow.getIntInterval(colName)
            if not filt:
                return
            if isinstance(filt, tuple):
                minInt, maxInt = filt
                filterVals = (str(minInt), str(maxInt))
            elif isinstance(filt, str):
                filterVals = filt
            self.applyFilter(colName, filterVals)
        elif colType == 'date':
            filt = FilterWindow.getDateInterval(colName)
            if not filt:
                return
            if isinstance(filt, tuple):
                minDate, maxDate = filt
                minDate = minDate.toPyDate()
                maxDate = maxDate.toPyDate()
                filterVals = (str(minDate), str(maxDate))
            elif isinstance(filt, str):
                filterVals = filt
            self.applyFilter(colName, filterVals)
        else:
            header = self.ui.realTable.horizontalHeader()

            geom = QtCore.QRect(header.sectionViewportPosition(logical_index), 0, header.sectionSize(logical_index),
                                header.height())
            item = QLineEdit(header)
            item.setGeometry(geom)
            item.show()
            item.setFocus()
            item.editingFinished.connect(lambda: (self.applyFilter(colName, item.text()),
                                                  item.clear(),
                                                  item.hide(),
                                                  item.deleteLater()))

    def applyFilter(self, colName, filter):
        print(sys._getframe().f_code.co_name)
        if filter == '':
            return

        if self.defaultFilter:
            self.ui.lineEditFilterList.clear()
            self.defaultFilter = False

        filterText = self.ui.lineEditFilterList.text()
        if not filterText:
            if isinstance(filter, str):
                filterText += '{}="{}"'.format(colName, filter)
            elif isinstance(filter, tuple):
                filterText += '{} < {} < {}'.format(filter[0], colName, filter[1])
            elif isinstance(filter, list):
                filterText += '{} in {}"'.format(str(filter), colName)
        else:
            if isinstance(filter, str):
                filterText += '; {}="{}"'.format(colName, filter)
            elif isinstance(filter, tuple):
                filterText += '; {} < {} < {}'.format(filter[0], colName, filter[1])
            elif isinstance(filter, list):
                filterText += '; {} in {}"'.format(str(filter), colName)

        self.ui.lineEditFilterList.setText(filterText)

        tup = (colName, filter)
        self.filterList.append(tup)
        realExpenses = self.expensesTableReal.filterRows(self.filterList)
        payments4Interval = self.apply_dates_interval_filter(realExpenses)
        payments, income = self.split_expenses_income(payments4Interval)

        realExpenses = np.atleast_2d(payments)
        realIncome = np.atleast_2d(income)
        if realExpenses.shape == (1, 0):
            realExpenses = np.empty((0, len(self.expensesTableReal.columnsNames)))
        if realIncome.shape == (1, 0):
            realIncome = np.empty((0, len(self.expensesTableReal.columnsNames)))

        self.populateTableReal(realExpenses)
        self.populateTableIncome(realIncome)

    def reset_filter(self):
        self.ui.lineEditFilterList.clear()
        self.prepareTableReal()

    def totals(self):
        if self.ui.LEtotalNoExpensesTrans.text():
            expensesTrans = int(self.ui.LEtotalNoExpensesTrans.text())
        else:
            expensesTrans = 0
        if self.ui.LEtotalNoIncomeTrans.text():
            incomeTrans = int(self.ui.LEtotalNoIncomeTrans.text())
        else:
            incomeTrans = 0

        if self.ui.LEtotalExpensesValue.text():
            expenses = float(self.ui.LEtotalExpensesValue.text())
        else:
            expenses = 0
        if self.ui.LEtotalIncomeValue.text():
            income = float(self.ui.LEtotalIncomeValue.text())
        else:
            income = 0

        trans = expensesTrans + incomeTrans
        total = expenses + income

        self.ui.LEtotalNoOfRealTransactions.setText(str(trans))
        self.ui.LEtotalRealValue.setText(str(total))

    def compare2plan(self):
        expensesTableReal = np.atleast_2d(self.expensesTableReal.data)
        ini_file = 'MySQL'
        data_base_name = 'myfolderstructure'
        self.dataBase = connect.DataBase(ini_file, data_base_name)
        searchCols = ['name', 'value', 'identification']
        cols2write2expensesTableReal = ['name', 'value']

        # loop over each table that includes the searchCols
        for table in self.dataBase.tables:
            self.dataBase.active_table = table
            check = all(item in list(self.dataBase.active_table.columnsProperties.keys()) for item in searchCols)
            if check:
                # loop over each row in table that includes the searchCols
                for row in self.dataBase.active_table.data:
                    print(row)
                    for sCol in searchCols:
                        v = row[self.dataBase.active_table.columnsNames.index(sCol)]
                        # if there is a value in col 'identification' create the condition query
                        if sCol == 'identification' and v:
                            conditions = json.loads(v)
                            cond = ''
                            for key, val in conditions.items():
                                colNo = self.expensesTableReal.columnsNames.index(key)
                                if key == 'Verwendungszweck':
                                    colIndx = self.expensesTableReal.columnsNames.index('Verwendungszweck')
                                    indVerwendungszweck = [x for x, item in enumerate(expensesTableReal[:, colIndx]) if
                                                           val in item]
                                elif key == 'Beguenstigter':
                                    colIndx = self.expensesTableReal.columnsNames.index('Beguenstigter')
                                    indBeguenstigter = [x for x, item in enumerate(expensesTableReal[:, colIndx]) if
                                                        val in item]
                                    print('BINGO', val)
                                    print('BINGO', indBeguenstigter)
                                else:
                                    cond += '(expensesTableReal[:, {}] == "{}") & '.format(colNo, val)
                            cond = cond[:-2]
                            ind = np.where(eval(cond))
                            if 'Verwendungszweck' in conditions.keys():
                                newInd = []
                                for ii in ind[0]:
                                    if ii in indVerwendungszweck:
                                        newInd.append(ii)
                                ind = newInd

                            if 'Beguenstigter' in conditions.keys():
                                newInd = []
                                for ii in ind[0]:
                                    if ii in indBeguenstigter:
                                        newInd.append(ii)
                                ind = newInd

                            # interrogate expensesTableReal for rows that fulfill the condition
                            # and do a loop over each of them
                            for rowExp in expensesTableReal[ind]:
                                expensesTableRowId = rowExp[self.expensesTableReal.columnsNames.index('id')]
                                if table == 'knowntrans':
                                    category = row[self.dataBase.active_table.columnsNames.index('category')]
                                    print(row)
                                    print(category)
                                    self.expensesTableReal.changeCellContent('table_name', category, 'id',
                                                                             expensesTableRowId)
                                else:
                                    self.expensesTableReal.changeCellContent('table_name', table, 'id',
                                                                             expensesTableRowId)
                                for wCol in cols2write2expensesTableReal:
                                    val = row[self.dataBase.active_table.columnsNames.index(wCol)]
                                    self.expensesTableReal.changeCellContent(wCol, val, 'id', expensesTableRowId)

        self.prepareTableReal()

    def readRealExpenses(self):
        rows = self.ui.realTable.rowCount()
        cols = self.ui.realTable.columnCount()
        realExpenseTable = np.empty((rows, cols), dtype=object)
        realExpenseTableHead = []
        for row in range(rows):
            for column in range(cols):
                cell = self.ui.realTable.item(row, column)
                realExpenseTable[row, column] = cell.text()
                colName = self.ui.realTable.horizontalHeaderItem(column).text()
                if colName not in realExpenseTableHead:
                    realExpenseTableHead.append(colName)

        return realExpenseTable, realExpenseTableHead

    def plotTablePie(self):
        realExpenseTable, realExpenseTableHead = self.readRealExpenses()
        allValues = realExpenseTable[:, realExpenseTableHead.index('Betrag')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = sum(allValues)

        colTableName = realExpenseTable[:, realExpenseTableHead.index('table_name')]
        labels = []
        sizes = []
        for table in np.unique(colTableName):
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('table_name')] == table)
            smallArray = realExpenseTable[indx]
            values = sum(smallArray[:, realExpenseTableHead.index('Betrag')].astype(float))
            txt = '{} = {:.2f}'.format(table, values)
            labels.append(txt)
            size = (values / totalVal) * 100
            sizes.append(size)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90)
        ax1.axis('equal')
        plt.legend(title='Total: {:.2f}'.format(totalVal))
        plt.show()

    def plotNamePie(self):
        realExpenseTable, realExpenseTableHead = self.readRealExpenses()
        allValues = realExpenseTable[:, realExpenseTableHead.index('Betrag')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = sum(allValues)

        colTableName = realExpenseTable[:, realExpenseTableHead.index('name')]
        labels = []
        sizes = []
        for table in np.unique(colTableName):
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('name')] == table)
            smallArray = realExpenseTable[indx]
            values = sum(smallArray[:, realExpenseTableHead.index('Betrag')].astype(float))
            txt = '{} = {:.2f}'.format(table, values)
            labels.append(txt)
            size = (values / totalVal) * 100
            sizes.append(size)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90)
        ax1.axis('equal')
        plt.legend(title='Total: {:.2f}'.format(totalVal))
        plt.show()


class FilterWindow(QDialog):
    def __init__(self, colType, colName):
        super(FilterWindow, self).__init__()
        path2src, pyFileName = os.path.split(__file__)
        uiFileName = 'filterWindow.ui'
        path2GUI = os.path.join(path2src, 'GUI', uiFileName)
        Ui_MainWindow, QtBaseClass = uic.loadUiType(path2GUI)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.colName = colName
        self.ui.GB_DateInterval.setVisible(False)
        self.ui.GB_IntInterval.setVisible(False)
        self.ui.checkBoxDateInterval.stateChanged.connect(self.openDateInterval)
        self.ui.checkBoxIntInterval.stateChanged.connect(self.openIntInterval)

        self.rejected.connect(self.byebye)

        if colType == 'int':
            self.ui.GB_IntInterval.setVisible(True)
            self.ui.lineEdit_max.setEnabled(False)
        if colType == 'date':
            self.ui.GB_DateInterval.setVisible(True)
            self.ui.dateEditTo.setEnabled(False)

    def openIntInterval(self):
        if self.ui.checkBoxIntInterval.isChecked():
            self.ui.lineEdit_max.setEnabled(True)
            self.ui.label_int.setText('< {} <'.format(self.colName))
        else:
            self.ui.lineEdit_max.setEnabled(False)
            self.ui.label_int.setText('= {}'.format(self.colName))

    def openDateInterval(self):
        if self.ui.checkBoxDateInterval.isChecked():
            self.ui.dateEditTo.setEnabled(True)
            self.ui.label_date.setText('< {} <'.format(self.colName))
        else:
            self.ui.dateEditTo.setEnabled(False)
            self.ui.label_date.setText('= {}'.format(self.colName))

    def byebye(self):
        self.close()

    def intInterval(self):
        if self.ui.checkBoxIntInterval.isChecked():
            tup = (self.ui.lineEdit_min.text(), self.ui.lineEdit_max.text())
            return tup
        else:
            return self.ui.lineEdit_min.text()

    def dateInterval(self):
        if self.ui.checkBoxDateInterval.isChecked():
            tup = (self.ui.dateEditFrom.date(), self.ui.dateEditTo.date())
            return tup
        else:
            return self.ui.dateEditFrom.date()

    @staticmethod
    def getIntInterval(colName):
        dialog = FilterWindow('int', colName)
        result = dialog.exec_()
        filt = dialog.intInterval()
        if result == QDialog.Accepted:
            return filt
        else:
            return None

    @staticmethod
    def getDateInterval(colName):
        dialog = FilterWindow('date', colName)
        result = dialog.exec_()
        filt = dialog.dateInterval()
        if result == QDialog.Accepted:
            return filt
        else:
            return None


def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    # sys.exit(app.exec_())
    app.exec_()


if __name__ == '__main__':
    main()
