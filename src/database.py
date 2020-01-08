import re

import pymysql

con, cur = None, None
check_constraint = {}
table_name = {'sno': 'Student', 'tno': 'Teacher', 'dno': 'Department', 'rname': 'Room', 'bno': 'Book', 'cno': 'Course'}
primary_key = {'Student': ['sno'], 'Jiaowu': ['jno'],
               'Teacher': ['tno'], 'Administrator': ['ano'],
               'Course': ['cno'], 'Book': ['bno'],
               'Room': ['rname'], 'Department': ['dno'],
               'CPS': ['pcno', 'scno'], 'CB': ['cno', 'bno'],
               'CR': ['cno', 'rname', 'ctime'], 'SC': ['sno', 'cno'],
               'TC': ['tno', 'cno'], 'CTA': ['sno', 'cno'], 'SB': ['id']}

'''
1.接口描述中的“列表”和“元组”可以相互替换，以实现方便为准。
2.某些函数在插删改时要对其他表做修改，可以在函数中按描述手动实现过程，也可以在数据库建立阶段写好触发器实现。
3.如果不用触发器和存储过程，也需要找一两个过程写一下，因为实现报告有这一栏，要水报告的23333……
4.如果使用数据库框架，最好用sql-alchemy；不想用框架继续odbc应该也可以。
5.描述中的“不存在”指主码非法或表中没有该主码。
6.有写的不清楚的地方我尽快解释或修改，辛苦你啦！
'''


def readSql(filename):
    try:
        with open(filename, encoding='utf-8', mode='r') as f:
            # [:-1]删除最后一个元素，也就是空字符串
            str_list = f.read().split(';')[:-1]
            sql_list = []
            for x in str_list:
                if '\n' in x:
                    x = x.replace('\n', ' ')
                if '    ' in x:
                    x = x.replace('    ', '')
                sql_list.append(x + ';')
            return sql_list
    except:
        raise Exception('文件找不到！')


def execute(sql_list):
    try:
        for stmt in sql_list:
            cur.execute(stmt)
        con.commit()
    except:
        return False
    return True


def fetch(sql_stmt):
    try:
        cur.execute(sql_stmt)
        con.commit()
        result = cur.fetchall()
        return list(result)
    except:
        return []


# 删除库内数据，新建一个空的test库
def create_table():
    execute(readSql('./sql/create_table.sql'))


# 身份证号的简单判断

def is_lawful_identity_id(sid):
    if type(sid) != str or not str.isdigit(sid) or len(sid) != 18:
        return False
    return True


def is_lawful_pwd(pwd):
    if str.isalnum(pwd) and len(pwd) >= 6 and len(pwd) <= 18:
        return True
    return False


def is_lawful_bno(bno):
    if type(bno) == str and re.match(r'^([0-9])\-([0-9]{3})\-([0-9]{5})\-([0-9])$', bno):
        return True
    return False


def is_lawful_cno(cno):
    if type(cno) != int or cno <= 0:
        return False
    return True


def is_lawful_email(email):
    if type(email) != str:
        return False
    elif re.match(r'^[0-9a-zA-Z_]*@((qq\.com)|(buaa\.edu\.cn)|(163\.com))$', email):
        return True
    else:
        return False


def is_lawful_name(name):
    return type(name) == str and name != '' and len(name) <= 10


def is_lawful_sex(sex):
    return type(sex) == str and sex in ['男', '女']


def is_lawful_tel(tel):
    return type(tel) == str and len(tel) >= 6 and len(tel) <= 11


def is_lawful_no(number):
    return type(number) == str and str.isalnum(number) and len(number) <= 10


def is_lawful_ctime(ctime):
    if type(ctime) != str:
        return False
    elif re.match(r'^([1-7])-([1-9]|1[0-4])$', ctime):
        return True
    else:
        return False


# number 需要在int范围内
def is_lawful_pos_int(number):
    return type(number) == int and number >= 0


def is_lawful_year(year):
    return type(year) == str and str.isdigit(year) and int(year) > 0


def is_lawful_dno(dno):
    if type(dno) != str or not str.isalnum(dno) or len(dno) > 4:
        return False
    return True


def value_exist(**attrib):
    for key in attrib.keys():
        value = attrib[key]
        res_list = fetch('select {} from {}'.format(key, table_name[key]))
        for item in res_list:
            if value in item.values():
                return True
        return False


def check_student_constraint(attrib):
    if 'sno' in attrib.keys():
        if not is_lawful_no(attrib['sno']):
            return False
    if 'sid' in attrib.keys():
        if not is_lawful_identity_id(attrib['sid']):
            return False
    if 'spwd' in attrib.keys():
        if not is_lawful_pwd(attrib['spwd']):
            return False
    if 'sname' in attrib.keys():
        if not is_lawful_name(attrib['sname']):
            return False
    if 'ssex' in attrib.keys():
        if not is_lawful_sex(attrib['ssex']):
            return False
    if 'sdept' in attrib.keys():
        if not (is_lawful_dno(attrib['sdept']) or attrib['sdept'] == ''):
            return False
    if 'stel' in attrib.keys():
        if not (is_lawful_tel(attrib['stel']) or attrib['stel'] == ''):
            return False
    return True


def check_teacher_constraint(attrib):
    if 'tno' in attrib.keys():
        if not is_lawful_no(attrib['tno']):
            return False
    if 'tid' in attrib.keys():
        if not is_lawful_identity_id(attrib['tid']):
            return False
    if 'tpwd' in attrib.keys():
        if not is_lawful_pwd(attrib['tpwd']):
            return False
    if 'tname' in attrib.keys():
        if not is_lawful_name(attrib['tname']):
            return False
    if 'tsex' in attrib.keys():
        if not is_lawful_sex(attrib['tsex']):
            return False
    if 'tdept' in attrib.keys():
        if not (is_lawful_dno(attrib['tdept']) or attrib['tdept'] == ''):
            return False
    if 'ttel' in attrib.keys():
        if not (is_lawful_tel(attrib['ttel']) or attrib['ttel'] == ''):
            return False
    if 'tmail' in attrib.keys():
        if not (is_lawful_email(attrib['tmail']) or attrib['tmail'] == ''):
            return False
    return True


