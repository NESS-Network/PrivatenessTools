import NessKeys.tests.json_checker
import NessKeys.tests.deep_checker
import NessKeys.tests.keys
import NessKeys.tests.encryption

from framework.ARGS import ARGS

if ARGS.args(['auth', str, str]):
    import NessKeys.tests.auth
    import NessKeys.tests.key_storage
    import NessKeys.tests.encrypted_storage
else:
    print('Authentication test: python run-tests.py auth <username> <node URL>')