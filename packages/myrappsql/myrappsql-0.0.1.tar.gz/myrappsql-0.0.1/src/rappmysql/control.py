import chelt_plan
from mysqlquerys import connect
from datetime import date


def main():
    selectedStartDate = date(2021, 12, 30)
    selectedEndDate = date(2024, 1, 29)

    app = chelt_plan.CheltuieliPlanificate()
    app.prepareTablePlan('EC', selectedStartDate, selectedEndDate)
    print(app.expenses)

if __name__ == '__main__':
    main()
