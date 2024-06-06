# 如果需要产生workload.log,需要单独开启两个终端,一个终端运行serve.py,另一个运行run.py.此时会产生workload.log(其中含有效率测试结果)和serve.log
# import sys
# sys.path.append(r'D:\DS_bookstore\Project_1\bookstore')
from fe.bench.workload import Workload
from fe.bench.session import Session
from fe.bench import check


def run_bench():
    wl = Workload()
    wl.gen_database()

    sessions = []
    for i in range(0, wl.session):
        ss = Session(wl)
        sessions.append(ss)

    for ss in sessions:
        ss.start()

    for ss in sessions:
        ss.join()

    check.checkSumMoney(wl.tot_fund)


def run_hot_one_test():
    wl = Workload()
    wl.gen_database_hot_one_test()
    sessions = []
    for i in range(0, wl.session * 5):
        ss = Session(wl, True)
        sessions.append(ss)
    for ss in sessions:
        ss.start()
    for ss in sessions:
        ss.join()
    check.checkSumMoney(wl.tot_fund)


# if __name__ == "__main__":
#    run_bench()
