from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
import click
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:xsSZD0420@localhost:3306/selectsystem?utf8mb4'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SECRET_KEY'] = '123456'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['FLASK_DEBUG'] = True
app.config['SECRET_KEY'] = 'dev'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view= 'tlogin'


class Studentinf(db.Model):
    __tablename = 'studentinf'
    sid = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    phone = db.Column(db.String(20))


class Teacherinf(db.Model):
    __tablename = 'teacherinf'
    tid = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(20))
    title = db.Column(db.String(20))
    introduce = db.Column(db.String(200))
    address = db.Column(db.String(50))
    email = db.Column(db.String(50))


class Student(db.Model, UserMixin):
    __tablename__ = 'student'
    id = db.Column(db.Integer, primary_key=True)
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'))
    spassword = db.Column(db.String(128))

    def set_password(self, spassword):
        self.spassword = generate_password_hash(spassword)

    def validate_password(self, spassword):
        return check_password_hash(self.spassword, spassword)


class Teacher(db.Model, UserMixin):
    __tablename__ = 'teacher'
    id = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'))
    tpassword = db.Column(db.String(128))

    def set_password(self, tpassword):
        self.tpassword = generate_password_hash(tpassword)

    def validate_password(self, tpassword):
        return check_password_hash(self.tpassword, tpassword)


class Schoice(db.Model):
    __tablename__ = 'schoice'
    id = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    firstchoice = db.Column(db.String(10)) #####
    secondchoice = db.Column(db.String(10))


class Tchoice(db.Model):
    __tablename = 'tchoice'
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'), primary_key=True)
    isfirst = db.Column(db.Integer)


class Final(db.Model):
    __tablename = 'final'
    sid = db.Column(db.String(10), db.ForeignKey('studentinf.sid'), primary_key=True)
    tid = db.Column(db.String(10), db.ForeignKey('teacherinf.tid'), primary_key=True)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    """Initialize the database."""
    if drop:  # 判断是否输入了选项
        db.drop_all()
    db.create_all()
    click.echo('Initialized database.')


@app.cli.command()
@click.option('--tid', prompt=True, help='The id used to login.')
@click.option('--password', prompt=True, hide_input=False, confirmation_prompt=True, help='The password used to login.')
def admin(tid, password):
    """Create user."""
    db.create_all()
    teacher = Teacher.query.filter_by(tid=tid).first()
    if teacher is not None:
        click.echo('Updating user...')
        teacher.set_password(password)
    else:
        click.echo('Creating user..')
        teacher = Teacher(tid=tid, tpassword='0')
        teacher.set_password(password)
        db.session.add(teacher)
    db.session.commit()
    click.echo('Done.')


@login_manager.user_loader
def load_user(teacher_tid):
    teacher = Teacher.query.get(int(teacher_tid))
    return teacher


@app.context_processor
def inject_user():
    if not current_user.is_authenticated:
        teacher = []
    else:
        teacher = Teacher.query.filter_by(tid=current_user.tid).first()# 要改
    return dict(teacher=teacher)


@app.route('/')
def index():
    if not current_user.is_authenticated:
        stu = []
        stu1 = []
    else:
        stu = Schoice.query.filter_by(firstchoice=current_user.tid).all()#改
        stu1 = Schoice.query.filter_by(secondchoice=current_user.tid).all()  # 改
    return render_template('index.html', students=stu, students1=stu1)


@app.route('/tlogin', methods=['GET', 'POST'])
def tlogin():
    if request.method == 'POST':
        tid = request.form['tid']
        tpassword = request.form['password']
        if not tid or not tpassword:
            flash('Invalid input')
            return redirect(url_for('tlogin'))

        teacher = Teacher.query.filter_by(tid=tid).first()
        if tid == teacher.tid and teacher.validate_password(tpassword):
            login_user(teacher)
            flash('Login success.')
            return redirect(url_for('index'))
        flash('Invalid username or password.')
        return redirect(url_for('tlogin'))
    return render_template('tlogin.html')


@app.route('/s/inf/<sid>')
@login_required
def sidinf(sid):
    student = Studentinf.query.filter_by(sid=sid).first()
    return render_template('sinf.html', student=student)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye.')
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    stu = []
    return render_template('404.html'), 404


@app.route('/thome')
@login_required
def thome():
    stu = Final.query.filter_by(tid=current_user.tid).all()
    teacher_inf = Teacherinf.query.filter_by(tid=current_user.tid).first()
    return render_template('thome.html', students=stu, teacher=teacher_inf)


@app.route('/tchoice', methods=['GET', 'POST'])
@login_required
def tchoice():
    if request.method == 'POST':
        name = request.form.get('name')
        sid = request.form.get('sid')
        if not name or not sid:
            flash('Invalid input.')
            return redirect(url_for('index'))
        studentinf = Studentinf.query.filter_by(sid=sid).first()
        if studentinf.name != name:
            flash('信息有误，请重新输入')
        else:
            studentchoice = Schoice.query.filter_by(id=sid).first()
            if studentchoice is None:
                flash('学生未选你！')
            elif studentchoice.firstchoice == current_user.tid:
                f = Final.query.filter_by(sid=sid).first()
                if f is not None:
                    f.tid = current_user.tid
                else:
                    f = Final(sid=sid, tid=current_user.tid)
                    db.session.add(f)
                tchoice = Tchoice.query.filter_by(sid=sid).first()
                if tchoice is not None:
                    tchoice.tid = current_user.tid
                    tchoice.sid = sid
                    tchoice.isfirst = 1
                else:
                    tchoice = Tchoice(sid=sid, tid=current_user.tid, isfirst=1)
                    db.session.add(tchoice)
                db.session.commit()
            elif studentchoice.secondchoice == current_user.tid:
                tchoice = Tchoice.query.filter_by(sid=sid).first()
                if tchoice is not None:
                    tchoice.tid = current_user.tid
                    tchoice.sid = sid
                    tchoice.isfirst = 0
                else:
                    tchoice = Tchoice(sid=sid, tid=current_user.tid, isfirst=0)
                    db.session.add(tchoice)
                tchoice.tid = current_user.tid
                tchoice.isfirst = 0
                db.session.commit()
        return redirect(url_for('tchoice'))# 是否要去掉
    stu = Student.query.filter_by(tid=current_user.tid).first()
    tea = Teacher.query.all()
    return render_template('tchoice.html', teachers=tea)
