# 综合教务管理系统

## 环境需求

### 基本需求

- Python 3.7
- MySQL 8.0

### Python包需求

- flask
- flask-login
- pymysql

### 测试平台

- Windows 10

## 运行说明

- 准备一个本机MySQL账号，并在本机MySQL中创建一个名为jiaowu的数据库。
- 通过`python lab2.py`运行，根据命令行提示输入以下信息
  - MySQL账号及密码，用于连接本机MySQL
  - 是否建表(y/n)。若选择y则会在本机jiaowu数据库重新建表；若选择n则会保留原有表。
  - 是否重建数据(y/n)。选择y则会删除本机jiaowu原有数据，用`sql/load_data.sql`中的数据代替。
- 运行成功后flask会在本机IP运行。若本机接入校园网，则任意一台设备接入校园网后可通过IP访问系统，本机可直接通过localhost访问。教务系统顶级管理员账号`a1`，密码`pwdpwd`。