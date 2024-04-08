import sys


def case_converter() -> str:
    if len(sys.argv) == 2:
        return sys.argv[1].upper()


if __name__ == "__main__":
    print(case_converter(sys.argv[1]))
