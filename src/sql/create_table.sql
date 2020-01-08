drop database  if  exists test;
create database test;
use test;
set foreign_key_checks=0;
create table Student(
	sno varchar(10) primary key,
	sid varchar(18) not null unique,
	spwd varchar(18) not null,
	sname varchar(10) not null,
	ssex varchar(4) not null check (ssex in('男','女')),
	sdept varchar(4),
	stel varchar(11),
	foreign key(sdept) references Department(dno) on delete set null on update cascade
);

create table Teacher(
	tno varchar(10) primary key,
	tid varchar(18) unique,
	tpwd varchar(18) not null,
	tname varchar(10) not null,
	tsex varchar(4) not null check (tsex in('男','女')),
	tdept varchar(4),
	ttel varchar(11),
	tmail varchar(30),
	foreign key(tdept) references Department(dno) on delete set null on update cascade
);

create table Jiaowu(
	jno varchar(10) primary key,
	jid varchar(18) not null unique,
	jpwd varchar(18) not null,
	jname varchar(10) not null,
	jtel varchar(11),
	jmail varchar(30)
);

create table Administrator(
	ano varchar(10) primary key,
	apwd varchar(18) not null,
	atel varchar(11),
	amail varchar(30)
);

create table Course(
	cno int auto_increment primary key,
	cname varchar(10) not null,
	cdept varchar(4),
	ccap int not null,
	ccredit int not null,
	cdate varchar(4) not null,
	foreign key(cdept) references Department(dno) on delete set null on update cascade
);

create table Book(
	bno varchar(15) primary key,
	bname varchar(10) not null,
	bstore int not null
);

create table Room(
	rname varchar(10) primary key,
	rcap int not null
);

create table Department(
	dno varchar(4) primary key,
	dname varchar(10) not null unique,
	dhead varchar(10),
	foreign key(dhead) references Teacher(tno) on delete set null on update cascade
);

create table CPS(
	pcno int,
	scno int,
	primary key(pcno,scno),
	foreign key(pcno) references Course(cno) on delete cascade on update cascade,
	foreign key(scno) references Course(cno) on delete cascade on update cascade
);

create table CB(
	cno int,
	bno varchar(13),
	primary key(cno,bno),
    index(cno),
	foreign key(cno) references Course(cno) on delete cascade on update cascade,
	foreign key(bno) references Book(bno) on delete cascade on update cascade
);

create table CR(
	cno int,
	rname varchar(10),
	ctime varchar(10),
	primary key(cno,rname,ctime),
	foreign key(cno) references Course(cno) on delete cascade on update cascade,
	foreign key(rname) references Room(rname) on delete cascade on update cascade
);

create table SC(
	sno varchar(10),
	cno int,
	grade int,
	primary key(sno,cno),
	foreign key(sno) references Student(sno) on delete cascade on update cascade,
	foreign key(cno) references Course(cno) on delete cascade on update cascade
);

create table TC(
	tno varchar(10),
	cno int,
	primary key(tno,cno),
	foreign key(tno) references Teacher(tno) on delete cascade on update cascade,
	foreign key(cno) references Course(cno) on delete cascade on update cascade
);

create table CTA(
	sno varchar(10),
	cno int,
	agree varchar(4) not null check (agree in('Y','N')),
	primary key(sno,cno),
	foreign key(sno) references Student(sno) on delete cascade on update cascade,
	foreign key(cno) references Course(cno) on delete cascade on update cascade
);

create table SB(
	id int not null auto_increment,
	sno varchar(10) not null,
	bno varchar(13) not null,
	primary key(id),
	foreign key(sno) references Student(sno) on delete cascade on update cascade,
	foreign key(bno) references Book(bno) on delete cascade on update cascade
);

set foreign_key_checks=1;