def check_jiaowu_constraint(attrib):
    if 'jno' in attrib.keys():
        if not is_lawful_no(attrib['jno']):
            return False
    if 'jid' in attrib.keys():
        if not is_lawful_identity_id(attrib['jid']):
            return False
    if 'jpwd' in attrib.keys():
        if not is_lawful_pwd(attrib['jpwd']):
            return False
    if 'jname' in attrib.keys():
        if not is_lawful_name(attrib['jname']):
            return False
    if 'jtel' in attrib.keys():
        if not (is_lawful_tel(attrib['jtel']) or attrib['jtel'] == ''):
            return False
    if 'jmail' in attrib.keys():
        if not (is_lawful_email(attrib['jmail']) or attrib['jmail'] == ''):
            return False
    return True


def check_administrator_constraint(attrib):
    if 'ano' in attrib.keys():
        if not is_lawful_no(attrib['ano']):
            return False
    if 'apwd' in attrib.keys():
        if not is_lawful_pwd(attrib['apwd']):
            return False
    if 'atel' in attrib.keys():
        if not (is_lawful_tel(attrib['atel']) or attrib['atel'] == ''):
            return False
    if 'amail' in attrib.keys():
        if not (is_lawful_email(attrib['amail']) or attrib['amail'] == ''):
            return False
    return True


def check_course_constraint(attrib):
    # cno不在传入参数内
    if 'cname' in attrib.keys():
        if not is_lawful_name(attrib['cname']):
            return False
    if 'cdept' in attrib.keys():
        if not (is_lawful_dno(attrib['cdept']) or attrib['cdept'] == ''):
            return False
    if 'ccap' in attrib.keys():
        if not is_lawful_pos_int(attrib['ccap']):
            return False
    if 'ccredit' in attrib.keys():
        if not is_lawful_pos_int(attrib['ccredit']):
            return False
    if 'cdate' in attrib.keys():
        if not is_lawful_year(attrib['cdate']):
            return False
    return True


def check_book_constraint(attrib):
    if 'bno' in attrib.keys():
        if not is_lawful_bno(attrib['bno']):
            return False
    if 'bname' in attrib.keys():
        if not is_lawful_name(attrib['bname']):
            return False
    if 'bstore' in attrib.keys():
        if not is_lawful_pos_int(attrib['bstore']):
            return False
    return True


def check_room_constraint(attrib):
    if 'rname' in attrib.keys():
        if not is_lawful_name(attrib['rname']):
            return False
    if 'rcap' in attrib.keys():
        if not is_lawful_pos_int(attrib['rcap']):
            return False
    return True


def check_department_constraint(attrib):
    if 'dno' in attrib.keys():
        if not is_lawful_dno(attrib['dno']):
            return False
    if 'dname' in attrib.keys():
        if not is_lawful_name(attrib['dname']):
            return False
    if 'dhead' in attrib.keys():
        if not (is_lawful_no(attrib['dhead']) or attrib['dhead'] == ''):
            return False
    return True


def check_cps_constraint(attrib):
    if 'pcno' in attrib.keys():
        if not is_lawful_cno(attrib['pcno']):
            return False
    if 'scno' in attrib.keys():
        if not is_lawful_cno(attrib['scno']):
            return False
    return True


def check_cb_constraint(attrib):
    if 'cno' in attrib.keys():
        if not is_lawful_cno(attrib['cno']):
            return False
    if 'bno' in attrib.keys():
        if not is_lawful_bno(attrib['bno']):
            return False
    return True


def check_cr_constraint(attrib):
    if 'cno' in attrib.keys():
        if not is_lawful_cno(attrib['cno']):
            return False
    if 'rname' in attrib.keys():
        if not is_lawful_name(attrib['rname']):
            return False
    if 'ctime' in attrib.keys():
        if not is_lawful_ctime(attrib['ctime']):
            return False
    return True


def check_sc_constraint(attrib):
    if 'sno' in attrib.keys():
        if not is_lawful_no(attrib['sno']):
            return False
    if 'cno' in attrib.keys():
        if not is_lawful_cno(attrib['cno']):
            return False
    if 'grade' in attrib.keys():
        if not ((type(attrib['grade']) == int and attrib['grade'] <= 100 and attrib['grade'] >= 0) or attrib[
            'grade'] == None):
            return False
    return True


def check_tc_constraint(attrib):
    if 'tno' in attrib.keys():
        if not is_lawful_no(attrib['tno']):
            return False
    if 'cno' in attrib.keys():
        if not is_lawful_cno(attrib['cno']):
            return False
    return True


def check_cta_constraint(attrib):
    if 'sno' in attrib.keys():
        if not is_lawful_no(attrib['sno']):
            return False
    if 'cno' in attrib.keys():
        if not is_lawful_cno(attrib['cno']):
            return False
    if 'agree' in attrib.keys():
        if attrib['agree'] != 'Y' and attrib['agree'] != 'N':
            return False
    return True


def check_sb_constraint(attrib):
    if 'sno' in attrib.keys():
        if not is_lawful_no(attrib['sno']):
            return False
    if 'bno' in attrib.keys():
        if not is_lawful_bno(attrib['bno']):
            return False
    return True


def get_tname_of_course(cno):
    res_tname = fetch('select tname from Teacher where tno in (select tno from TC where cno={})'.format(cno))
    return [item['tname'] for item in res_tname]


def get_atname_of_course(cno):
    res_cta = fetch(
        'select sname from Student where sno in (select sno from CTA where agree=\'Y\' and cno={})'.format(
            cno))
    return [item['sname'] for item in res_cta]


