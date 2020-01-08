import database
from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from functools import wraps

DEBUG = True
ADMIN_NAME = 'a1'
DFT_PWD = 'pwdpwd'

class User(UserMixin):
    cast = {'S': 'Student', 'T': 'Teacher', 'J': 'Jiaowu', 'A':'Administrator'}
    def __init__(self, status, no):
        if status in self.cast:
            status = self.cast[status]
        assert status in ['Student', 'Teacher', 'Jiaowu', 'Administrator']
        assert isinstance(no, str)
        self.status = status
        self.no = no
        self.id = status[:1] + no
    def has_stu_auth(self, sno):
        return database.query('Student', sno=sno) and (self.status in ['Jiaowu', 'Administrator'] \
            or (self.status == 'Student' and self.no == sno))
    def has_tec_auth(self, tno):
        return database.query('Teacher', tno=tno) and (self.status in ['Jiaowu', 'Administrator'] \
            or (self.status == 'Teacher' and self.no == tno))
    def has_crs_auth(self, tno, cno):
        return self.has_tec_auth(tno) and database.tec_authority(tno, to_int(cno))
    def has_lower_jw_auth(self):
        return self.status in ['Jiaowu', 'Administrator']
    def has_jw_auth(self, jno):
        return database.query('Jiaowu', jno=jno) and (self.status == 'Administrator' \
            or (self.status == 'Jiaowu' and self.no == jno))
    def has_ad_auth(self):
        return self.status == 'Administrator'
    def validate_pwd(self, pwd):
        return database.validate(self.status, self.no, pwd)

def auth(status):
    def auth_decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                assert current_user.is_authenticated
                if status == 'Student':
                    assert current_user.has_lower_jw_auth() or current_user.has_stu_auth(kwargs['sno'])
                elif status == 'Teacher':
                    assert current_user.has_lower_jw_auth() or current_user.has_tec_auth(kwargs['tno'])
                elif status == 'LowerJiaowu':
                    assert current_user.has_lower_jw_auth()
                elif status == 'Jiaowu':
                    assert current_user.has_ad_auth() or current_user.has_jw_auth(kwargs['jno'])
                elif status == 'Administrator':
                    assert current_user.has_ad_auth()
                elif status == 'Course':
                    assert current_user.has_lower_jw_auth() or current_user.has_crs_auth(kwargs['tno'], kwargs['cno'])
                else:
                    assert False
                return func(*args, **kwargs)
            except:
                flash('权限不足')
                return redirect(url_for('index'))
        return wrapped_func
    return auth_decorator

