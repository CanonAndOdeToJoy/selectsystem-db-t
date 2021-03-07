from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import click
from flask_login import login_user
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xsSZD0420@localhost:3306/selectsystem?utf8mb4'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_DEBUG'] = True
db = SQLAlchemy(app)


class Student(db.Model):
    __tablename__ = 'student'
    sid = db.Column(db.String(10), primary_key=True)
    spassword = db.Column(db.String(20))


class Teacher(db.Model):
    __tablename__ = 'teacher'
    tid = db.Column(db.String(10), primary_key=True)
    tpassword = db.Column(db.String(20))


class Schoice(db.Model):
    __tablename__ = 'schoice'
    id = db.Column(db.String(10), db.ForeignKey('student.sid'), primary_key=True)
    firstchoice = db.Column(db.String(10)) #####
    secondchoice = db.Column(db.String(10))


class Tchoice(db.Model):
    __tablename = 'tchoice'
    sid = db.Column(db.String(10), db.ForeignKey('student.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacher.tid'), primary_key=True)
    isfirst = db.Column(db.Integer)


class Final(db.Model):
    __tablename = 'final'
    sid = db.Column(db.String(10), db.ForeignKey('student.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacher.tid'), primary_key=True)


class Studentinf(db.Model):
    __tablename = 'studentinf'
    sid = db.Column(db.String(10), db.ForeignKey('student.sid'), primary_key=True)
    name = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    phone = db.Column(db.String(20))


class Teacherinf(db.Model):
    __tablename = 'teacherinf'
    tid = db.Column(db.String(10), db.ForeignKey('teacher.tid'), primary_key=True)
    name = db.Column(db.String(20))
    title = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.context_processor
def inject_user():
    teacher = Teacher.query.first()
    return dict(teacher=teacher)


@app.route('/')
def index():
    stu = Schoice.query.filter_by(firstchoice='12001').all()
    return render_template('index.html', students=stu)


@app.errorhandler(404)
def page_not_found(e):
    stu = Student.query.first()
    return render_template('404.html'), 404


@app.route('/thome')
def thome():
    stu = Final.query.filter_by(tid='12001').all()
    return render_template('thome.html', students=stu)


@app.route('/tchoice', methods=['GET', 'POST'])
def tchoice():
    if request.method == 'POST':
        name = request.form.get('name')
        sid = request.form.get('sid')
        if not name or not sid:
            flash('Invalid input.')
            return redirect(url_for('index'))
        studentinf = Studentinf.query.filter_by(sid=sid).first()
        if studentinf.name != name:
            flash('Invalid input')
        else:
            studentchoice = Schoice.query.filter_by(id='18120001')
            if studentchoice.firstchoice == '12001':
                f = Final.query.filter_by(sid=sid).first()
                f.tid = '12001'
                tchoice = Tchoice.query.filter_by(sid=sid).first()
                tchoice.tid = '12001'
                tchoice.isfirst = 1
                db.session.commit()
            elif studentchoice.second =='12001':
                tchoice = Tchoice.query.filter_by(sid=sid).first()
                tchoice.tid = '12001'
                tchoice.isfirst = 0
                db.session.commit()
            else:
                flash('学生未选你！')
        return redirect(url_for('tchoice'))
    stu = Student.query.first()
    tea = Teacher.query.all()
    return render_template('tchoice.html', teachers=tea)
