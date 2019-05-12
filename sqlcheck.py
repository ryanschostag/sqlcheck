#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 19:31:41 2019

@author: john
Module to showcase a way to control which SQL statements can be 
passed through a SQL connection

Use cases:
    
    1. Single SELECT, UPDATE, and INSERT statement
    2. Do not pass any other commands but SELECT, UPDATE, and INSERT
    3. Multiple statement types in single statement
    4. Multiple statements

To find out how many SELECT, INSERT, UPDATE statements there are, will use
regular expressions. Then, using the findall() method, examine each statement
type.
    
"""
from collections import defaultdict
import re
import logging

format_string = ('{"time": "%(asctime)s", "level": "%(levelname)s", '
                 '"file": "%(pathname)s", "function": "%(funcName)s", '
                 '"line": %(lineno)d, "message": "%(message)s"}')
logging.basicConfig(
    filename='sqlcheck.log',
    format=format_string,
    level=logging.DEBUG,
    filemode='w'
)

class SQL:
    _sql = defaultdict(dict)
    valid_select = 'table_one table_two MAX(id)'
    valid_update = 'UPDATE table_one SET'
    valid_insert= 'INSERT INTO table_three VALUE(SELECT MAX(id) + 1 FROM table_three),'
    invalid = []
    valid = []
    commits = 0
    total = 0
    select_regex = re.compile(r'select|SELECT.*')
    insert_regex = re.compile(r'insert|INSERT.*')
    update_regex = re.compile(r'update|UPDATE.*')
    split_rule = ' '


def send():
    for k, v in SQL._sql.items():
        if False not in v['valid']:
            v['committed'] = True
            SQL.commits += 1
        else:
            v['committed'] = False
    else:
        logging.debug(SQL._sql)
        SQL._sql.clear()


def validate(sql_statement, validation_string, statement_type, record):
    """
    Validates a SQL statement
    
    :param sql_statement: <string>
    :param validation_string: <string>
    :param statement_type: <string>
    :param record: <int> key in SQL._sql
    """
    if SQL._sql[record]['committed']:
        logging.debug(f'Already committed: {SQL._sql[record]}')
        return None
    
    if statement_type == 'select':
        for i in validation_string.split(SQL.split_rule):
            if i in sql_statement:
                logging.debug(f'validation_string: {i}')
                logging.debug(f'sql_statement: {sql_statement}')
                SQL._sql[record]['checked'].append(True)
                SQL._sql[record]['valid'].append(True)
            else:
                logging.debug(f'validation_string: {i}')
                logging.debug(f'sql_statement: {sql_statement}')
                SQL._sql[record]['checked'].append(True)
                SQL._sql[record]['valid'].append(False)
    else:
        if validation_string in sql_statement:
            logging.debug(f'validation_string: {validation_string}')
            logging.debug(f'sql_statement: {sql_statement}')
            SQL._sql[record]['checked'].append(True)
            SQL._sql[record]['valid'].append(True)
        else:
            logging.debug(f'validation_string: {validation_string}')
            logging.debug(f'sql_statement: {sql_statement}')
            SQL._sql[record]['checked'].append(True)
            SQL._sql[record]['valid'].append(False)
    
    if True in SQL._sql[record]['valid']:
        SQL.valid.append(SQL._sql[record]['command'])
    else:
        SQL.invalid.append(SQL._sql[record]['command'])


def validation_processor():
    """
    Iterates through SQL._sql[record][select|insert|update] lists 
    and sends each of those lists to the validate function
    
    :returns: None
    """
    for record in SQL._sql:
        if SQL._sql[record]['select']:
            for statement in SQL._sql[record]['select']:
                validate(statement, SQL.valid_select, 'select', record)
        if SQL._sql[record]['insert']:
            for statement in SQL._sql[record]['insert']:
                validate(statement, SQL.valid_insert, 'insert', record)
        if SQL._sql[record]['update']:
            for statement in SQL._sql[record]['update']:
                validate(statement, SQL.valid_update, 'update', record)


def sql_data(*args):
    """
    Loop through *args, which are SQL statements, and 
    enter data in SQL._sql dictionary of dictionaries.
    
    :param args: List of SQL statements (strings)
    :returns: None
    :raises: TypeError
    """
    if '__iter__' not in dir(args):
        if 'key' in dir(args) or isinstance(args, str):
            te = f'Invalid type: {args}'
            logging.error(te)
            raise TypeError(te)
            
    if not args:
        ve = f'Cannot process empty data structure'
        logging.error(ve)
        raise ValueError(ve)
        
    for number, arg in enumerate(args):
        SQL._sql[number]['command'] = arg
        SQL._sql[number]['checked'] = []
        SQL._sql[number]['valid'] = []
        SQL._sql[number]['committed'] = False
        SQL._sql[number]['select'] = re.findall(SQL.select_regex, arg)
        SQL._sql[number]['insert'] = re.findall(SQL.insert_regex, arg)
        SQL._sql[number]['update'] = re.findall(SQL.update_regex, arg)
        SQL._sql[number]['detected'] = sum([
                len(SQL._sql[number]['select']),
                len(SQL._sql[number]['insert']),
                len(SQL._sql[number]['update'])
            ])
        SQL.total += 1
        if SQL._sql[number]['detected'] == 0:
            SQL.invalid.append(arg)


def sql_gateway(*args):
    try:
        sql_data(*args)
        validation_processor()
    except ValueError as val_err:
        logging.error(val_err)
    finally:
        send()


if __name__ == "__main__":
    s1 = 'SELECT * FROM table_one'
    s2 = 'UPDATE table_one SET '
    s3 = 'INSERT INTO table_one WHERE (SELECT id FROM table_two)'
    s4 = 'DROP TABLE table_three'
    s5 = 'SELECT column_one FROM table_two'
    commands = s1, s2, s3, s4, s5
    sql_gateway(*commands)
    print(f'{SQL.commits} commits of {SQL.total}')
    print(f'Committed: {SQL.valid}')
    print(f'Not Committed: {SQL.invalid}')