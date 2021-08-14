# 🛠 [ToolKit bot](t.me/Tool_Kit_Bot)

<div align="center">
<img alt="GitHub" src="https://img.shields.io/github/license/igorechek06/ToolKit?style=for-the-badge"/>
<img alt="Telegram" src="https://img.shields.io/badge/Telegam-bot-0088cc?style=for-the-badge&logo=telegram" />

<br> 

<img alt="GitHub last commit (main)" src="https://img.shields.io/github/last-commit/igorechek06/ToolKit/main?label=Last%20main%20commit&style=for-the-badge"/>
<img alt="GitHub last commit (dev)" src="https://img.shields.io/github/last-commit/igorechek06/ToolKit/dev?label=Last%20dev%20commit&style=for-the-badge"/>
</div>

<!-- I know it is wrong -->

## Setup database

[Install MySQL](https://dev.mysql.com/downloads/)

Login to MySQL console

    sudo mysql

In MySQL console

    CREATE USER '{username}'@'localhost' IDENTIFIED BY '{password}';
    GRANT ALL PRIVILEGES ON * . * TO '{username}'@'localhost';
    FLUSH PRIVILEGES;
    CREATE DATABASE {database_name};

Where {*} insert their values

## Setup

    python3.9 setup.py