def get_croom_of_course(cno):
    res_room = fetch('select rname,ctime from CR where cno={}'.format(cno))
    return [tuple([item['rname'], item['ctime']]) for item in res_room]


def get_grade_of_course(sno, cno):
    result = fetch('select grade from sc where sno={} and cno={}'.format('\'' + sno + '\'', cno))
    if len(result) == 0:
        return None
    else:
        return result[0]['grade']


# 判断是否是助教
def is_at_of_course(sno, cno):
    result = fetch('select sno from cta where sno={} and cno={}'.format('\'' + sno + '\'', cno))
    result2 = fetch('select sno from cta where sno={} and cno={} and agree=\'Y\''.format('\'' + sno + '\'', cno))
    if len(result) == 0:
        return ''
    elif len(result2) == 0:
        return 'N'
    else:
        return 'Y'


# 获取选课学生数
def get_course_student(cno):
    stu_cnt = fetch('select count(*) cnt from SC where cno={}'.format(cno))
    return stu_cnt[0]['cnt']


# 需提前判断cno合法性
def is_course_full(cno):
    ccap = fetch('select ccap from Course where cno={};'.format(cno))
    return get_course_student(cno) >= ccap[0]['ccap']


def already_select_course(sno, cno):
    sno = '\'' + sno + '\''
    res = fetch('select cno from SC where sno={} and cno={};'.format(sno, cno))
    if len(res) != 0:
        return True
    else:
        return False


def get_book_storage(bno):
    if not is_lawful_bno(bno) or not value_exist(bno=bno):
        return 0
    else:
        bno = '\'' + bno + '\''
        res = fetch('select bstore from Book where bno={};'.format(bno))
        return res[0]['bstore']


# 以上为help function


def new_cell(table, **attrib):
    '''
        表名称table in ['Student', 'Teacher', 'Jiaowu', 'Course', 'Book', 'Room', 'Department',
            'CPS', 'CB',  'CR', 'SC', 'TC', 'CTA','SB']
        字典传参attrib，key为接口表项中的属性名，value为对应值（全部为字符串形式，空字符串表示空值）。
        注：若table是'Student'、'Teacher'、'Jiaowu'，attrib中也包含密码。

        执行插入，如果：主码值可以插入；各属性值满足非空约束、外码约束、范围约束。
            注：插入操作可以使用数据库存储过程实现。
        插入失败则raise Exception('数据非法或重复')。
    '''
    assert table in ['Student', 'Teacher', 'Jiaowu', 'Course', 'Book', 'Room', 'Department',
                     'CPS', 'CB', 'CR', 'SC', 'TC', 'CTA', 'SB']
    if check_constraint[table](attrib):
        str_att, str_val = '', ''
        for key in attrib.keys():
            value = attrib[key]
            str_att = str_att + key + ','
            if value == '' or value == None:
                str_val = str_val + 'null,'
            elif type(value) == str:
                str_val = str_val + '\'' + value + '\','
            elif type(value) == int:
                str_val = str_val + str(value) + ','
        sql = 'insert into {}({})  values({})'.format(table, str_att[:-1], str_val[:-1])
        if not execute([sql]):
            raise Exception('数据非法或重复')
    else:
        raise Exception('数据非法或重复')


# 一定要在attrib中提供主码
def modify_cell(table, **attrib):
    '''
        传参同new_cell，table范围增加一个'Administrator'。某属性不在attrib中表示不修改，在attrib中但value为空串表示改为空值。
        如果提供的主码不存在于表中，或有属性值不满足非空约束、外码约束、范围约束，拒绝修改并raise Exception('非法属性值')；
        如果修改课程，且新的课容量小于已选该课程的已选学生人数，拒绝修改并raise Exception('课容量小于已选学生人数')；
        否则执行修改。失败则raise Exception('未知错误')。
    '''
    assert table in ['Student', 'Teacher', 'Administrator', 'Jiaowu', 'Course', 'Book', 'Room', 'Department',
                     'CPS', 'CB', 'CR', 'SC', 'TC', 'CTA', 'SB']
    if check_constraint[table](attrib):
        pkey = primary_key[table]
        if not (set(list(attrib.keys())) >= set(pkey)):  # 传入的键值不包含主码或者主码不全
            raise Exception('非法属性值')
        str_modify, str_select = '', ''
        for key in attrib.keys():
            value = attrib[key]
            if key not in pkey:
                if value == '' or value == None:
                    str_modify = str_modify + key + '=null,'
                elif type(value) == str:
                    str_modify = str_modify + key + '=\'' + value + '\','
                elif type(value) == int:
                    str_modify = str_modify + key + '=' + str(value) + ','
                else:
                    raise Exception('非法属性值')
            else:
                if value == '' or value == None:
                    raise Exception('非法属性值')
                elif type(value) == str:
                    str_select = str_select + key + '=\'' + value + '\' and '
                elif type(value) == int:
                    str_select = str_select + key + '=' + str(value) + ' and '
        sql = 'update {} set {} where {}'.format(table, str_modify[:-1], str_select[:-4])
        # print(sql)
        if table == 'Course' and 'ccap' in attrib.keys():
            if get_course_student(attrib['cno']) > attrib['ccap']:
                raise Exception('课容量小于已选学生人数')
        if not execute([sql]):
            raise Exception('非法属性值')
    else:
        raise Exception('非法属性值')


