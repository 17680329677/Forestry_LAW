import requests, datetime, time
import threading


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        """
        why: 因为threading类没有返回值,因此在此处重新定义MyThread类,使线程拥有返回值
        此方法来源 https://www.cnblogs.com/hujq1029/p/7219163.html?utm_source=itdadao&utm_medium=referral
        """
        super(MyThread, self).__init__()
        self.func = target
        self.args = args

    def run(self):
        # 接受返回值
        self.result = self.func(*self.args)

    def get_result(self):
        # 线程不结束,返回值为None
        try:
            return self.result
        except Exception:
            return None


# 为了限制真实请求时间或函数执行时间的装饰器
def limit_decor(limit_time):
    """
    :param limit_time: 设置最大允许执行时长,单位:秒
    :return: 未超时返回被装饰函数返回值,超时则返回 None
    """

    def functions(func):
        # 执行操作
        def run(*params):
            thre_func = MyThread(target=func, args=params)
            # 主线程结束(超出时长),则线程方法结束
            thre_func.setDaemon(True)
            thre_func.start()
            # 计算分段沉睡次数
            sleep_num = int(limit_time // 1)
            sleep_nums = round(limit_time % 1, 1)
            # 多次短暂沉睡并尝试获取返回值
            for i in range(sleep_num):
                time.sleep(1)
                infor = thre_func.get_result()
                if infor:
                    return infor
            time.sleep(sleep_nums)
            # 最终返回值(不论线程是否已结束)
            if thre_func.get_result():
                return thre_func.get_result()
            else:
                return "请求超时"  # 超时返回  可以自定义
        return run
    return functions


# 接口函数
def time_limit_method(func, *args):
    # 这里把逻辑封装成一个函数,使用线程调用
    a_theadiing = MyThread(target=func, args=args)
    a_theadiing.start()
    a_theadiing.join()
    # 返回结果
    a = a_theadiing.get_result()
    return a


@limit_decor(3)  # 超时设置为3s   2s逻辑未执行完毕返回接口超时
def a2(arg):
    time.sleep(2)
    a = arg + 2
    return a


# 程序入口     未超时返回a的值   超时返回请求超时
if __name__ == '__main__':
    a = time_limit_method(a2, 2)  # 调用接口(这里把函数a1看做一个接口)
    print(a)