def root(name):
    def root_decorator(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
                flash(info)
                return redirect(url_for(name))
        return wrapped_func
    return root_decorator

def to_int(x):
    return int(x) if x else None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

login_manager = LoginManager(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User(user_id[:1], user_id[1:])
    except:
        return None
    
login_manager.login_view = 'login'
login_manager.login_message = '您未登录'

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', code=404)

@app.errorhandler(500)
def page_not_found(e):
    return render_template('error.html', code=500)

def error():
    return render_template('error.html', code='Unknown')

@app.route('/', methods=['GET'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    elif current_user.status == 'Student':
        return redirect(url_for('stu_index', sno=current_user.no))
    elif current_user.status == 'Teacher':
        return redirect(url_for('tec_index', tno=current_user.no))
    elif current_user.status == 'Jiaowu':
        return redirect(url_for('jw_index', jno=current_user.no))
    elif current_user.status == 'Administrator':
        return redirect(url_for('ad_index'))
    else:
        raise Exception('非法用户状态')

@app.route('/login', methods=['GET', 'POST'])
@root('error')
def login():
    if request.method == 'GET':
        if current_user.is_authenticated:
            flash('您已经登录')
            return redirect(url_for('index'))
        return render_template('login.html')
    try:
        user = User(request.form.get('status'), request.form.get('no'))
        assert user.validate_pwd(request.form.get('pwd'))
        login_user(user)
        flash('登录成功')
        return redirect(url_for('index'))
    except:
        flash('登录失败')
        return redirect(url_for('login'))

@app.route('/logout', methods=['GET'])
@login_required
@root('error')
def logout():
    logout_user()
    flash('您已登出')
    return redirect(url_for('login'))


@app.route('/student/<sno>', methods=['GET'])
@auth('Student')
@root('error')
def stu_index(sno):
    return render_template('stu_index.html', sno=sno)

@app.route('/student/<sno>/info', methods=['GET', 'POST'])
@auth('Student')
@root('stu_index')
def stu_info(sno):
    if request.method == 'GET':
        return render_template('stu_info.html', sno=sno, sinfo=database.query('Student', sno=sno)[0])
    try:
        attrib = {x: request.form.get(x) for x in ['stel']}
        attrib['sno'] = sno
        database.modify_cell('Student', **attrib)
        flash('修改信息成功')
        return redirect(url_for('stu_index', sno=sno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改信息失败，' + info)
        return redirect(url_for('stu_info', sno=sno))

@app.route('/student/<sno>/pwd', methods=['GET', 'POST'])
@auth('Student')
@root('error')
def stu_pwd(sno):
    if request.method == 'GET':
        return render_template('stu_pwd.html', sno=sno)
    try:
        database.change_pwd('Student', sno, request.form.get('old'), request.form.get('new'))
        flash('修改密码成功')
        return redirect(url_for('stu_index', sno=sno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改密码失败，' + info)
        return redirect(url_for('stu_pwd', sno=sno))

@app.route('/student/<sno>/course', methods=['GET', 'POST'])
@auth('Student')
@root('error')
def stu_course(sno):
    if request.method == 'GET':
        return render_template('stu_course.html', sno=sno, cinfo=database.stu_query_course(sno))
    try:
        op = request.form.get('op')
    except Exception:
        flash('非法课程操作')
        return redirect(url_for('stu_course', sno=sno))
    if op == 'picked':
        try:
            cinfo = [x for x in database.stu_query_course(sno) if x['pick']]
            flash('筛选成功')
            return render_template('stu_course.html', sno=sno, cinfo=cinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('筛选失败，' + info)
            return redirect(url_for('stu_course', sno=sno))
    elif op == 'unpicked':
        try:
            cinfo = [x for x in database.stu_query_course(sno) if not x['pick']]
            flash('筛选成功')
            return render_template('stu_course.html', sno=sno, cinfo=cinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('筛选失败，' + info)
            return redirect(url_for('stu_course', sno=sno))
    elif op == 'cno':
        try:
            cinfo = database.stu_query_course(sno, cno=to_int(request.form.get('cno')))
            flash('检索成功')
            return render_template('stu_course.html', sno=sno, cinfo=cinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('检索失败，' + info)
            return redirect(url_for('stu_course', sno=sno))
    elif op == 'cname':
        try:
            cinfo = database.stu_query_course(sno, cname=request.form.get('cname'))
            flash('检索成功')
            return render_template('stu_course.html', sno=sno, cinfo=cinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('检索失败，' + info)
            return redirect(url_for('stu_course', sno=sno))
    elif op == 'pick':
        try:
            database.stu_pick_course(sno=sno, cno=to_int(request.form.get('cno')))
            flash('选课成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('选课失败，' + info)
        return redirect(url_for('stu_course', sno=sno))
    elif op == 'exit':
        try:
            database.delete_cell('SC', sno=sno, cno=to_int(request.form.get('cno')))
            flash('退课成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('退课失败，' + info)
        return redirect(url_for('stu_course', sno=sno))
    elif op == 'apply':
        try:
            database.new_cell('CTA', sno=sno, cno=to_int(request.form.get('cno')), agree='N')
            flash('申请成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('申请失败，' + info)
        return redirect(url_for('stu_course', sno=sno))
    elif op == 'cancel':
        try:
            database.delete_cell('CTA', sno=sno, cno=to_int(request.form.get('cno')))
            flash('取消申请成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('取消申请失败，' + info)
        return redirect(url_for('stu_course', sno=sno))
    else:
        flash('非法课程操作')
        return redirect(url_for('stu_course', sno=sno))

@app.route('/student/<sno>/book', methods=['GET', 'POST'])
@auth('Student')
@root('error')
def stu_book(sno):
    if request.method == 'GET':
        all_book, bought = database.stu_query_book(sno)
        return render_template('stu_book.html', sno=sno, all_book=all_book, bought=bought)
    try:
        database.stu_buy_book(sno, request.form.get('bno'))
        flash('购书成功')
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('购书失败，' + info)
    return redirect(url_for('stu_book', sno=sno))

@app.route('/student/<sno>/timetable', methods=['GET'])
@auth('Student')
@root('error')
def stu_timetable(sno):
    table = [[[] for j in range(14)] for i in range(7)]
    for cname, rname, (x, y) in database.query_timetable(sno=sno):
        table[x-1][y-1].append((cname, rname))
    return render_template('stu_timetable.html', sno=sno, table=table)


@app.route('/teacher/<tno>', methods=['GET'])
@auth('Teacher')
@root('error')
def tec_index(tno):
    return render_template('tec_index.html', tno=tno)

@app.route('/teacher/<tno>/info', methods=['GET', 'POST'])
@auth('Teacher')
@root('error')
def tec_info(tno):
    if request.method == 'GET':
        return render_template('tec_info.html', tno=tno, tinfo=database.query('Teacher', tno=tno)[0])
    try:
        attrib = {x: request.form.get(x) for x in ['tdept', 'ttel', 'tmail']}
        attrib['tno'] = tno
        database.modify_cell('Teacher', **attrib)
        flash('修改信息成功')
        return redirect(url_for('tec_index', tno=tno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改信息失败，' + info)
        return redirect(url_for('tec_info', tno=tno))

@app.route('/teacher/<tno>/pwd', methods=['GET', 'POST'])
@auth('Teacher')
@root('error')
def tec_pwd(tno):
    if request.method == 'GET':
        return render_template('tec_pwd.html', tno=tno)
    try:
        database.change_pwd('Teacher', tno, request.form.get('old'), request.form.get('new'))
        flash('修改密码成功')
        return redirect(url_for('tec_index', tno=tno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改密码失败，' + info)
        return redirect(url_for('tec_pwd', tno=tno))

@app.route('/teacher/<tno>/course', methods=['GET', 'POST'])
@auth('Teacher')
@root('error')
def tec_course(tno):
    if request.method == 'GET':
        return render_template('tec_course.html', tno=tno, cinfo=database.tec_query_course(tno))
    try:
        op = request.form.get('op')
    except Exception:
        flash('非法课程操作')
        return redirect(url_for('tec_course', tno=tno))
    if op == 'new':
        try:
            attrib = {x: request.form.get(x) for x in ['cname', 'cdept', 'ccap', 'ccredit', 'cdate']}
            for x in ['ccap', 'ccredit']:
                attrib[x] = to_int(attrib[x])
            database.new_cell('Course', **attrib)
            flash('开课成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('开课失败，' + info)
        return redirect(url_for('tec_course', tno=tno))
    elif op == 'delete':
        try:
            database.delete_cell('Course', cno=to_int(request.form.get('cno')))
            flash('消课成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('消课失败，' + info)
        return redirect(url_for('tec_course', tno=tno))
    else:
        flash('非法课程操作')
        return redirect(url_for('tec_course', tno=tno))

@app.route('/teacher/<tno>/course/<cno>/info', methods=['GET', 'POST'])
@auth('Course')
@root('error')
def tec_course_info(tno, cno):
    cno=to_int(cno)
    print(cno)
    print(database.query('CB', cno=cno))
    if request.method == 'GET':
        cinfo = None
        for x in database.tec_query_course(tno):
            if x['cno'] == cno:
                cinfo = x
        return render_template('tec_course_info.html', tno=tno, cno=cno, cinfo=cinfo, binfo=database.query('CB', cno=cno), tainfo=database.query_course_ta(cno))
    try:
        op = request.form.get('op')
    except Exception:
        flash('非法课程操作')
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    if op == 'update':
        try:
            attrib = {x: request.form.get(x) for x in ['ccap', 'ccredit', 'cdate']}
            attrib['cno'] = cno
            for x in ['ccap', 'ccredit']:
                attrib[x] = to_int(attrib[x])
            database.modify_cell('Course', **attrib)
            flash('修改信息成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('修改信息失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    elif op == 'newco':
        try:
            database.new_cell('TC', tno=request.form.get('tno'), cno=cno)
            flash('添加合作教师成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('添加合作教师失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    elif op == 'newbook':
        try:
            database.new_course_book(cno, request.form.get('bno'), request.form.get('bname'))
            flash('添加参考书成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('添加参考书失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    elif op == 'agree':
        try:
            database.modify_cell('CTA', cno=cno, sno=request.form.get('sno'), agree='Y')
            flash('添加助教成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('添加助教失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    elif op == 'deny':
        try:
            database.delete_cell('CTA', cno=cno, sno=request.form.get('sno'))
            flash('拒绝助教成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('拒绝助教失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    elif op == 'deletebook':
        try:
            database.delete_course_book(cno, request.form.get('bno'))
            flash('删除参考书成功')
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('删除参考书失败，' + info)
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))
    else:
        flash('非法课程操作')
        return redirect(url_for('tec_course_info', tno=tno, cno=cno))

@app.route('/teacher/<tno>/course/<cno>/student', methods=['GET', 'POST'])
@auth('Course')
@root('error')
def tec_course_stu(tno, cno):
    cno=to_int(cno)
    if request.method == 'GET':
        return render_template('tec_course_stu.html', tno=tno, cno=cno, sinfo=database.query_course_student(cno))
    try:
        op = request.form.get('op')
    except Exception:
        flash('非法课程操作')
        return redirect(url_for('tec_course_stu', tno=tno, cno=cno))
    if op == 'sno':
        try:
            sinfo = database.query_course_student(cno, sno=request.form.get('sno'))
            flash('检索成功')
            return render_template('tec_course_stu.html', tno=tno, cno=cno, sinfo=sinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('检索失败，' + info)
            return redirect(url_for('tec_course_stu', tno=tno, cno=cno))
    elif op == 'sname':
        try:
            sinfo = database.query_course_student(cno, sname=request.form.get('sname'))
            flash('检索成功')
            return render_template('tec_course_stu.html', tno=tno, cno=cno, sinfo=sinfo)
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('检索失败，' + info)
            return redirect(url_for('tec_course_stu', tno=tno, cno=cno))
    elif op == 'grade':
        try:
            database.modify_cell('SC', sno=request.form.get('sno'), cno=cno, grade=to_int(request.form.get('grade')))
            flash('打分成功')
            return redirect(url_for('tec_course_stu', tno=tno, cno=cno))
        except Exception as e:
            info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
            flash('打分失败，' + info)
            return redirect(url_for('tec_course_stu', tno=tno, cno=cno))
    else:
        flash('非法课程操作')
        return redirect(url_for('tec_course_stu', tno=tno, cno=cno))

@app.route('/teacher/<tno>/timetable', methods=['GET'])
@auth('Teacher')
@root('error')
def tec_timetable(tno):
    table = [[[] for j in range(14)] for i in range(7)]
    for cname, rname, time in database.query_timetable(tno=tno):
        x, y = int(time[0]), int(time[2:])
        table[x-1][y-1].append((cname, rname))
    return render_template('tec_timetable.html', tno=tno, table=table)

@app.route('/jiaowu/<jno>', methods=['GET'])
@auth('Jiaowu')
@root('error')
def jw_index(jno):
    return render_template('jw_index.html', jno=jno)

@app.route('/jiaowu/<jno>/info', methods=['GET', 'POST'])
@auth('Jiaowu')
@root('error')
def jw_info(jno):
    if request.method == 'GET':
        return render_template('jw_info.html', jno=jno, jinfo=database.query('Jiaowu', jno=jno)[0])
    try:
        attrib = {x: request.form.get(x) for x in ['jtel', 'jmail']}
        attrib['jno'] = jno
        database.modify_cell('Jiaowu', **attrib)
        flash('修改信息成功')
        return redirect(url_for('jw_index', jno=jno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改信息失败，' + info)
        return redirect(url_for('jw_info', jno=jno))

@app.route('/jiaowu/<jno>/pwd', methods=['GET', 'POST'])
@auth('Jiaowu')
@root('error')
def jw_pwd(jno):
    if request.method == 'GET':
        return render_template('jw_pwd.html', jno=jno)
    try:
        database.change_pwd('Jiaowu', jno, request.form.get('old'), request.form.get('new'))
        flash('修改密码成功')
        return redirect(url_for('jw_index', jno=jno))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改密码失败，' + info)
        return redirect(url_for('jw_pwd', jno=jno))

@app.route('/admin', methods=['GET'])
@auth('Administrator')
@root('error')
def ad_index():
    return render_template('ad_index.html')

@app.route('/admin/info', methods=['GET', 'POST'])
@auth('Administrator')
@root('error')
def ad_info():
    if request.method == 'GET':
        return render_template('ad_info.html', ainfo=database.query('Administrator')[0])
    try:
        attrib = {x: request.form.get(x) for x in ['atel', 'amail']}
        attrib['ano'] = ADMIN_NAME
        print(attrib)
        database.modify_cell('Administrator', **attrib)
        flash('修改信息成功')
        return redirect(url_for('ad_index'))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改信息失败，' + info)
        return redirect(url_for('ad_info'))

@app.route('/admin/pwd', methods=['GET', 'POST'])
@auth('Administrator')
@root('error')
def ad_pwd():
    if request.method == 'GET':
        return render_template('ad_pwd.html')
    try:
        assert current_user.validate_pwd(request.form.get('old'))
        database.modify_cell('Administrator', ano=ADMIN_NAME, apwd=request.form.get('new'))
        flash('修改密码成功')
        return redirect(url_for('ad_index'))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('修改密码失败，' + info)
        return redirect(url_for('ad_pwd'))

@app.route('/admin/student', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_stu():
    if request.method == 'GET':
        return render_template('ad_stu.html', sinfo=database.query('Student'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['sno', 'sid', 'sname', 'ssex', 'sdept', 'stel']}
        attrib['spwd'] = DFT_PWD
        database.new_cell('Student', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_stu'))
    elif op == 'delete':
        database.delete_cell('Student', sno=request.form.get('sno'))
        flash('删除成功')
        return redirect(url_for('ad_stu'))
    elif op == 'sno':
        sinfo = database.query('Student', sno=request.form.get('sno'))
        flash('检索成功')
        return render_template('ad_stu.html', sinfo=sinfo)
    elif op == 'sname':
        sinfo = database.query('Student', sname=request.form.get('sname'))
        flash('检索成功')
        return render_template('ad_stu.html', sinfo=sinfo)
    elif op == 'pwd':
        database.modify_cell('Student', sno=request.form.get('sno'), spwd=DFT_PWD)
        flash('修改成功')
        return redirect(url_for('ad_stu'))
    else:
        raise Exception('非法操作')
    

@app.route('/admin/teacher', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_tec():
    if request.method == 'GET':
        return render_template('ad_tec.html', tinfo=database.query('Teacher'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['tno', 'tid', 'tname', 'tsex', 'tdept', 'ttel', 'tmail']}
        attrib['tpwd'] = DFT_PWD
        database.new_cell('Teacher', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_tec'))
    elif op == 'delete':
        database.delete_cell('Teacher', tno=request.form.get('tno'))
        flash('删除成功')
        return redirect(url_for('ad_tec'))
    elif op == 'tno':
        tinfo = database.query('Teacher', tno=request.form.get('tno'))
        flash('检索成功')
        return render_template('ad_tec.html', tinfo=tinfo)
    elif op == 'tname':
        tinfo = database.query('Teacher', tname=request.form.get('tname'))
        flash('检索成功')
        return render_template('ad_tec.html', tinfo=tinfo)
    elif op == 'pwd':
        database.modify_cell('Teacher', tno=request.form.get('tno'), tpwd=request.form.get('pwd'))
        flash('修改成功')
        return redirect(url_for('ad_tec'))
    else:
        raise Exception('非法操作')

@app.route('/admin/jiaowu', methods=['GET', 'POST'])
@auth('Administrator')
@root('error')
def ad_jw():
    if request.method == 'GET':
        return render_template('ad_jw.html', tinfo=database.query('Teacher'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['jno', 'jid', 'jname', 'jtel', 'jmail']}
        attrib['jpwd'] = DFT_PWD
        database.new_cell('Jiaowu', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_jw'))
    elif op == 'delete':
        database.delete_cell('Jiaowu', jno=request.form.get('jno'))
        flash('删除成功')
        return redirect(url_for('ad_jw'))
    elif op == 'jno':
        jinfo = database.query('Jiaowu', jno=request.form.get('jno'))
        flash('检索成功')
        return render_template('ad_jw.html', jinfo=jinfo)
    elif op == 'jname':
        jinfo = database.query('Jiaowu', jname=request.form.get('jname'))
        flash('检索成功')
        return render_template('ad_jw.html', jinfo=jinfo)
    elif op == 'pwd':
        database.modify_cell('Jiaowu', jno=request.form.get('jno'), jpwd=request.form.get('pwd'))
        flash('修改成功')
        return redirect(url_for('ad_jw'))
    else:
        raise Exception('非法操作')

@app.route('/admin/department', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_dept():
    if request.method == 'GET':
        return render_template('ad_dept.html', dinfo=database.query('Department'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['dno', 'dname', 'dhead']}
        database.new_cell('Department', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_dept'))
    elif op == 'delete':
        database.delete_cell('Department', dno=request.form.get('dno'))
        flash('删除成功')
        return redirect(url_for('ad_dept'))
    else:
        raise Exception('非法操作')

@app.route('/admin/book', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_book():
    if request.method == 'GET':
        return render_template('ad_book.html', binfo=database.query('Book'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['bno', 'bname']}
        attrib['bstore'] = 0
        database.new_cell('Book', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_book'))
    elif op == 'delete':
        database.delete_cell('Book', bno=request.form.get('bno'))
        flash('删除成功')
        return redirect(url_for('ad_book'))
    elif op == 'update':
        database.modify_cell('Book', bno=request.form.get('bno'), bstore=to_int(request.form.get('bstore')))
        flash('修改库存成功')
        return redirect(url_for('ad_book'))
    else:
        raise Exception('非法操作')

@app.route('/admin/room', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_room():
    if request.method == 'GET':
        return render_template('ad_room.html', rinfo=database.query('Room'))
    op = request.form.get('op')
    if op == 'new':
        attrib = {x: request.form.get(x) for x in ['rname', 'rcap']}
        attrib['rcap'] = to_int(attrib['rcap'])
        database.new_cell('Room', **attrib)
        flash('添加成功')
        return redirect(url_for('ad_room'))
    elif op == 'delete':
        database.delete_cell('Room', rname=request.form.get('rname'))
        flash('删除成功')
        return redirect(url_for('ad_room'))
    else:
        raise Exception('非法操作')

@app.route('/admin/course', methods=['GET', 'POST'])
@auth('LowerJiaowu')
@root('error')
def ad_crs():
    if request.method == 'GET':
        return render_template('ad_crs.html', cinfo=database.query('Course'))
    op = request.form.get('op')
    if op == 'delete':
        database.delete_cell('Course', cno=to_int(request.form.get('cno')))
        flash('删除成功')
        return redirect(url_for('ad_crs'))
    elif op == 'cno':
        cinfo = database.query('Course', cno=to_int(request.form.get('cno')))
        flash('检索成功')
        return render_template('ad_crs.html', cinfo=cinfo)
    elif op == 'jname':
        cinfo = database.query('Course', cname=request.form.get('cname'))
        flash('检索成功')
        return render_template('ad_crs.html', cinfo=cinfo)
    else:
        raise Exception('非法操作')

@app.route('/admin/arrange/<cno>/time', methods=['GET'])
@auth('LowerJiaowu')
@root('error')
def ad_crs_time(cno):
    cno = to_int(cno)
    table = [[False] * 14 for i in range(7)]
    for x, y in database.course_busy_time(cno):
        table[x-1][y-1] = True
    return render_template('ad_crs_time.html', cno=cno, table=table)

@app.route('/admin/arrange/<cno>/room/<x>_<y>', methods=['GET'])
@auth('LowerJiaowu')
@root('error')
def ad_crs_room(cno, x, y):
    cno = to_int(cno)
    x, y = int(x), int(y)
    rinfo = database.time_free_room(cno, x, y)
    print(rinfo)
    return render_template('ad_crs_room.html', cno=cno, x=x, y=y, rinfo=rinfo)

@app.route('/admin/arrange/<cno>/room/<x>_<y>/<room>', methods=['POST'])
@auth('LowerJiaowu')
@root('error')
def ad_arrange(cno, x, y, room):
    cno = to_int(cno)
    x, y = int(x), int(y)
    try:
        database.arrange_course(cno, x, y, room)
        flash('排课成功')
        return redirect(url_for('ad_crs'))
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('排课失败，' + info)
        return redirect(url_for('ad_crs'))

@app.route('/admin/everything', methods=['GET', 'POST'])
@auth('Administrator')
@root('error')
def ad_everything():
    if request.method == 'GET':
        return render_template('ad_everything.html', info=[])
    op = request.form.get('op')
    table = request.form.get('table')
    assert table in ['Student', 'Teacher', 'Jiaowu', 'Course', 'Book', 'Room', 'Department',
        'CPS', 'CB',  'CR', 'SC', 'TC', 'CTA']
    attrib = request.form.get('attrib')
    attrib.replace(' ', '')
    attrib = attrib.split(',')
    dic = {}
    for x in attrib:
        if x:
            x = x.split('=')
            n, v = x[0], x[1]
            if n in ['ccap', 'ccredit', 'bstore', 'rcap', 'grade']:
                v = to_int(v)
            dic[n] = v
    try:
        if op == 'new':
            database.new_cell(table, **dic)
            flash('插入成功')
            return redirect(url_for('ad_everything'))
        elif op == 'delete':
            database.delete_cell(table, **dic)
            flash('删除成功')
            return redirect(url_for('ad_everything'))
        elif op == 'modify':
            database.modify_cell(table, **dic)
            flash('修改成功')
            return redirect(url_for('ad_everything'))
        elif op == 'query':
            info = database.query(table, **dic)
            flash('查询成功')
            return render_template('ad_everything.html', info=info)
        else:
            raise Exception('非法操作')
    except Exception as e:
        info = str(e) if len(str(e)) < 8 or DEBUG else '未知错误'
        flash('操作失败，' + info)
        return redirect(url_for('ad_everything'))

if __name__ == "__main__":
    acc = input('mysql account:')
    pwd = input('mysql password:') 
    create = input('create table?(y/n)')
    while create not in ['y', 'Y', 'n', 'N']:
        create = input('create table?(y/n):')
    create = True if create in ['y', 'Y'] else False
    rebuild = input('rebuild data?(y/n)')
    while rebuild not in ['y', 'Y', 'n', 'N']:
        rebuild = input('rebuild data?(y/n):')
    rebuild = True if rebuild in ['y', 'Y'] else False
    print('init database')
    database.init_db(ano=acc, apwd=pwd, create=create)
    if rebuild:
        database.load_data('./sql/load_data.sql')
        print('load finished, jiaowu admin account is "a1", and default password is "pwdpwd"')
    app.run(host='0.0.0.0',port=80)