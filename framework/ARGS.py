import types
import sys

class ARGS():
    @staticmethod
    def arg(num: int):
        if num < len(sys.argv):
            return sys.argv[num].lower()
        else:
            return False

    @staticmethod
    def args(args: list):
        if len(sys.argv) != (len(args) + 1):
            return False

        i = 0

        for item in args:
            i += 1
            if type(item) == str:
                if sys.argv[i].lower() != item.lower():
                    return False


        return True