def delete_cell(table, **attrib):
    '''
        传参类似new_cell，attrib只包含主码值
        执行删除，如果：主码值存在于表中
            触发：执行删除过程前，如果被删除的主码被其他表引用做外码，需要保证所有引用的参照完整性：若外码可以为空则将其改为空（如Student中的sdept）；
            否则需要将整个元组删除（如SC中的sno和cno）。
            完整性维持可以使用数据库触发器实现。
        raise Exception('删除不存在的数据') otherwise
    '''
    assert table in ['Student', 'Teacher', 'Jiaowu', 'Course', 'Book', 'Room', 'Department',
                     'CPS', 'CB', 'CR', 'SC', 'TC', 'CTA', 'SB']
    pkey = primary_key[table]
    if not (set(list(attrib.keys())) >= set(pkey)):  # 传入的键值不包含主码或者主码不全
        raise Exception('非法属性值')
    str_select = ''
    for key in attrib.keys():
        value = attrib[key]
        if key in primary_key[table]:
            if value == None or value == '':
                raise Exception('非法属性值')
            elif type(value) == str:
                str_select = str_select + key + '=\'' + value + '\' and '
            elif type(value) == int:
                str_select = str_select + key + '=' + str(value) + ' and '
    sql = 'delete from {} where {}'.format(table, str_select[:-4])
    if not execute([sql]):
        raise Exception('删除不存在的数据')


def validate(status, id, pwd):
    '''
        status in ['Administrator', 'Student', 'Teacher', 'Jiaowu']，对应的id是ano,sno,tno,jno
        return True 如果：status表中id存在、id和密码相符
        return False otherwise
    '''
    if status == 'Administrator':
        str_id, str_pwd = 'ano', 'apwd'
    elif status == 'Student':
        str_id, str_pwd = 'sno', 'spwd'
    elif status == 'Teacher':
        str_id, str_pwd = 'tno', 'tpwd'
    elif status == 'Jiaowu':
        str_id, str_pwd = 'jno', 'jpwd'
    else:
        return False
    sql='select * from {} where {}={} and {}={}'.format(status, str_id, '\'' + id + '\'', str_pwd, '\'' + pwd + '\'')
    correct_pwd = fetch(sql)
    if len(correct_pwd) == 0:
        return False
    else:
        return True


def change_pwd(status, id, old_pwd, new_pwd):
    if status == 'Administrator':
        str_id, str_pwd = 'ano', 'apwd'
    elif status == 'Student':
        str_id, str_pwd = 'sno', 'spwd'
    elif status == 'Teacher':
        str_id, str_pwd = 'tno', 'tpwd'
    elif status == 'Jiaowu':
        str_id, str_pwd = 'jno', 'jpwd'
    else:
        raise Exception('未知错误')
    if not validate(status, id, old_pwd):
        raise Exception('账号不存在或密码错误')
    else:
        if is_lawful_pwd(new_pwd):
            sql = 'update {} set {}={} where {}={}'.format(status, str_pwd, '\'' + new_pwd + '\'', str_id,
                                                           '\'' + id + '\'')
            if not execute([sql]):
                raise Exception('未知错误')
        else:
            raise Exception('新密码不合法')


def query(table, **attrib):
    '''
        传参同modify_cell
        raise Exception('非法查询条件')，如果：value中有空值、或key中有table不存在的属性名或value类型与属性类型不匹配
        return 包含全部查询结果的列表，每个列表元素是一个字典，包含查询结果的全部attrib（均为字符串形式，空值value设为空串或None）。
        如果attrib是空的，视为不设检索条件、返回table所有内容
    '''
    if len(attrib)==0:
        sql='select * from {}'.format(table)
    else:
        str_select = ''
        for key in attrib.keys():
            value = attrib[key]
            if type(value) == int:
                str_select += key + '=' + str(value) + ' and '
            elif type(value) == str:
                str_select += key + '=\'' + value + '\' and '
            else:
                raise Exception('非法查询条件')
        sql = 'select * from {} where {}'.format(table, str_select[:-4])
    # print(sql)
    if not execute([sql]):
        raise Exception('非法查询条件')
    else:
        return fetch(sql)


def stu_query_course(sno, cno=None, cname=None):
    '''
        以学生sno视角检索课程信息。
        cno和cname最多只传入一个，在所有课程中检索并返回符合cno或cname的课程列表。如果cno和cname都为None说明不设检索条件，Course中全部课程均符合。
        raise Exception('非法学号') 如果：sno不存在
        return 课程信息列表 otherwise
        列表元素格式为该门课的数据字典，key值包括：Course表中的全部属性、cdept对应的dname、该门课全部任课教师cteacher（其value是教师列表，
            列表元素是教师姓名）、该门课全部已经通过申请的助教cta（其value是助教列表，列表元素是助教姓名）、
            该门课全部排课croom（其value是排课信息列表，列表元素是元组(rname,time)）、该门课成绩grade（未选课或未评分均设为空字符串）、
            学生是否选课pick（其value是布尔值，若学生选择了该门课程则为True，否则为False）、申请该门课助教的信息agree（未申请设为空字符串）
    '''
    if not is_lawful_no(sno) or not value_exist(sno=sno):
        raise Exception('非法学号')
    else:
        if cno == None and cname == None:
            res = fetch('select * from Course')
        elif cno == None:
            res = fetch('select * from Course where cname={};'.format('\'' + cname + '\''))
        elif cname == None:
            res = fetch('select * from Course where cno={};'.format(cno))
        for item in res:
            cno = item['cno']
            item['cteacher'] = get_tname_of_course(cno)
            item['cta'] = get_atname_of_course(cno)
            item['croom'] = get_croom_of_course(cno)
            grade = get_grade_of_course(sno, cno)
            item['grade'] = '' if (grade == None) else grade
            item['pick'] = already_select_course(sno, cno)
            item['agree'] = is_at_of_course(sno, cno)
        return res


