import sys    
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.DeepChecker import DeepChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
import types

print("==DEEP CHECKER==")

json = {
    'q': 1,
    'w': 2,
    'main': {
        'test1': 4,
        'test2': 5,
        'test3': 6,
        'test4': '7',
    },
    'e': 1,
    'r': 2,
    't': 3,
    'y': 4,
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test4': int,
}

try:
    DeepChecker.check('Deep test 1', json, map, 1)
    print('Deep test 1: Failed')
except LeafBuildException as error:
    print('Deep test 1: OK')

json = {
    'q': 1,
    'w': 2,
    'main': {
        'test1': 4,
        'test2': 5,
        'test3': 6,
        'test4': '7',
    },
    'e': 1,
    'r': 2,
    't': 3,
    'sub1': {
        'test1': 4,
        'test2': 5,
        'test3': 6,
        'sub2': {
            'test1': 4,
            'test2': 5,
            'test3': 6,
            'test4': '7',
        }
    },
    'y': 4,
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test4': int,
}

try:
    DeepChecker.check('Deep test 2', json, map, 2)
    print('Deep test 2: Failed')
except LeafBuildException as error:
    print('Deep test 2: OK')

json = {
    'q': 1,
    'w': 2,
    'main': {
        'test1': 4,
        'test2': 5,
        'test3': 6,
        'test4': '7',
    },
    'e': 1,
    'r': 2,
    't': 3,
    'sub1': {
        'test1': 4,
        'test2': 5,
        'test3': 6,
        'sub2': {
            'test1': 4,
            'test2': 5,
            'test3': 6,
            'test0': {
                'qqq': 4,
                'www': 5,
                'www': 6,
                'rty': 7,
            },
            'test4': '7',
        }
    },
    'y': 4,
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test0': dict,
    'test4': int,
}

try:
    DeepChecker.check('Deep test 3', json, map, 2)
    print('Deep test 3: Failed')
except LeafBuildException as error:
    print('Deep test 3: OK')


json = {
    'q': 1,
    'w': 2,
    'main': {
        'x': 4,
        'y': 5,
        'z': 6,
    },
    'e': 1,
    'r': 2,
    't': 3,
    'zzz': [
        {
            'test1': 1,
            'test2': 2,
            'test3': 3,
            'test4': 4
        },
        {
            'test1': 11,
            'test2': 22,
            'test3': 33,
            'test4': 44
        }
    ],
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test4': int,
}

try:
    DeepChecker.check('Deep test 4', json, map, 2)
    print('Deep test 4: OK')
except LeafBuildException as error:
    print('Deep test 4: Failed')


json = {
    'q': 1,
    'w': 2,
    'e': 1,
    'r': 2,
    't': 3,
    'zzz': [
        {
            'test1': 1,
            'test2': 2,
            'test3': 3,
            'test4': 4
        },
        {
            'test1': 11,
            'test2': 22,
            'test3': 33,
            'test4': '44'
        }
    ],
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test4': int,
}

try:
    DeepChecker.check('Deep test 5', json, map, 1)
    print('Deep test 5: Failed')
except LeafBuildException as error:
    print('Deep test 5: OK')