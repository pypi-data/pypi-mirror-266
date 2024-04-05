import decimal
import traceback
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import csv
import sys
import os
import sip
import matplotlib.pyplot as plt
from __init__ import __version__ as packVersion
sys.path.append(r'D:\Python\MySQL\SQL_Query')
import connect
np.set_printoptions(linewidth=250)
__version__ = 'V1'


class CheltPlanificate:
    def __init__(self, db_type, data_base_name):
        self.dataBase = connect.DataBase(db_type, data_base_name)

    def filter_dates(self, tableHead, table, selectedStartDate, selectedEndDate):
        # print(sys._getframe().f_code.co_name, tableHead)
        tableHead.append('payDay')
        validFromIndx = tableHead.index('valid_from')
        validToIndx = tableHead.index('valid_to')
        freqIndx = tableHead.index('freq')
        payDayIndx = tableHead.index('pay_day')
        nameIndx = tableHead.index('name')

        payments4Interval = []
        for val in table:
            # print('before', len(val), val)
            validfrom, validTo, freq, payDatum = val[validFromIndx], val[validToIndx], val[freqIndx], val[payDayIndx]
            name = val[nameIndx]
            #daca data expirarii este mai mica decat data de start selectata continua
            if (validTo and validTo < selectedStartDate) or not freq:
                continue
            toBePayed = False
            try:
                payDay = datetime(validfrom.year, validfrom.month, payDatum).date()
            except ValueError:
                payDay = datetime(validfrom.year, validfrom.month+1, 1).date() - relativedelta(days=1)
            except TypeError:
                payDay = validfrom
            except Exception:
                print('OOOO')
                print(traceback.format_exc())
                sys.exit()
            # cat timp data de end selectata este mai mare decat data platii...
            while selectedEndDate >= payDay:
                if selectedStartDate <= payDay <= selectedEndDate:
                    if not validTo or payDay < validTo:
                        tup = [x for x in val]
                        tup.append(payDay)
                        payments4Interval.append(tup)
                        toBePayed = True
                # if name == 'Kfz-Steuer fuer M RA 8612':
                    # print(payDay, type(relativedelta(months=+freq)))

                payDay = payDay + relativedelta(months=+freq)
                try:
                    payDay = datetime(payDay.year, payDay.month, payDatum).date()
                except ValueError:
                    payDay = datetime(payDay.year, payDay.month + 1, 1).date() - relativedelta(days=1)
                except TypeError:
                    payDay = payDay
                except Exception:
                    print('OOOO')
                    print(traceback.format_exc())
                    sys.exit()
                # print(payDay, type(payDay), freq, type(freq), payDay.month+freq)
            if not toBePayed:
                continue
        payments4Interval = np.atleast_2d(payments4Interval)
        return tableHead, payments4Interval

    def get_all_sql_vals(self, tableHead):
        # print(sys._getframe().f_code.co_name, tableHead)
        all_chelt = []
        for table in self.dataBase.tables:
            self.dataBase.active_table = table
            check = all(item in list(self.dataBase.active_table.columnsProperties.keys()) for item in tableHead)
            if check:
                vals = self.dataBase.active_table.returnColumns(tableHead)
                for row in vals:
                    row = list(row)
                    row.insert(0, table)
                    all_chelt.append(row)

        newTableHead = ['table']
        for col in tableHead:
            newTableHead.append(col)

        return newTableHead, all_chelt

    def filter_conto(self, tableHead, table, currentConto):
        # print(sys._getframe().f_code.co_name, tableHead, currentConto)
        if table.shape[1] > 0:
            if currentConto == 'all':
                indxConto = np.where(table[:, tableHead.index('table')] != 'expenses')
            else:
                indxConto = np.where(table[:, tableHead.index('myconto')] == currentConto)
            return tableHead, table[indxConto]
        else:
            return tableHead, np.empty((0, len(tableHead)))

    def split_expenses_income(self, tableHead, table):
        # print(sys._getframe().f_code.co_name)
        indxValue = tableHead.index('value')
        payments = []
        income = []
        for row in table:
            if row[indxValue] > 0:
                income.append(row)
            if row[indxValue] < 0:
                payments.append(row)
        payments = np.atleast_2d(payments)
        income = np.atleast_2d(income)

        return payments, income


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        # Ui_MainWindow, QtBaseClass = uic.loadUiType(r'D:\Python\MySQL\Cheltuieli\GUI\plan_vs_real.ui')
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        path2src, pyFileName = os.path.split(__file__)
        uiFileName = 'plan_vs_real.ui'
        path2GUI = os.path.join(path2src, 'GUI', uiFileName)
        Ui_MainWindow, QtBaseClass = uic.loadUiType(path2GUI)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        title = '{}_{}'.format(pyFileName, __version__)
        self.setWindowTitle(title)

        db_type = 'MySQL'
        self.dataBase = connect.DataBase(db_type, 'cheltuieli')
        self.expensesTableReal = connect.Table(db_type, 'cheltuieli', 'real_expenses')
        self.tableHead = ['name', 'value', 'myconto', 'freq', 'pay_day', 'valid_from', 'valid_to']
        self.cheltPlan = CheltPlanificate(db_type, 'myfolderstructure')
        self.myAccountsTable = connect.Table(db_type, 'myfolderstructure', 'banca')
        self.myContos = self.myAccountsTable.returnColumn('name')

        self.ui.GB_RealExpenses.setVisible(False)
        self.ui.GB_RealIncome.setVisible(False)
        self.ui.GB_PlanIncome.setVisible(False)

        self.populateCBConto()
        self.populateDatesInterval()

        self.prepareTablePlan()
        self.ui.planTable.horizontalHeader().sectionClicked.connect(self.sortPlan)

        self.prepareTableReal()

        self.ui.cbReal.currentIndexChanged.connect(lambda: (self.prepareTableReal(), self.prepareTablePlan()))
        self.ui.DERealFrom.dateTimeChanged.connect(lambda: (self.prepareTableReal(), self.prepareTablePlan()))
        self.ui.DEReaTo.dateTimeChanged.connect(lambda: (self.prepareTableReal(), self.prepareTablePlan()))

        self.ui.realTable.horizontalHeader().sectionClicked.connect(self.sortReal)
        self.ui.realTable.horizontalHeader().sectionDoubleClicked.connect(self.setFilter)

        # self.ui.pbImportCSV.clicked.connect(self.importCSV)
        self.ui.PBComp.clicked.connect(self.compare2plan)
        self.ui.PB_plotTablePie.clicked.connect(self.plotTablePie)
        self.ui.CBIncome.stateChanged.connect(self.showHideIncomeTabels)
        #===========================

    def populateCBConto(self):
        print(sys._getframe().f_code.co_name)
        # contos = self.myAccountsTable.returnColumn('ContoName')
        # self.ui.cbReal.addItems(contos)
        self.ui.cbReal.addItems(self.myContos)

    def populateDatesInterval(self):
        print(sys._getframe().f_code.co_name)
        self.ui.DERealFrom.setDate(QDate(datetime.now().year,
                                         datetime.now().month-2,
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
        matches = ('name', currentConto)
        IBAN = self.myAccountsTable.returnCellsWhere('IBAN', matches)[0]
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
        # self.totals()

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
            predefHeader = ['table_name', 'name', 'value', 'Buchungstag', 'Betrag','Buchungstext', 'Beguenstigter', 'Verwendungszweck']#'Buchungstext',
            newTable = np.empty((table.shape[0], len(predefHeader)), dtype=object)
            for i, colName in enumerate(predefHeader):
                # colName = self.ui.realTable.horizontalHeaderItem(i).text()
                # predefHeader.append(colName)
                colValuesIndx = self.expensesTableReal.columnsNames.index(colName)
                colValues = table[:, colValuesIndx]
                newTable[:, i] = colValues

            indxTableName = predefHeader.index('table_name')
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
                    # self.ui.realTable.item(row, col).setBackground(QtGui.QColor('red'))

        if table.shape[1] > 0:
            allValues = table[:, self.expensesTableReal.columnsNames.index('Betrag')].astype(float)
            if None in allValues:
                allValues = allValues[allValues != np.array(None)]
            totalVal = sum(allValues)
        # self.ui.LEtotalNoExpensesTrans.setText(str(len(table)))
        # self.ui.LEtotalExpensesValue.setText(('{:02f}'.format(totalVal)))

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
        currentConto = self.ui.cbReal.currentText()
        if "Sparkasse" in currentConto:
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

            geom = QtCore.QRect(header.sectionViewportPosition(logical_index), 0, header.sectionSize(logical_index), header.height())
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

    def showHideIncomeTabels(self):
        if self.ui.CBIncome.isChecked():
            self.ui.GB_RealIncome.setVisible(True)
            self.ui.GB_PlanIncome.setVisible(True)
        else:
            self.ui.GB_RealIncome.setVisible(False)
            self.ui.GB_PlanIncome.setVisible(False)

    # def totals(self):
    #     if self.ui.LEtotalNoExpensesTrans.text():
    #         expensesTrans = int(self.ui.LEtotalNoExpensesTrans.text())
    #     else:
    #         expensesTrans = 0
    #     if self.ui.LEtotalNoIncomeTrans.text():
    #         incomeTrans = int(self.ui.LEtotalNoIncomeTrans.text())
    #     else:
    #         incomeTrans = 0
    #
    #     if self.ui.LEtotalExpensesValue.text():
    #         expenses = float(self.ui.LEtotalExpensesValue.text())
    #     else:
    #         expenses = 0
    #     if self.ui.LEtotalIncomeValue.text():
    #         income = float(self.ui.LEtotalIncomeValue.text())
    #     else:
    #         income = 0
    #
    #     trans = expensesTrans + incomeTrans
    #     total = expenses + income
    #
    #     self.ui.LEtotalNoOfRealTransactions.setText(str(trans))
    #     self.ui.LEtotalRealValue.setText(('{:02f}'.format(total)))

    def compare2plan(self):
        self.ui.GB_RealExpenses.setVisible(True)
        realExpenseTable, realExpenseTableHead = self.readRealExpenses()
        planExpenseTable, planExpenseTableHead = self.readPlanExpenses()

        allValues = realExpenseTable[:, realExpenseTableHead.index('Betrag')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalVal = sum(allValues)
        realExpensesDict = {'total': [len(realExpenseTable),totalVal]}

        allValues = planExpenseTable[:, planExpenseTableHead.index('value')].astype(float)
        if None in allValues:
            allValues = allValues[allValues != np.array(None)]
        totalPlanVal = sum(allValues)
        planExpensesDict = {'total': [len(planExpenseTable),totalPlanVal]}

        #unknownTrans color cells red
        unknownTransIndx = np.where(realExpenseTable[:, realExpenseTableHead.index('table_name')] == 'None')[0]
        unknownValues = realExpenseTable[unknownTransIndx, realExpenseTableHead.index('Betrag')].astype(float)
        if None in unknownValues:
            unknownValues = unknownValues[unknownValues != np.array(None)]
        unknownVal = sum(unknownValues)

        realExpensesDict['Unknown'] = [len(unknownTransIndx), unknownVal]
        for row in unknownTransIndx:
            cell = self.ui.realTable.item(row, realExpenseTableHead.index('table_name'))
            cell.setBackground(QtGui.QColor('red'))

        #knownTransactions color cells green
        knownTransIndx = np.where(realExpenseTable[:, realExpenseTableHead.index('table_name')] != 'None')[0]
        knownTrans = realExpenseTable[knownTransIndx]
        # print(knownTrans)
        colTableName = realExpenseTable[knownTransIndx, realExpenseTableHead.index('table_name')]
        colName = realExpenseTable[knownTransIndx, realExpenseTableHead.index('name')]
        realArray = np.stack((colTableName, colName), axis=1)
        uniqRealArray = np.unique(realArray.astype(str), axis=0)
        # print(uniqRealArray)

        planned = []
        plannedPlan = []
        notPlanned = []
        plannedButNotExecuted = []
        for row in uniqRealArray:
            tableName, name = row
            #how many instances in real table???
            indxReal = np.where((realExpenseTable[:, realExpenseTableHead.index('table_name')] == tableName) &
                                (realExpenseTable[:, realExpenseTableHead.index('name')] == name))[0]
            # how many instances in plan table???
            indxPlan = np.where((planExpenseTable[:, planExpenseTableHead.index('table')] == tableName) &
                                (planExpenseTable[:, planExpenseTableHead.index('name')] == name))[0]

            if len(indxReal) == len(indxPlan):
                for i in indxReal:
                    cell = self.ui.realTable.item(i, realExpenseTableHead.index('table_name'))
                    cell.setBackground(QtGui.QColor('green'))
                    planned.append(realExpenseTable[i])
                for i in indxPlan:
                    cell = self.ui.planTable.item(i, planExpenseTableHead.index('table'))
                    cell.setBackground(QtGui.QColor('green'))
                    plannedPlan.append(planExpenseTable[i])
            elif len(indxReal) > len(indxPlan):
                if len(indxPlan) == 0:
                    for i in indxReal:
                        cell = self.ui.realTable.item(i, realExpenseTableHead.index('table_name'))
                        cell.setBackground(QtGui.QColor('orange'))
                        notPlanned.append(realExpenseTable[i])
                else:
                    plannedNo = len(indxReal) - len(indxPlan)
                    for i in indxReal[:plannedNo]:
                        cell = self.ui.realTable.item(i, realExpenseTableHead.index('table_name'))
                        cell.setBackground(QtGui.QColor('green'))
                        planned.append(realExpenseTable[i])
                    for i in indxReal[plannedNo:]:
                        cell = self.ui.realTable.item(i, realExpenseTableHead.index('table_name'))
                        cell.setBackground(QtGui.QColor('orange'))
                        notPlanned.append(realExpenseTable[i])
                    for i in indxPlan:
                        cell = self.ui.planTable.item(i, planExpenseTableHead.index('table'))
                        cell.setBackground(QtGui.QColor('green'))
                        plannedPlan.append(planExpenseTable[i])
            elif len(indxReal) < len(indxPlan):
                plannedNo = len(indxReal) - len(indxPlan)
                for i in indxReal:
                    cell = self.ui.realTable.item(i, realExpenseTableHead.index('table_name'))
                    cell.setBackground(QtGui.QColor('green'))
                    planned.append(realExpenseTable[i])
                for i in indxPlan[:plannedNo]:
                    cell = self.ui.planTable.item(i, planExpenseTableHead.index('table'))
                    cell.setBackground(QtGui.QColor('green'))
                    plannedPlan.append(planExpenseTable[i])

        planned = np.atleast_2d(planned)
        notPlanned = np.atleast_2d(notPlanned)
        plannedPlan = np.atleast_2d(plannedPlan)

        if planned.shape[1] > 0:
            plannedValues = planned[:, realExpenseTableHead.index('Betrag')].astype(float)
            if None in plannedValues:
                plannedValues = plannedValues[plannedValues != np.array(None)]
            plannedValues = sum(plannedValues)
            realExpensesDict['Planned'] = [len(planned), plannedValues]
        if notPlanned.shape[1] > 0:
            notPlannedValues = notPlanned[:, realExpenseTableHead.index('Betrag')].astype(float)
            # print(plannedValues)
            if None in notPlannedValues:
                notPlannedValues = notPlannedValues[notPlannedValues != np.array(None)]
            notPlannedValues = sum(notPlannedValues)
            realExpensesDict['NotPlanned'] = [len(notPlanned), notPlannedValues]
        if plannedPlan.shape[1] > 0:
            plannedValues = plannedPlan[:, planExpenseTableHead.index('value')].astype(float)
            # print(plannedValues)
            if None in plannedValues:
                plannedValues = plannedValues[plannedValues != np.array(None)]
            plannedValues = sum(plannedValues)
            planExpensesDict['executed'] = [len(plannedPlan), plannedValues]

            planExpensesDict['notExecuted'] = [len(planExpenseTable)-len(plannedPlan), totalPlanVal-plannedValues]

        self.populate_GB_RealExpenses(realExpensesDict)
        self.populate_GB_PlanExpenses(planExpensesDict)

    def populate_GB_RealExpenses(self, realExpensesDict):
        grupa = self.ui.GB_RealExpenses
        if grupa.layout() is not None:
            self.deleItemsOfLayout()
        self.gridLayoutRealExpenses = QGridLayout()

        row = 1
        label = QLabel('name')
        self.gridLayoutRealExpenses.addWidget(label, 0, 0)
        label = QLabel('no')
        self.gridLayoutRealExpenses.addWidget(label, 0, 1)
        label = QLabel('val')
        self.gridLayoutRealExpenses.addWidget(label, 0, 2)
        for key, value in realExpensesDict.items():
            no, val = value
            label = QLabel(key)
            label.row = row
            label.col = 0
            if key == 'Unknown':
                label.setStyleSheet('background : red')
            elif key == 'Planned':
                label.setStyleSheet('background : green')
            elif key == 'NotPlanned':
                label.setStyleSheet('background : orange')
                # label.setStyleSheet('color : orange')
            noBox = QLineEdit(str(no))
            noBox.row = row
            noBox.col = 1

            valBox = QLineEdit('{:.2f}'.format(float(val)))
            valBox.row = row
            valBox.col = 2

            self.gridLayoutRealExpenses.addWidget(label, label.row, label.col)
            self.gridLayoutRealExpenses.addWidget(noBox, noBox.row, noBox.col)
            self.gridLayoutRealExpenses.addWidget(valBox, valBox.row, valBox.col)
            row += 1
        grupa.setLayout(self.gridLayoutRealExpenses)

    def populate_GB_PlanExpenses(self, planExpensesDict):
        grupa = self.ui.GB_PlanExpenses
        if grupa.layout() is not None:
            self.deleItemsOfLayout()
        self.gridLayoutPlanExpenses = QGridLayout()

        row = 1
        label = QLabel('name')
        self.gridLayoutPlanExpenses.addWidget(label, 0, 0)
        label = QLabel('no')
        self.gridLayoutPlanExpenses.addWidget(label, 0, 1)
        label = QLabel('val')
        self.gridLayoutPlanExpenses.addWidget(label, 0, 2)
        for key, value in planExpensesDict.items():
            no, val = value
            label = QLabel(key)
            label.row = row
            label.col = 0
            if key == 'Unknown':
                label.setStyleSheet('background : red')
            elif key == 'executed':
                label.setStyleSheet('background : green')
            elif key == 'notExecuted':
                label.setStyleSheet('background : white')
                # label.setStyleSheet('color : orange')
            noBox = QLineEdit(str(no))
            noBox.row = row
            noBox.col = 1

            valBox = QLineEdit('{:.2f}'.format(float(val)))
            valBox.row = row
            valBox.col = 2

            self.gridLayoutPlanExpenses.addWidget(label, label.row, label.col)
            self.gridLayoutPlanExpenses.addWidget(noBox, noBox.row, noBox.col)
            self.gridLayoutPlanExpenses.addWidget(valBox, valBox.row, valBox.col)
            row += 1
        grupa.setLayout(self.gridLayoutPlanExpenses)

    def deleItemsOfLayout(self):
        if self.gridLayoutRealExpenses is not None:
            while self.gridLayoutRealExpenses.count():
                item = self.gridLayoutRealExpenses.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                # else:
                #     self.deleItemsOfLayout(item.layout())
            sip.delete(self.gridLayoutRealExpenses)
        if self.gridLayoutPlanExpenses is not None:
            while self.gridLayoutPlanExpenses.count():
                item = self.gridLayoutPlanExpenses.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                # else:
                #     self.deleItemsOfLayout(item.layout())
            sip.delete(self.gridLayoutPlanExpenses)

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

    def readPlanExpenses(self):
        rows = self.ui.planTable.rowCount()
        cols = self.ui.planTable.columnCount()
        planExpenseTable = np.empty((rows, cols), dtype=object)
        planExpenseTableHead = []
        for row in range(rows):
            for column in range(cols):
                cell = self.ui.planTable.item(row, column)
                planExpenseTable[row, column] = cell.text()
                colName = self.ui.planTable.horizontalHeaderItem(column).text()
                if colName not in planExpenseTableHead:
                    planExpenseTableHead.append(colName)

        return planExpenseTable, planExpenseTableHead

    def prepareTablePlan(self):
        print(sys._getframe().f_code.co_name)
        currentConto = self.ui.cbReal.currentText()

        selectedStartDate = self.ui.DERealFrom.date()
        selectedEndDate = self.ui.DEReaTo.date()
        selectedStartDate = selectedStartDate.toPyDate()
        selectedEndDate = selectedEndDate.toPyDate()

        tableHead, table = self.cheltPlan.get_all_sql_vals(self.tableHead)

        tableHead, payments4Interval = self.cheltPlan.filter_dates(tableHead, table, selectedStartDate, selectedEndDate)
        # print(payments4Interval)
        tableHead, payments4Interval = self.cheltPlan.filter_conto(tableHead, payments4Interval, currentConto)

        payments4Interval, income = self.cheltPlan.split_expenses_income(tableHead, payments4Interval)

        if payments4Interval.shape == (1, 0):
            payments4Interval = np.empty((0, len(tableHead)))
        if income.shape == (1, 0):
            income = np.empty((0, len(tableHead)))

        self.populateExpensesPlan(tableHead, payments4Interval)
        self.populateIncomePlan(tableHead, income)
        # self.totals()

    def populateExpensesPlan(self, tableHead, table):
        print(sys._getframe().f_code.co_name)
        self.ui.planTable.setColumnCount(len(tableHead))
        self.ui.planTable.setHorizontalHeaderLabels(tableHead)
        self.ui.planTable.setRowCount(table.shape[0])
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
                self.ui.planTable.setItem(row, col, item)

        # if table.shape[1] > 0:
        #     allValues = table[:, tableHead.index('value')]
        #     if None in allValues:
        #         allValues = allValues[allValues != np.array(None)]
            # for i in allValues:
            #     print(i, type(i))
            # totalVal = sum(allValues.astype(float))
            # self.ui.LEtotalNoOfTransactions.setText(str(len(table)))
            # self.ui.LEtotalValue.setText(str(totalVal))

    def populateIncomePlan(self, tableHead, table):
        print(sys._getframe().f_code.co_name)
        self.ui.planTableIncome.setColumnCount(len(tableHead))
        self.ui.planTableIncome.setHorizontalHeaderLabels(tableHead)
        self.ui.planTableIncome.setRowCount(table.shape[0])
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
                self.ui.planTableIncome.setItem(row, col, item)

        if table.shape[1] > 0:
            allValues = table[:, tableHead.index('value')]
            if None in allValues:
                allValues = allValues[allValues != np.array(None)]
            # for i in allValues:
            #     print(i, type(i))
            totalVal = sum(allValues.astype(float))
            self.ui.LEtotalNoOfIncome.setText(str(len(table)))
            self.ui.LEtotalIncome.setText(str(totalVal))

    # def totals(self):
    #     if self.ui.LEtotalNoOfTransactions.text():
    #         expensesTrans = int(self.ui.LEtotalNoOfTransactions.text())
    #     else:
    #         expensesTrans = 0
    #     if self.ui.LEtotalNoOfIncome.text():
    #         incomeTrans = int(self.ui.LEtotalNoOfIncome.text())
    #     else:
    #         incomeTrans = 0
    #
    #     if self.ui.LEtotalValue.text():
    #         expenses = float(self.ui.LEtotalValue.text())
    #     else:
    #         expenses = 0
    #     if self.ui.LEtotalIncome.text():
    #         income = float(self.ui.LEtotalIncome.text())
    #     else:
    #         income = 0
    #
    #     trans = expensesTrans + incomeTrans
    #     total = expenses + income
    #
    #     self.ui.LEtotalNo.setText(str(trans))
    #     self.ui.LEtotalVa.setText(str(total))

    def sortPlan(self, logical_index):
        print(sys._getframe().f_code.co_name)
        header = self.ui.planTable.horizontalHeader()
        order = Qt.DescendingOrder
        if not header.isSortIndicatorShown():
            header.setSortIndicatorShown(True)
        elif header.sortIndicatorSection() == logical_index:
            order = header.sortIndicatorOrder()
        header.setSortIndicator(logical_index, order)
        self.ui.planTable.sortItems(logical_index, order)

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
            indx = np.where(realExpenseTable[:, realExpenseTableHead.index('table_name')]==table)
            smallArray = realExpenseTable[indx]
            values = sum(smallArray[:, realExpenseTableHead.index('Betrag')].astype(float))
            txt = '{} = {}'.format(table, values)
            labels.append(txt)
            size = (values/totalVal)*100
            sizes.append(size)


        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.2f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.title.set_text(str(totalVal))
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