def stu_query_book(sno):
    '''
        raise Exception('非法学号') 如果：sno不存在，或者学号值是不合法的
        return 元组(A, B) otherwise
        A和B是两个列表，A包含学号为sno的学生所选课程所需的全部书籍，B包含其所选课程中全部已购书籍。
        A、B的列表元素定义为该本教材的数据字典，key值包括：Book表中的全部属性以及学生购买该书的数量bcnt
    '''
    if not is_lawful_no(sno) or not value_exist(sno=sno):
        raise Exception('非法学号')
    else:
        sno = '\'' + sno + '\''
        sql0 = 'drop view if exists v_bcnt,v_A,v_B'
        sql1 = 'create view v_bcnt(bno,bcnt) as (select bno,count(*) from SB where sno={} group by bno )'.format(sno)
        sql2 = 'create view v_A(bno,bname,bstore) as (select * from Book where bno in (select bno from CB where cno in (select cno from SC where sno={})))'.format(
            sno)
        sql3 = 'select v_A.*,ifnull(bcnt,0) as bcnt from v_A left join v_bcnt on v_bcnt.bno=v_A.bno'
        sql4 = 'create view v_B(bno,bname,bstore) as (select * from Book where bno in (select bno from SB where sno={}) and bno in (select bno from SB where sno={}))'.format(
            sno, sno)
        sql5 = 'select v_B.*,v_bcnt.bcnt from v_B join v_bcnt on v_bcnt.bno=v_B.bno'
        execute([sql0, sql1, sql2, sql4])
        A = fetch(sql3)
        B = fetch(sql5)
        return tuple([A, B])


def stu_buy_book(sno, bno):
    '''
        raise Exception('非法学号') 如果：学生sno不存在
        raise Exception('非法ISBN') 如果：教材bno不存在
        raise Exception('您未选相关课') 如果：sno没有选修任何以bno为参考书的课程
        raise Exception('库存不足') 如果：参考书bno库存为0
        否则，Book表中库存减一、在SB表中插入购书信息。失败则raise Exception('未知错误')。
    '''
    if not is_lawful_no(sno) or not value_exist(sno=sno):
        raise Exception('非法学号')
    elif not is_lawful_bno(bno) or not value_exist(bno=bno):
        raise Exception('非法ISBN')
    elif get_book_storage(bno) <= 0:
        raise Exception('库存不足')
    else:
        result = fetch(
            'select cno from cb where bno={} and cno in (select cno from sc where sno={})'.format('\'' + bno + '\'',
                                                                                                  '\'' + sno + '\''))
        if (len(result) == 0):
            raise Exception('您未选相关课')
        try:
            new_cell('SB', sno=sno, bno=bno)
            modify_cell('Book', bno=bno, bstore=get_book_storage(bno) - 1)
        except:
            raise Exception('未知错误')


def stu_pick_course(sno, cno):
    '''
        raise Exception('非法数据') 如果：sno或cno不存在；
        raise Exception('重复选课') 如果：学生已经选择了该课程；
        raise Exception('课程人数已满') 如果：选择该课程的学生总数不小于课程课容量。
        否则，在选课表中插入选课信息，成绩设为空值。失败则raise Exception('未知错误')。
    '''

    if not is_lawful_no(sno) or not value_exist(sno=sno):
        raise Exception('非法数据')
    elif not is_lawful_cno(cno) or not value_exist(cno=cno):
        raise Exception('非法数据')
    elif already_select_course(sno, cno):
        raise Exception('重复选课')
    elif is_course_full(cno):
        raise Exception('课程人数已满')
    else:
        sno = '\'' + sno + '\''
        if not execute(['insert into SC values({},{},null);'.format(sno, cno)]):
            raise Exception('未知错误')


def query_timetable(**no):
    '''
        传参的key值只在'sno'和'tno'中取，返回sno学生所选课程的全部排课列表/tno教师所授课程的全部排课列表，no不存在则raise Exception('非法学号或工号')。
        列表元素为元组(课程名cname、教室名rname、上课时间ctime) ctime形式为元组（int X，int Y）表示周X第Y节。
    '''
    for key in no:
        value = no[key]
        if key == 'sno':
            if not is_lawful_no(value) or not value_exist(sno=value):
                raise Exception('非法学号或工号')
            else:
                sno = '\'' + value + '\''
                res = fetch(
                    'select Course.cname,CR.rname,CR.ctime from Course,CR where Course.cno=CR.cno and CR.cno in (select cno from SC where sno={});'.format(
                        sno))
                return_res = []
                for item in res:
                    new_list = []
                    for key in item:
                        v = item[key]
                        if key != 'ctime':
                            new_list.append(v)
                        else:
                            strs = v.split('-')
                            new_list.append(tuple([int(strs[0]), int(strs[1])]))
                    return_res.append(tuple(new_list))
                return return_res
        elif key == 'tno':
            tno = '\'' + value + '\''
            res = fetch(
                'select Course.cname,CR.rname,CR.ctime from Course,CR where Course.cno=CR.cno and CR.cno in (select cno from TC where tno={});'.format(
                    tno))
            return_res = []
            for item in res:
                new_list = []
                for v in item.values():
                    if key != 'ctime':
                        new_list.append(v)
                    else:
                        strs = v.split('-')
                        new_list.append(tuple(int(strs[0], int(strs[1]))))
                return_res.append(tuple(new_list))
            return return_res
        else:
            raise Exception('非法属性')


def tec_query_course(tno):
    '''
        raise Exception('非法工号') 如果：tno不存在
        return tno教师全部已开课程信息列表，列表元素为该门课数据字典，key值包括：Course表中的全部属性、该门课全部任课教师cteacher（其value是教师列表，
            列表元素是教师姓名）、该门课全部已经通过申请的助教cta（其value是助教列表，列表元素是助教姓名）、
            该门课全部排课croom（其value是排课信息列表，列表元素是元组(rname,ctime)）
    '''
    if not is_lawful_no(tno) or not value_exist(tno=tno):
        raise Exception('非法工号')
    else:
        tno = '\'' + tno + '\''
        course_list = fetch('select * from Course where cno in (select cno from TC where tno={});'.format(tno))
        for course in course_list:
            cno = course['cno']
            res_tname = fetch('select tname from Teacher where tno in (select tno from TC where cno={})'.format(cno))
            course['cteacher'] = [item['tname'] for item in res_tname]
            res_cta = fetch(
                'select sname from Student where sno in (select sno from CTA where agree=\'Y\' and cno={})'.format(
                    cno))
            course['cta'] = [item['sname'] for item in res_cta]
            res_room = fetch('select rname,ctime from CR where cno={}'.format(cno))
            course['croom'] = [tuple([item['rname'], item['ctime']]) for item in res_room]
        return course_list


