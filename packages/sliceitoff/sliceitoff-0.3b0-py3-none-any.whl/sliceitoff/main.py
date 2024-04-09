""" main.py """
from runpy import run_path
from pathlib import Path

def main():
    """ Let's start the app as current path being base """
    my_path = Path(__file__).parent.resolve()
    run_path(f"{my_path}", run_name="sliceitoff")

if __name__ == "__main__":
    main()
