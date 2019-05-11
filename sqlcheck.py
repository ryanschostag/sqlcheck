#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 10 19:31:41 2019

@author: john
"""
from collections import defaultdict
from pprint import pprint


class SQL:
    _sql = defaultdict(dict)
    valid_select = 'table_one table_two MAX(id)'
    valid_update = 'UPDATE table_one SET'
    valid_insert= 'INSERT INTO table_three VALUE(SELECT MAX(id) + 1 FROM table_three),'
    invalid = []
    valid = []
    commits = 0
    total = 0


def send():
    pprint(SQL._sql)
    for k, v in SQL._sql.items():
        if v['valid']:
            v['committed'] = True
            SQL.commits += 1
        else:
            v['committed'] = False
    else:
        pprint(SQL._sql)
        SQL._sql.clear()


def validate(sql_statement, validation_string, statement_type):
    record = None
    for key, value in SQL._sql.items():
        if value['command'] == sql_statement:
            record = key
    
    if SQL._sql[record]['committed']:
        return None
    
    if statement_type == 'select':
        for i in validation_string.split(' '):
            if i in sql_statement:
                SQL._sql[record]['checked'] = True
                SQL._sql[record]['valid'] = True
            else:
                SQL._sql[record]['checked'] = True
    else:
        if validation_string in sql_statement:
            SQL._sql[record]['checked'] = True
            SQL._sql[record]['valid'] = True
        else:
            SQL._sql[record]['checked'] = True
    
    if SQL._sql[record]['valid']:
        SQL.valid.append(SQL._sql[record]['command'])
    else:
        SQL.invalid.append(SQL._sql[record]['command'])
    

def sql_statement_parser(*args, record=None):
    for number, arg in enumerate(args):
        SQL._sql[number]['command'] = arg
        SQL._sql[number]['checked'] = False
        SQL._sql[number]['valid'] = False
        SQL._sql[number]['committed'] = False
        SQL.total += 1
        
        if 'select' in arg.lower():
            if 'insert' in arg.lower():
                validate(arg, SQL.valid_insert, 'insert')
            elif 'update' in arg.lower():
                validate(arg, SQL.valid_update, 'update')
            else:
                validate(arg, SQL.valid_select, 'select')
        elif 'update' in arg.lower():
            validate(arg, SQL.valid_update, 'update')
        elif 'insert' in arg.lower():
            validate(arg, SQL.valid_insert, 'insert')
        else:
            validate(arg, SQL.valid_insert, 'invalid_type')
    else:
        if SQL.invalid:
            raise ValueError(f'Invalid Statements: {SQL.invalid}')

def sql_gateway(*args):
    try:
        sql_statement_parser(*args)
    except ValueError as val_err:
        print(val_err)
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