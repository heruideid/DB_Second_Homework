set foreign_key_checks=0;
use test;
SET sql_safe_updates=0;
delete from student;
delete from teacher;
delete from course;
delete from administrator;
delete from jiaowu;
delete from room;
delete from book;
delete from department;
delete from cps;
delete from cb;
delete from cr;
delete from sb;
delete from cta;
delete from sc;
delete from tc;


alter table course auto_increment=1;
alter table sb auto_increment=1;

insert into student(sno,sid,spwd,sname,ssex,sdept,stel) values('17373174','500381233366664914','pwdpwd','何瑞','男','6','1234567');
insert into student(sno,sid,spwd,sname,ssex,sdept,stel) values('17230000','500111111111111111','pwdpwd','李瑞康','男','6','119110120');
insert into student(sno,sid,spwd,sname,ssex,sdept,stel) values('10000000','500222222222222222','pwdpwd','马冬梅','女','6','1008611');
insert into student(sno,sid,spwd,sname,ssex,sdept,stel) values('20000000','600222222222222222','pwdpwd','沈腾','男','2','1008612');

insert into teacher(tno,tid,tpwd,tname,tsex,tdept,ttel,tmail) values('t1','111111111111111111','pwdpwd','李华','男','2','119110120','lihua@buaa.edu.cn');
insert into teacher(tno,tid,tpwd,tname,tsex,tdept,ttel,tmail) values('t2','222222222222222222','pwdpwd','时磊','男','6','119110120','6666@qq.com');


insert into course(cname,cdept,ccap,ccredit,cdate) values('数据结构','6',150,3,'2019');
insert into course(cname,cdept,ccap,ccredit,cdate) values('算法','6',150,4,'2019');
insert into course(cname,cdept,ccap,ccredit,cdate) values('c语言','6',150,4,'2019');
insert into course(cname,cdept,ccap,ccredit,cdate) values('数据库','21',1,1,'2019');

insert into department(dno,dname,dhead) values('2','电子系','t1');
insert into department(dno,dname,dhead) values('6','计算机系','t2');
insert into department(dno,dname,dhead) values('21','软院',null);

insert into jiaowu(jno,jid,jpwd,jname,jtel,jmail) values('j1','123456789123456789','pwdpwd','henry','1008611','henry@163.com');
insert into administrator(ano,apwd,atel,amail) values('a1','pwdpwd','1008632','harry@163.com');

insert into Room(rname,rcap) values('主M402',200);
insert into Room(rname,rcap) values('主201',100);
insert into Room(rname,rcap) values('J3-301',200);
insert into Room(rname,rcap) values('J1-211',200);
insert into Room(rname,rcap) values('J2-311',200);

insert into book(bno,bname,bstore) values('0-751-12345-5','<算法导论>',100);
insert into book(bno,bname,bstore) values('1-123-12345-6','<数据结构>',100);
insert into book(bno,bname,bstore) values('2-600-82162-4','<<c语言>>',1);
insert into book(bno,bname,bstore) values('3-600-82162-4','<<数据库>>',100);



set foreign_key_checks=1;

#C语言程设需要： <<c语言>>
#数据结构需要：<数据结构> 和 <<c语言>>
#算法需要 ：<算法导论> 和 <<c语言>>
insert into cps(pcno,scno) values(3,2);
insert into cb(cno,bno) values(3,'2-600-82162-4');
insert into cb(cno,bno) values(2,'0-751-12345-5');
insert into cb(cno,bno) values(2,'2-600-82162-4'); 
insert into cb(cno,bno) values(1,'1-123-12345-6'); 
insert into cb(cno,bno) values(1,'2-600-82162-4');

#星期一、四的一二节排C语言 J3-301
insert into cr(cno,rname,ctime) values(3,'J3-301','1-1');
insert into cr(cno,rname,ctime) values(3,'J3-301','1-2');
insert into cr(cno,rname,ctime) values(3,'J3-301','4-1');
insert into cr(cno,rname,ctime) values(3,'J3-301','4-2');
#星期二的一二节排数据结构 J1-211
insert into cr(cno,rname,ctime) values(1,'J1-211','2-1');
insert into cr(cno,rname,ctime) values(1,'J1-211','2-2');
#星期三的三四节排算法 J2-311
insert into cr(cno,rname,ctime) values(2,'J2-311','3-1');
insert into cr(cno,rname,ctime) values(2,'J2-311','3-2');

#何瑞选了c语言和算法
#李瑞康选了C语言和数据结构
insert into sc(sno,cno,grade) values('17373174',3,null);
insert into sc(sno,cno,grade) values('17373174',2,null);
insert into sc(sno,cno,grade) values('17230000',3,null);
insert into sc(sno,cno,grade) values('17230000',1,null);

#教师1 讲数据结构和C语言和算法
#教师2 讲C语言
insert into tc(tno,cno) values('t1',1);
insert into tc(tno,cno) values('t1',3);
insert into tc(tno,cno) values('t2',3);
insert into tc(tno,cno) values('t1',2);

#助教马冬梅
#通过了的申请：算法、C语言助教
#未通过的申请:数据结构
#未申请助教的课:数据库
insert into cta(sno,cno,agree) values('10000000',1,'N');
insert into cta(sno,cno,agree) values('10000000',2,'Y');
insert into cta(sno,cno,agree) values('10000000',3,'Y');

#何瑞买了c语言程序设计
#李瑞康买了C语言程设和数据结构
insert into sb(sno,bno) values('17373174','2-600-82162-4');
insert into sb(sno,bno) values('17230000','2-600-82162-4');
insert into sb(sno,bno) values('17230000','1-123-12345-6');