def tec_new_course(tno, **attrib):
    '''
    接受tno和一个课程除了cno以外的其他字典信息
    cno函数内自增生成，创建这个课程，然后把tno,cno加到TC里，tno如果是空字符串就不用加入TC

    过程一：
    往Course表插入新课信息
     raise Exception('课程信息非法或不足') 如果：相关字段值非法，或缺少某些属性值
    过程二:
    如果tno不为空，往TC中插入排课信息
    raise Exception('教师工号非法或不存在') 如果：教师工号非法或不存在
    在TC表中执行插入，失败则raise Exception('未知错误')
    '''
    if not check_course_constraint(attrib):
        raise Exception('课程信息非法')
    else:
        try:
            new_cell('Course', cname=attrib['cname'], cdept=attrib['cdept'], ccap=attrib['ccap'],
                     ccredit=attrib['ccredit'], cdate=attrib['cdate'])
        except:
            raise Exception('课程信息非法或不足')
        # 过程二
        if tno != '':
            if not is_lawful_no(tno) or not value_exist(tno=tno):
                raise Exception('教师工号非法或不存在')
            else:
                try:
                    res = query('Course', cname=attrib['cname'], cdept=attrib['cdept'], ccap=attrib['ccap'],
                                ccredit=attrib['ccredit'], cdate=attrib['cdate'])
                    # print(res)
                    new_cell('TC', tno=tno, cno=res[0]['cno'])
                except:
                    raise Exception('未知错误')


def tec_authority(tno, cno):
    '''
    return True 如果：tno是cno的授课教师
    return False 如果：tno不存在/cno不存在/tno不是cno的授课教师
    '''
    if not is_lawful_no(tno) or not value_exist(tno=tno):
        return False
    elif not is_lawful_cno(cno) or not value_exist(cno=cno):
        return False
    else:
        tno = '\'' + tno + '\''
        res = fetch('select tno from TC where cno={} and tno={};'.format(cno, tno))
        if len(res) == 0:
            return False
        else:
            return True


def query_course_student(cno, sno=None, sname=None):
    '''
    检索选修了课程cno的全部学生信息。
    sno和sname最多只传入一个，在选修了课程cno的全部学生中检索并返回符合sno或sname的学生列表。sno和sname都为None说明不设检索条件，返回所有选课学生。
    raise Exception('非法课程代码') 如果：cno不存在
    return 学生信息列表，列表元素为学生数据字典，key值包括：Student表全部属性（除了密码）、分数grade
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno):
        raise Exception('非法课程代码')
    else:
        if sno == None and sname == None:
            sql = 'select Student.sno,sid,sname,ssex,sdept,stel,grade from Student,SC where SC.cno={} and SC.sno=Student.sno'.format(
                cno)
            return fetch(sql)
        elif sno != None:
            sno = '\'' + sno + '\''
            sql = 'select Student.sno,sid,sname,ssex,sdept,stel,grade from Student,SC where SC.cno={} and SC.sno={} and SC.sno=Student.sno'.format(
                cno, sno)
            return fetch(sql)
        elif sname != None:
            sname = '\'' + sname + '\''
            sql = 'select Student.sno,sid,sname,ssex,sdept,stel,grade from Student,SC where SC.cno={} and SC.sno in (select sno from Student where sname={}) and SC.sno=Student.sno'.format(
                cno, sname)
            return fetch(sql)


def query_course_ta(cno):
    '''
    raise Exception('非法课程代码') 如果：cno不存在
    return 元组(A,B)
    A是申请了cno课程但未被通过的学生信息列表，列表元素为学生数据字典，key值包括：Student表全部属性（除了密码）
    B是申请了cno课程且申请被通过的学生信息列表，列表元素为学生数据字典，key值包括：Student表全部属性（除了密码）
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno):
        return Exception('非法课程代码')
    else:
        A = fetch(
            'select sno,sid,sname,ssex,sdept,stel from Student where sno in (select sno from CTA where agree=\'N\' and cno={})'.format(
                cno))
        B = fetch(
            'select sno,sid,sname,ssex,sdept,stel from Student where sno in (select sno from CTA where agree=\'Y\' and cno={})'.format(
                cno))
        return tuple([A, B])


def new_course_book(cno, bno, bname):
    '''
    过程一：
    触发：若bno与Book中主码重复，则检查bname是否与Book中对应书名相同，不同则raise Exception('教材数据冲突')；
    若不与Book中主码重复，则尝试在Book中执行插入(bno,bname,0)，失败则raise Exception('无法新增教材')。
    过程二：
    在CB表中执行插入(cno,bno)，如果可以插入。
    如果不可以插入，raise Exception('数据非法或参考书重复')
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno) or not is_lawful_bno(bno) or not is_lawful_name(bname):
        raise Exception('数据非法或参考书重复')
    else:
        if value_exist(bno=bno):
            res = fetch(
                'select bname from Book where bno={} and bname={}'.format('\'' + bno + '\'', '\'' + bname + '\''))
            if len(res) == 0:
                raise Exception('教材数据冲突')
        else:
            try:
                new_cell('Book', bno=bno, bname=bname, bstore=0)
            except:
                raise Exception('无法新增教材')
        # 过程2
        try:
            new_cell('CB', cno=cno, bno=bno)
        except:
            raise Exception('数据非法或参考书重复')


def delete_course_book(cno, bno):
    '''
    过程一：
    在CB表中尝试删除(cno,bno)，失败则raise Exception('数据非法或不存在参考书')
    过程二：
    触发：如果CB表中已没有其他课程选择bno作为参考书，且Book表中该书库存为0，则在Book中删除该书（删除失败不需要抛出异常）。
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno) or not is_lawful_bno(bno) or not value_exist(bno=bno):
        raise Exception('数据非法或不存在参考书')
    else:
        try:
            delete_cell('CB', cno=cno, bno=bno)
        except:
            raise Exception('数据非法或不存在参考书')
        if len(fetch('select cno from CB where bno={}')) == 0 and get_book_storage(bno) == 0:
            try:
                delete_cell('Book', bno=bno)
            except:
                pass


