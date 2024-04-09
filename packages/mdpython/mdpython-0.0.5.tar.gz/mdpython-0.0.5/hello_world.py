from mdpython.debugutils import timer
from random import randint
from math import factorial

timer.start("main")

def count_elements_in_array():
    ar = list(range(randint(1000000,10000000)))
    print(len(ar))

def get_factorial():
    for i in range(5):
        timer.start("looptest")
        num = randint(900,1000)
        print(num, factorial(num))
        timer.stop("looptest")

timer.start("func1")
count_elements_in_array()
timer.stop("func1")

get_factorial()

timer.stop("main")

timer.show()
