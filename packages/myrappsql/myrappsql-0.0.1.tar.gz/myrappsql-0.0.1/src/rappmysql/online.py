from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, redirect, url_for
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import traceback
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re
import os
import numpy as np
from mysqlquerys import connect
from mysqlquerys import mysql_rm
from cheltuieli import chelt_plan
from cheltuieli.chelt_plan import CheltuieliPlanificate, Income
from cheltuieli.masina import Masina
from cheltuieli.kalendar import Kalendar

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://newuser_radu:Paroladetest_1234@localhost/cheltuieli_desktop"
app.config['SECRET_KEY'] = "my super secret"


login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'

ini_file = 'static/wdb.ini'
kalendar_ini_file = 'static/kalendar.ini'
# ini_file = 'static/heroku.ini'
conf = connect.Config(ini_file)


class Users(UserMixin):
    def __init__(self, user_name):
        self.user_name = user_name

        self.users_table = mysql_rm.Table(conf.credentials, 'users')

    @property
    def id(self):
        matches = ('username', self.user_name)
        user_id = self.users_table.returnCellsWhere('id', matches)
        return user_id

    # @property
    # def bla(self):
    #     matches = ('id', 5)
    #     print('nnnnn', self.user_name)
    #     user_id = self.users_table.returnCellsWhere('id', matches)[0]
    #     print('ÖÖ__ÖÖÖÖ', user_id)
    #     return user_id

    @property
    def hashed_password(self):
        matches = ('username', self.user_name)
        hashed_password = self.users_table.returnCellsWhere('password', matches)[0]
        return hashed_password

    def verify_password(self, password):
        return check_password_hash(self.hashed_password, password)


@login_manager.user_loader
def load_user(user_id):
    # print(sys._getframe().f_code.co_name, request.method)
    mat = int(re.findall("\[(.+?)\]", user_id)[0])
    matches = ('id', mat)
    users_table = mysql_rm.Table(conf.credentials, 'users')
    name = users_table.returnCellsWhere('username', matches)[0]
    user = Users(name)
    return user


@app.route('/', methods=['GET', 'POST'])
def index():
    # print(sys._getframe().f_code.co_name, request.method)
    print('++++', request.method)
    if request.method == 'POST':
        print('lllll')
    else:
        print('BOOOOO')

    return render_template('index.html')#, userDetails='all_chelt', database_name='heroku_6ed6d828b97b626'


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        user = Users(username)
        if user.verify_password(request.form['password']):
            login_user(user)
            return redirect(url_for("index"))
    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # print(sys._getframe().f_code.co_name, request.method)
    conf = connect.Config(ini_file)
    users_table = mysql_rm.Table(conf.credentials, 'users')
    # users = users_table.returnAllRecordsFromTable()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cols = ('username', 'email', 'password')
        hash = generate_password_hash(password)
        vals = (username, email, hash)
        users_table.addNewRow(cols, vals)
    elif request.method == 'GET':
        print('****', request.method)

    return render_template('register.html')


@app.route('/cheltuieli', methods=['GET', 'POST'])
@login_required
def cheltuieli():
    chelt_app = CheltuieliPlanificate(ini_file)
    income_app = Income(ini_file)
    dataFrom, dataBis = chelt_plan.default_interval()
    conto = 'all'

    if request.method == 'POST':
        month = request.form['month']
        year = int(request.form['year'])
        conto = request.form['conto']
        dataFrom = request.form['dataFrom']
        dataBis = request.form['dataBis']
        if month != 'interval':
            dataFrom, dataBis = chelt_plan.get_monthly_interval(month, year)
        elif month == 'interval' and (dataFrom == '' or dataBis == ''):
            dataFrom, dataBis = chelt_plan.default_interval()
        else:
            try:
                dataFrom = datetime.strptime(dataFrom, "%Y-%m-%d")
                dataBis = datetime.strptime(dataBis, "%Y-%m-%d")
                print(dataFrom.date(), dataBis.date())
            except:
                print(traceback.format_exc())
    try:
        if isinstance(dataFrom, datetime):
            chelt_app.prepareTablePlan(conto, dataFrom.date(), dataBis.date())
            income_app.prepareTablePlan(conto, dataFrom.date(), dataBis.date())
            ch = chelt_plan.CheltPlusIncome(ini_file, conto, dataFrom.date(), dataBis.date())
        elif isinstance(dataFrom, date):
            chelt_app.prepareTablePlan(conto, dataFrom, dataBis)
            income_app.prepareTablePlan(conto, dataFrom, dataBis)
            ch = chelt_plan.CheltPlusIncome(ini_file, conto, dataFrom, dataBis)
    except:
        print(traceback.format_exc())

    return render_template('cheltuieli.html',
                           expenses=chelt_app.expenses,
                           income=income_app.income,
                           income_tab_head=income_app.tableHead,
                           total_netto=income_app.netto,
                           total_taxes=income_app.taxes,
                           total_brutto=income_app.brutto,
                           salary_uberweisung=income_app.salary_uberweisung,
                           salary_abzuge=income_app.salary_abzuge,
                           salary_netto=income_app.salary_netto,
                           salary_gesetzliche_abzuge=income_app.salary_gesetzliche_abzuge,
                           salary_brutto=income_app.salary_brutto,
                           tot_no_of_monthly_expenses=chelt_app.tot_no_of_monthly_expenses(),
                           tot_val_of_monthly_expenses=chelt_app.tot_val_of_monthly_expenses(),
                           tot_no_of_irregular_expenses=chelt_app.tot_no_of_irregular_expenses(),
                           tot_val_of_irregular_expenses=chelt_app.tot_val_of_irregular_expenses(),
                           tot_no_of_expenses=chelt_app.tot_no_of_expenses(),
                           tot_val_of_expenses=chelt_app.tot_val_of_expenses(),
                           summary_table=ch.summary_table,
                           tot_val_of_income='chelt_app.tot_val_of_income()',
                           dataFrom=dataFrom,
                           dataBis=dataBis
                           )