def course_busy_time(cno):
    '''
    raise Exception('非法课程代码') 如果：cno不存在。
    return cno课程所有任课教师教授的所有课程的上课时间列表，在这些时间里不能给cno排课。
    列表元素为元组（int X，int Y）表示周X第Y节。
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno):
        raise Exception('非法课程代码')
    else:
        res = fetch(
            'select ctime from CR where cno in (select cno from TC where tno in (select tno from TC where cno={}))'.format(
                cno))
        return_list = []
        for item in res:
            strs = item['ctime'].split('-')
            return_list.append((int(strs[0]), int(strs[1])))
        return return_list


def time_free_room(cno, x, y):
    '''
    raise Exception('非法课程代码或时间') 如果：cno不是合法课程/时间“X-Y”不在接口表项定义的合法上课时间范围内
    return 教室信息列表，包含所有在时间“X-Y”没有被排课、教室容量不小于课程课容量的教室。
        列表元素定义为元组（教室名，教室容量）
    '''

    if type(x) != int or type(y) != int or x <= 0 or x > 7 or y <= 0 or y > 14:
        raise Exception('非法课程代码或时间')
    elif not is_lawful_cno(cno) or not value_exist(cno=cno):
        raise Exception('非法课程代码或时间')
    else:
        res = fetch(
            'select rname,rcap from Room where rname not in (select rname from CR where ctime=\'{}-{}\') and rcap>={}'.format(
                x, y, get_course_student(cno)))
        q_list = []
        for item in res:
            q_list.append((item['rname'], item['rcap']))
        return q_list


def arrange_course(cno, x, y, rname):
    '''
    为课程cno增加一节星期x第y节在教室rname的排课。
    raise Exception('非法数据') 如果：存在非法数据
    raise Exception('教师时间冲突') 如果：该课程任课教师在该时间被排了其他课
    raise Exception('教室被占用') 如果：该教室在该时间被排了其他课
    raise Exception('非教室容量不足') 如果：该教室容量小于课程课容量
    在CR表中执行插入，失败则raise Exception('数据非法或重复')
    '''
    if not is_lawful_cno(cno) or not value_exist(cno=cno):
        raise Exception('存在非法数据')
    elif type(x) != int or type(y) != int or x <= 0 or x > 7 or y <= 0 or y > 14:
        raise Exception('存在非法数据')
    elif not is_lawful_name(rname) or not value_exist(rname=rname):
        raise Exception('存在非法数据')
    elif (x, y) in course_busy_time(cno):
        raise Exception('教师时间冲突')
    else:
        free_room = time_free_room(cno, x, y)
        has_find = False
        for item in free_room:
            if rname == item[0]:
                has_find = True
                break
        if not has_find:
            raise Exception('教室被占用或教室容量不足')
        else:
            try:
                new_cell('CR', cno=cno, rname=rname, ctime='{}-{}'.format(x, y))
            except:
                raise Exception('数据非法或重复')


def load_data(filename):
    if not execute(readSql(filename)):
        raise Exception('加载数据失败')


def init_db(ano, apwd, atel=None, amail=None, create=False):
    global con, cur, check_constraint
    con = pymysql.connect(host='localhost', user=ano, password=apwd, port=3306, db='jiaowu',
                          cursorclass=pymysql.cursors.DictCursor)
    cur = con.cursor()
    if create:
        create_table()
    else:
        execute(['set foreign_key_checks=1;'])
    check_constraint = {'Student': check_student_constraint, 'Jiaowu': check_jiaowu_constraint,
                        'Teacher': check_teacher_constraint, 'Administrator': check_administrator_constraint,
                        'Course': check_course_constraint, 'Book': check_book_constraint,
                        'Room': check_room_constraint, 'Department': check_department_constraint,
                        'CPS': check_cps_constraint, 'CB': check_cb_constraint,
                        'CR': check_cr_constraint, 'SC': check_sc_constraint,
                        'TC': check_tc_constraint, 'CTA': check_cta_constraint, 'SB': check_sb_constraint}
    print('init done')


def test():
#new_cell
    # new_cell('Student',sno='17370000',sname='胡歌',ssex='男',sdept='',stel='110110110',sid='987654321987654321',spwd='hugepwdpwd')
    # new_cell('Course',cname='机器学习',ccap=150,ccredit=2,cdept='6',cdate='2019')
    # new_cell('Teacher', tno='t3', tname='沈元', tsex='男', tdept='2', ttel='1010101010', tid='887654321987654321',
    #          tpwd='shenyuanpwdpwd')
    # new_cell('Book', bname='<机器学习>', bno='4-600-82162-4', bstore=2)
    # new_cell('Department', dno='15', dname='宇航系', dhead='')
    # new_cell('Room', rname='机器学习', rcap=150)
    # new_cell('Jiaowu', jno='j2', jid='987654321987654329', jpwd='j1pwdpwd', jname='吃瓜群众', jtel='158110110', jmail='')
    # new_cell('CPS',pcno=1,scno=2)
    # new_cell('CB',cno=1,bno='4-600-82162-4')
    # new_cell('CR',cno=1,rname='机器学习',ctime='1-5')
    # new_cell('SC',sno='17370000',cno=1,grade=100)
    # new_cell('TC',tno='t3',cno=1)
    # new_cell('CTA',sno='17370000',cno=2,agree='Y')
    # new_cell('SB', sno='17370000', bno='4-600-82162-4')

#modify_cell
    # modify_cell('Student',sno='17370000',sname='胡歌1',sdept='6',stel='110110110',sid='987654321987654321',spwd='hugepwdpwd')
    # modify_cell('Course', cno=1, cname='机器学习', ccap=150, ccredit=2, cdept='6', cdate='2019')
    # modify_cell('Teacher', tno='t3', tname='沈元', tsex='男', tdept='2', ttel='1010101010', tid='887654321987654321',
    #             tpwd='shenyuanpwdpwd')
    # modify_cell('Book', bname='<机器学习>', bno='4-600-82162-4', bstore=2)
    # modify_cell('Department', dno='15', dname='宇航系', dhead='')
    # modify_cell('Room', rname='机器学习', rcap=150)
    # modify_cell('Jiaowu', jno='j2', jid='987654321987654329', jpwd='j1pwdpwd', jname='吃瓜群众', jtel='158110110', jmail='')
    # modify_cell('SC', sno='17370000', cno=1, grade=100)
    # modify_cell('CTA', sno='17370000', cno=2, agree='Y')
    # modify_cell('SB', id=1, sno='17370000', bno='4-600-82162-4')


#delete_cell()
    # delete_cell('Student',sno='17370000',sname='胡歌',ssex='男',sdept='',stel='110110110',sid='987654321987654321',spwd='hugepwdpwd')
    # delete_cell('Course',cno=1)
    # delete_cell('Teacher', tno='t3')
    # delete_cell('Book', bno='4-600-82162-4')
    # delete_cell('Department', dno='15')
    # delete_cell('Room', rname='机器学习')
    # delete_cell('Jiaowu', jno='j2')
    # delete_cell('CPS',pcno=1,scno=2)
    # delete_cell('CB',cno=1,bno='4-600-82162-4')
    # delete_cell('CR',cno=1,rname='机器学习',ctime='1-5')
    # delete_cell('SC',sno='17370000',cno=1)
    # delete_cell('TC',tno='t3',cno=1)
    # delete_cell('CTA',sno='17370000',cno=2)
    # delete_cell('SB', id=1)

#validate()
    # print(validate('Student','17230000','pwdpwd'))
    # print(validate('Student','17230000','pwdpwd1'))
    # print(validate('Teacher','t1','pwdpwd'))
    # print(validate('Teacher','t1','pwdpwd1'))
    # print(validate('Administrator','a1','pwdpwd'))
    # print(validate('Administrator','a1','pwdpwd1'))
    # print(validate('Jiaowu','j1','pwdpwd'))
    # print(validate('Jiaowu','j1','pwdpwd1'))

#change_pwd
    # change_pwd('Student','17230000','pwdpwd','pwdpwdnew')
    # change_pwd('Teacher','t1','pwdpwd','pwdpwdnew')
    # change_pwd('Administrator','a1','pwdpwd','pwdpwdnew')
    # change_pwd('Jiaowu','j1','pwdpwd','pwdpwdnew')

#query
    # print(query('Student',sname='何瑞'))
    # print(query('Student',sno='17373174'))
    #
    # print(query('Teacher',tno='t1'))
    #
    # print(query('Course',cno=1))
    # print(query('Course',cname='数据结构'))
    # print(query('Course',cdept='6',cdate='2019'))
    #
    # print(query('Book',bname='<<c语言>>'))
    # print(query('Book',bno='2-600-82162-4'))
    #
    # print(query('Room',rname='主M402'))
    #
    # print(query('Department'))

    print(stu_query_course('17373174'))         #何瑞查询全部课程
    print(stu_query_course('17373174',cname='c语言'))         #何瑞查询c语言课程

    stu_pick_course('17373174',4)               #何瑞选课：数据库
    print(stu_query_book('17373174'))           #查询何瑞应买和已买的书籍信息
    stu_buy_book('17373174','0-751-12345-5')    #何瑞买算法导论


    print(query_timetable(sno='17373174'))
    print(query_timetable(tno='t1'))
    print(query_timetable(tno='t2'))



    print(tec_query_course('t1'))                                                      #教师一 查询自己的开课情况
    for course in tec_query_course('t1'):                                              #教师一 验证tec_authority函数
        print(tec_authority('t1',course['cno']))
    tec_new_course('t2', cname='数据挖掘', ccap=40, ccredit=2, cdept='6', cdate='2019') #教师一 新开一门课:数据挖掘
    print(tec_query_course('t1'))                                                      #教师一 再次查询自己的开课情况


    print(query_course_student(3))                                                     #查询选修了3号课程的所有学生信息
    print(query_course_student(3,'17230000'))                                          #查询选修了3号课程、姓名为何瑞的学生信息

    print(query_course_ta(3))                                                          #查询3号课程的助教申请信息


    new_course_book(4,'3-600-82162-4','<<数据库>>')                                     #指定数据库课程教材为<<数据库>>
    delete_course_book(4,'3-600-82162-4')                                              #解除绑定：数据库 ---  <<数据库>>


    print(course_busy_time(3))                      #查询3号课程（C语言）的教师已排课的时间
    print(time_free_room(3,2,1))                    #查询（2,1）无课的够大的教室排给 3号课程
    print(time_free_room(3, 1, 7))                  #查询（1,7）无课的够大的教室排给 3号课程

    arrange_course(3,1,7,'主M402') # 3号课程排在（1,7）的主M402


    return


if __name__ == '__main__':
    init_db('henry', 'Herui15823439009!',create=True)
    load_data('./sql/load_data.sql')
    # test()

