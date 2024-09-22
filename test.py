from gibbon_flow.flow import flow, task
import time


@task(name="task1")
def task1():
    time.sleep(1)
    print("task1")


@task(name="task2")
def task2():
    time.sleep(2)
    print("task2")


@task(name="task3")
def task3():
    time.sleep(3)
    print("task3")


@flow(name="flow1")
def flow1():
    task1()
    task3()
    task3()


@flow(name="flow2")
def flow2():
    flow1()
    task2()

