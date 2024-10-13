#!/usr/bin/env python

import logging
import sqlite3

from jirabot.config import DB_FILENAME
from jirabot.log_helper import build_loger
from jirabot.states.registration import RegistationData

log = build_loger('issue', logging.INFO)


def init():
    connection = sqlite3.connect(DB_FILENAME)
    with sqlite3.connect(DB_FILENAME) as connection:
        cursor = connection.cursor()

        # Создаем таблицу Users
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE,
        email TEXT NOT NULL,
        token TEXT NOT NULL,
        site TEXT NOT NULL
        )
        ''')
        connection.commit()


def add_user(registation: RegistationData) -> bool:
    res = False
    with sqlite3.connect(DB_FILENAME) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                'INSERT INTO Users (user_id, email, token, site) VALUES (?, ?, ?, ?)',
                (registation.user_id, registation.email, registation.token,
                 registation.site))
            connection.commit()
        except sqlite3.IntegrityError as e:
            log.error(e)
        else:
            res = True
    return res


def get_reg_date_by_user_id(user_id: int) -> RegistationData | None:
    res = None
    with sqlite3.connect(DB_FILENAME) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(
                'SELECT email, token, site FROM Users WHERE user_id = ?',
                (user_id, ))
            results = cursor.fetchall()
            if not results:
                return None
            results = results[0]
            res = RegistationData(user_id=user_id,
                                  email=results[0],
                                  token=results[1],
                                  site=results[2])
        except sqlite3.IntegrityError as e:
            log.error(e)
    return res

if __name__ == "__main__":
    init()
    # add_user(RegistationData(123123, "username", "token", "www.site.com"))
    reg = get_reg_date_by_user_id(322349924)
    print(reg)
    reg = get_reg_date_by_user_id(322349925)