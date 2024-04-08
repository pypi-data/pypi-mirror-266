import os
import sys
import time


def lyprint_separator(atom_character: str = "=") -> None:
    assert type(atom_character) is str, "The type of atom_character should be string."
    assert len(atom_character) == 1, "The length of atom_character should be 1"

    size = os.get_terminal_size()
    width = size.columns
    print(atom_character * width)


def overwrite_stdout(lines=1):
    sys.stdout.write(f"\033[{lines}A")  # 向上移动光标`lines`行
    sys.stdout.write("\033[K")  # 清除光标所在行


def lyprint_flash(input: str) -> None:
    assert type(input) is str, "The type of atom_character should be string."

    size = os.get_terminal_size()
    width = size.columns
    moveup_lines = len(input) // width + 1

    print(input)
    overwrite_stdout(moveup_lines)


def lyprint_elapsed_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Elapsed Time of {func.__name__}: {elapsed_time}s")
        return result

    return wrapper


if __name__ == "__main__":

    @lyprint_elapsed_time
    def print_howmanyhaha(times=2):
        for i in range(times):
            print("haha")
            r = i
        return r

    r = print_howmanyhaha(3)
    print(r)
