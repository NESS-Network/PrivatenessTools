import sys    
from ..JsonChecker.Checker import JsonChecker
from ..JsonChecker.exceptions.LeafBuildException import LeafBuildException
import types

print("==JSON CHECKER==")

json = {
    'test1': 111,
    'test2': 2.22,
    'test3': '333',
    'test4': [],
    'test5': 'krghierghiefgh'
}

map = {
    'test1': int,
    'test2': float,
    'test3': str,
    'test4': list,
    'test5': int
}

try:
    JsonChecker.check('Types test', json, map)
except LeafBuildException as error:
    print('Types test: OK')

json = {
    'test1': 1,
    'test2': 2,
    'test4': 4,
    'test5': '5'
}

map = {
    'test1': int,
    'test2': int,
    'test3': int,
    'test4': int,
    'test5': str
}


try:
    JsonChecker.check('No key test', json, map)
except LeafBuildException as error:
    print('No key test: OK')

json = {
    'test1': 1,
    'test2': 2,
    'test3': 3,
}

map = {
    'test1': 1,
    'test2': 2,
    'test3': 33,
}


try:
    JsonChecker.check('Wrong value test', json, map)
except LeafBuildException as error:
    print('Wrong value test: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : '2',
        'sub3' : 3.3
    }
}

map = {
    'test1': int,
    'test2': int,
    'main': {
        'sub1': int,
        'sub2': str,
        'sub3': float,
        'x': str
    }
}


try:
    JsonChecker.check('Deep test 1', json, map)
except LeafBuildException as error:
    print('Deep test 1: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : '2',
        'sub3' : 3.3
    },
    'mmm': {
        'm1': {
            '1': 1,
            '2': 2,
            '3': 'str'
        }
    }
}

map = {
    'test1': int,
    'test2': int,
    'main': {
        'sub1': int,
        'sub2': str,
        'sub3': float
    },
    'mmm': {
        'm1': {
            '1': int,
            '2': int,
            '3': int
        }
    }
}


try:
    JsonChecker.check('Deep test 2', json, map)
except LeafBuildException as error:
    print('Deep test 2: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : '2',
        'sub3' : 3.3
    },
    'test3': 1,
    'test4': 2,
}

map = {
    'test1': int,
    'test2': int,
    'main': dict,
    'test3': int,
    'test4': int,
}


try:
    JsonChecker.check('Deep test 3', json, map)
except LeafBuildException as error:
    print('Deep test 3: Failed')
print('Deep test 3: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : '2',
        'sub3' : 3.3,
        'xxx': {
            'x1': 'sdfgdfg',
            'xyz': 'qwerty'
        }
    },
    'test3': 1,
    'test4': 2,
}

map = {
    'test1': int,
    'test2': int,
    'main': {
        'sub1' : int,
        'sub2' : str,
        'sub3' : float,
        'xxx': dict
    },
    'test3': int,
    'test4': int,
}

try:
    JsonChecker.check('Deep test 4', json, map)
except LeafBuildException as error:
    print('Deep test 4: Failed')
print('Deep test 4: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : '2',
        'sub3' : 3.3,
        'xxx': []
    },
    'test3': 1,
    'test4': 2,
}

map = {
    'test1': int,
    'test2': int,
    'main': {
        'sub1' : int,
        'sub2' : str,
        'sub3' : float,
        'xxx': dict
    },
    'test3': int,
    'test4': int,
}

try:
    JsonChecker.check('Deep test 5', json, map)
except LeafBuildException as error:
    print('Deep test 5: OK')

json = {
    'test1': 1,
    'test2': 2,
    'main': {
        'sub1' : 1,
        'sub2' : 2,
        'sub3' : 3,
        'xxx': 4
    },
    'test3': 1,
    'test4': 2,
}

map = {
    'test1': int,
    'test2': int,
    'main': [dict, 4],
    'test3': int,
    'test4': int,
}

try:
    JsonChecker.check('Type test X', json, map)
    print('Complicated type test: OK')
except LeafBuildException as error:
    print('Complicated type test: Failed')


json = {
    'test1': 1,
    'test2': 2,
    'main': 4,
    'test3': 1,
    'test4': 2,
}

map = {
    'test1': int,
    'test2': int,
    'main': lambda arg: "Must not be equal 4" if arg == 4  else True,
    'test3': int,
    'test4': int,
}

try:
    JsonChecker.check('Lambda test', json, map)
    print('Lambda test: Failed')
except LeafBuildException as error:
    print('Lambda test: OK')