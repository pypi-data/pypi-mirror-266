import chelt_plan
import kalendar
import masina
import salariu_prime
from mysqlquerys import connect, mysql_rm
from datetime import date, datetime
import time


def get_cheltuieli(ini_file, selectedStartDate, selectedEndDate):
    app = chelt_plan.CheltuieliPlanificate(ini_file)
    app.prepareTablePlan('all', selectedStartDate.date(), selectedEndDate.date())
    # for i in app.expenses:
    #     print(i)
    # print(app.tot_val_of_monthly_expenses())
    # print(app.tot_val_of_expenses())
    # print(app.tot_val_of_irregular_expenses())


def get_income(ini_file, selectedStartDate, selectedEndDate):
    income = chelt_plan.Income(ini_file)
    income.prepareTablePlan('all', selectedStartDate.date(), selectedEndDate.date())
    # print(20*'#')
    # print(income.tableHead)
    # for i in income.income:
    #     print(i)
    # print(income.netto)
    # print(income.monthly_income)
    # print(income.irregular_income)


def get_totals(ini_file, conto, dataFrom, dataBis):
    ch = chelt_plan.CheltPlusIncome(ini_file, conto, dataFrom, dataBis)
    print(ch.summary_table)


def get_program(ini_file, selectedStartDate, selectedEndDate):
    program = kalendar.Kalendar(ini_file)
    # print(program.default_interval)
    appointments = program.get_appointments_in_interval('all', selectedStartDate, selectedEndDate)
    for i in appointments:
        print(i)


def get_auto_vals(ini_file, selectedStartDate, selectedEndDate):
    auto = masina.Masina(ini_file)
    alimentari = auto.get_alimentari_for_interval_type(selectedStartDate, selectedEndDate, 'benzina')
    print(alimentari)
    print(auto.table_totals)


def main():
    script_start_time = time.time()
    selectedStartDate = datetime(2024, 1, 1, 15, 0, 0)
    selectedEndDate = datetime(2024, 2, 15, 0, 0, 0)

    income_ini = r"D:\Python\MySQL\cheltuieli_db.ini"
    # income_ini = r"D:\Python\MySQL\kalendar.ini"

    # get_cheltuieli(income_ini, selectedStartDate, selectedEndDate)
    # get_income(income_ini, selectedStartDate, selectedEndDate)
    # get_program(income_ini, selectedStartDate, selectedEndDate)
    # get_auto_vals(income_ini, selectedStartDate, selectedEndDate)
    get_totals(income_ini, 'all', selectedStartDate.date(), selectedEndDate.date())


    scrip_end_time = time.time()
    duration = scrip_end_time - script_start_time
    duration = time.strftime("%H:%M:%S", time.gmtime(duration))
    print('run time: {}'.format(duration))

if __name__ == '__main__':
    main()
