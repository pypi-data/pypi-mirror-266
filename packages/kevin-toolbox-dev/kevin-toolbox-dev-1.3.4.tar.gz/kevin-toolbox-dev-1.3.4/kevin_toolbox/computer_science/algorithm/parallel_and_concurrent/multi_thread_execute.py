import concurrent.futures
from kevin_toolbox.computer_science.data_structure import Executor


def multi_thread_execute(executors, thread_nums=50, b_display_progress=True, timeout=None, _hook_for_debug=None):
    """
        多线程执行

        参数：
            executors:                  <list/generator/iterator of Executor> 执行器序列
            thread_nums:                <int> 线程数
            b_display_progress:         <boolean> 是否显示进度条
            timeout:                    <int> 每个线程的最大等待时间，单位是s
                                            默认为 None，表示允许等待无限长的时间
            _hook_for_debug:            <dict/None> 当设置为非 None 值时，将保存中间的执行信息。
                                            包括：
                                                - "execution_order":    执行顺序
                                                - "completion_order":   完成顺序
                                            这些信息与最终结果无关，仅面向更底层的调试需求，任何人都不应依赖该特性
        返回：
            res_ls, failed_idx_ls
            执行结果列表，执行失败的执行器 idx
    """
    executor_ls = []
    for i in executors:
        assert isinstance(i, (Executor,))
        executor_ls.append(i)
    if b_display_progress:
        from tqdm import tqdm
        p_bar = tqdm(total=len(executor_ls))
    else:
        p_bar = None
    _execution_orders, _completion_orders = [], []

    def wrapper(executor, idx):
        nonlocal p_bar, _execution_orders, _completion_orders
        _execution_orders.append(idx)
        res = executor.run()
        _completion_orders.append(idx)
        if p_bar is not None:
            p_bar.update()

        return res

    res_ls, failed_idx_ls = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_nums) as thread_pool:
        # 提交任务
        futures = [thread_pool.submit(wrapper, executor, i) for i, executor in enumerate(executors)]
        # 设置超时时间
        concurrent.futures.wait(futures, timeout=timeout)
        # 
        for i, future in enumerate(futures):
            if future.done() and not future.cancelled():
                res_ls.append(future.result())
            else:
                res_ls.append(None)
                failed_idx_ls.append(i)
    if b_display_progress:
        p_bar.close()

    #
    if isinstance(_hook_for_debug, (dict,)):
        _hook_for_debug.update(dict(execution_orders=_execution_orders, completion_orders=_completion_orders))

    return res_ls, failed_idx_ls


if __name__ == '__main__':
    import time


    def func_(i):
        if i in [2, 3, 7]:
            time.sleep(10)
        else:
            time.sleep(2)
        print(i)
        return i * 2


    hook_for_debug = dict()
    print(multi_thread_execute(executors=[Executor(func=func_, args=(i,)) for i in range(10)], thread_nums=5,
                               _hook_for_debug=hook_for_debug))
    print(hook_for_debug)