@app.route('/masina', methods=['GET', 'POST'])
def masina():
    print(sys._getframe().f_code.co_name, request.method)
    app_masina = Masina(ini_file)
    dataFrom, dataBis = app_masina.default_interval
    alim_type = None
    if request.method == 'POST':
        if "filter" in request.form:
            month = request.form['month']
            year = int(request.form['year'])
            alim_type = request.form['type']
            if alim_type == 'all':
                alim_type = None
            dataFrom = request.form['dataFrom']
            dataBis = request.form['dataBis']

            if month != 'interval':
                dataFrom, dataBis = app_masina.get_monthly_interval(month, year)
            elif month == 'interval' and (dataFrom == '' or dataBis == ''):
                dataFrom, dataBis = app_masina.default_interval
            else:
                try:
                    dataFrom = datetime.strptime(dataFrom, "%Y-%m-%d")
                    dataBis = datetime.strptime(dataBis, "%Y-%m-%d")
                except:
                    print(traceback.format_exc())
        elif "add_alim" in request.form:
            date = request.form['data']
            alim_type = request.form['type']
            brutto = request.form['brutto']
            amount = request.form['amount']
            km = request.form['km']
            ppu = round(float(brutto)/float(amount), 3)
            columns = ['data', 'type', 'brutto', 'amount', 'ppu', 'km']
            values = [date, alim_type, brutto, amount, ppu, km]
            redirect(url_for('masina'))
            app_masina.insert_new_alim(columns, values)
        elif 'upload_file' in request.form:
            file = request.files['myfile']
            filename = secure_filename(file.filename)
            fl = os.path.join("D:\Python\MySQL", filename)
            file.save(fl)
            with open(fl) as f:
                file_content = f.read()
                print(file_content)
            return file_content
        # else:
        #     print("AAAA")
    print('*****dataFrom', dataFrom)
    print('*****dataBis', dataBis)
    print('*****alim_type', alim_type)
    alimentari = app_masina.get_alimentari_for_interval_type(dataFrom, dataBis, alim_type)
    return render_template('masina.html',
                           userDetails=alimentari,
                           dataFrom=dataFrom.date(),
                           dataBis=dataBis.date(),
                           tabel_alimentari=app_masina.table_alimentari,
                           tabel_totals=app_masina.table_totals,
                           types_of_costs=app_masina.types_of_costs
                           )


@app.route('/kalendar', methods=['GET', 'POST'])
def kalendar():
    print(sys._getframe().f_code.co_name, request.method)
    app_program = Kalendar(kalendar_ini_file)
    dataFrom, dataBis = app_program.default_interval
    # alim_type = None
    if request.method == 'POST':
        if "add_to_kalendar" in request.form:
            person = request.form['person']
            termin = request.form['termin']
            dataFrom = request.form['dataFrom']
            dataBis = request.form['dataBis']
            # print('person', person)
            # print('dataFrom', dataFrom)
            # print('dataBis', dataBis)
            # print('termin', termin)
            columns = ['start', 'finish', person]
            values = [dataFrom, dataBis, termin]
            app_program.insert_new_termin(columns, values)

    programari = app_program.get_appointments_in_interval('all', dataFrom, dataBis)

    tableHead, table = programari[0], programari[1:]

    return render_template('kalendar.html',
                           tableHead=tableHead,
                           tableData=table,
                           persons=app_program.persons,
                           # tot_el=app_masina.tot_electric,
                           # tot_benz=app_masina.tot_benzina,
                           dataFrom=dataFrom,
                           dataBis=dataBis,
                           )


if __name__ == "__main__":
    app.run(debug=True)
