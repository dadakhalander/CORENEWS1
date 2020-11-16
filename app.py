from flask import Flask, render_template, request, session, url_for, redirect, jsonify
import pymysql
import pandas as pd
app = Flask(__name__)
app.secret_key = 'random string'

newspaper=''

#Database Connection
def dbConnection():
    connection = pymysql.connect(host="35.208.147.193", user="inbotics_testing", password="inbotesting", database="inbotics_testing2017")
    #connection = pymysql.connect(host="localhost", user="root", password="root", database="newsclassification")
    return connection


#close DB connection
def dbClose():
    dbConnection().close()
    return


@app.route('/index')
@app.route('/')
def index():
    session['userloc']= request.args.get("location")
    locationis=session['userloc']
    print(locationis)
    return render_template('index.html')


@app.route('/home')
def home():
    if 'user' in session:
        ht_cnt = 0
        toi_cnt = 0
        ie_cnt = 0
        d = {'ht': 0, 'toi': 0, 'ie': 0}
        b = {}
        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute('SELECT * FROM userdetails WHERE mobile = %s',
                                      (session['user']))
        res = cursor.fetchone()
        print(res)
        if result_count > 0:
            print(result_count)
            session['uid'] = res[0]
            ht_cnt = res[6]
            toi_cnt = res[7]
            ie_cnt = res[8]
            d['ht'] = ht_cnt
            d['toi'] = toi_cnt
            d['ie'] = ie_cnt

            print(d)
            a = sorted(d.items(), key=lambda x: x[1], reverse=True)
            b.update(a)
            print(b)
            list = []
            for key in b.keys():
                list.append(key)
            print(list)
            #session['sorted_dict'] = list
        #return render_template('home1.html',user=session['user'], s=session['sorted_dict'])
        return render_template('home.html', user=session['name'], s=list)
    return redirect(url_for('index'))


@app.route('/login', methods=["GET","POST"])
def login():
    msg = ''
    # ht_cnt = 0
    # toi_cnt = 0
    # ie_cnt = 0
    # d = {'ht': 0, 'toi': 0, 'ie': 0}
    # b= {}
    if request.method == "POST":
        # session.pop('user',None)
        mobno = request.form.get("mobile")
        password = request.form.get("pas")
        con = dbConnection()
        cursor = con.cursor()
        result_count = cursor.execute('SELECT * FROM userdetails WHERE mobile = %s AND password = %s',(mobno, password))
        res = cursor.fetchone()
        print(res)
        if result_count > 0:
            print(result_count)
            session['user'] = mobno
            session['name'] = res[1]
            session['uid'] = res[0]
            # ht_cnt = res[6]
            # toi_cnt = res[7]
            # ie_cnt = res[8]
            # d['ht'] = ht_cnt
            # d['toi'] = toi_cnt
            # d['ie'] = ie_cnt
            # print(d)
            # a = sorted(d.items(), key=lambda x: x[1], reverse=True)
            # b.update(a)
            # print(b)
            # list = []
            # for key in b.keys():
            #     list.append(key)
            # print(list)

            # session['sorted_dict']= list
            return redirect(url_for('home'))
        else:
            print(result_count)
            msg = 'Incorrect username/password!'
            return render_template('login.html')
    return render_template('login.html')

@app.route('/register', methods=["GET","POST"])
def register():
    print("register")
    if request.method == "POST":
        try:
            name = request.form.get("name")
            address = request.form.get("address")
            mailid = request.form.get("mailid")
            mobile = request.form.get("mobile")
            pass1 = request.form.get("pass1")
            con = dbConnection()
            cursor = con.cursor()
            cursor.execute('SELECT * FROM userdetails WHERE mobile = %s', (mobile))
            res = cursor.fetchone()
            if not res:
                sql = "INSERT INTO userdetails (name, address, email, mobile, password) VALUES (%s, %s, %s, %s, %s)"
                val = (name, address, mailid, mobile, pass1)
                cursor.execute(sql, val)
                con.commit()
                
                sql1 = "INSERT INTO readingcount (uid, ht_count, toi_count, ie_count) VALUES (%s, %s, %s, %s)"
                val1 = (mobile,int(0),int(0),int(0))
                cursor.execute(sql1, val1)
                con.commit()
                status= "success"
                return redirect(url_for('index'))
            else:
                status = "Already available"
            return status
        except Exception as inst:
            print(inst)
            print("Exception occured at user registration")
            return redirect(url_for('index'))
        finally:
            dbClose()
    return render_template('register.html')


#logout code
@app.route('/news', methods=['GET', 'POST'])
def news():
    global newspaper
    if 'user' in session:
        con = dbConnection()
        cursor = con.cursor()
        if 'view' in request.args:
            n = request.args['view']
            newspaper=n
            if n == 'ie':
                icount = 0
                cursor.execute('SELECT * FROM userdetails WHERE mobile = %s', (session['user']))
                res = cursor.fetchone()
                icount = res[8]
                icount1 = icount + 1
                cursor.execute('update userdetails SET ie_count = %s WHERE mobile = %s', (icount1, session['user']))
                con.commit()
            if n == 'toi':
                icount = 0
                cursor.execute('SELECT * FROM userdetails WHERE mobile = %s', (session['user']))
                res = cursor.fetchone()
                icount = res[7]
                icount1 = icount + 1
                cursor.execute('update userdetails SET toi_count = %s WHERE mobile = %s', (icount1, session['user']))
                con.commit()
            if n == 'ht':
                icount = 0
                cursor.execute('SELECT * FROM userdetails WHERE mobile = %s', (session['user']))
                res = cursor.fetchone()
                icount = res[6]
                icount1 = icount + 1
                cursor.execute('update userdetails SET ht_count = %s WHERE mobile = %s', (icount1, session['user']))
                con.commit()
        if 'location' in request.args:
            session['loc']= request.args['location']
            #session['userloc']= request.args.get("location")
        return redirect(url_for('city'))
        #return render_template('home.html',user=session['user'])
    return redirect(url_for('index'))


#logout code
@app.route('/citynews', methods=['GET', 'POST'])
def citynews():
    global newspaper
    if 'user' in session:
        Corpus=pd.DataFrame()
        if 'location' in request.args:
            location= request.args['location']
        print("location is "+location)   
        Corpus = pd.read_csv(r"allnews3.csv",encoding='latin-1',error_bad_lines=False)
        print("newspaperis "+newspaper)
        Corpus=Corpus[(Corpus['label']==location+"") & (Corpus['np']==newspaper)]
        
        
        
        return render_template("citynews.html",name=location, data=Corpus.to_html())
        #return render_template('home.html',user=session['user'])
    return redirect(url_for('index'))


@app.route('/city')
def city():
    if 'user' in session:
        loc ='mumbai' #session['userloc']#'mumbai'# session['loc']
        print(loc)
        locationis=session['userloc']
        return render_template('city.html', user=session['name'], loc=loc,userlocation=locationis)
    return redirect(url_for('index'))


#logout code
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run('0.0.0.0')
    #app.run()
