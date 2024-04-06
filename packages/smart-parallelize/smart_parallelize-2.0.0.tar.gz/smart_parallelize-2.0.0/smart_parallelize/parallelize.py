import ray
import numpy as np
from time import sleep
from ray.exceptions import RaySystemError



def get_mem_func():
    try:
        MEMORY = ray.available_resources()['memory']
    except ray.exceptions.RaySystemError:
        ray.init()
        MEMORY = ray.available_resources()['memory']
    try:
        CPUS = ray.available_resources()['CPU']
        MEM_PER_WORKER = (MEMORY / CPUS) * 0.8
    except KeyError:
        # get number of cores
        import multiprocessing
        CPUS = multiprocessing.cpu_count()
        MEM_PER_WORKER = (MEMORY / CPUS) * 0.8
    MEMORY = int(MEMORY)
    CPUS   = int(CPUS)
    MEM_PER_WORKER = int(MEM_PER_WORKER)
    return MEMORY, CPUS, MEM_PER_WORKER

try:
	MEMORY, CPUS, MEM_PER_WORKER = get_mem_func()
except RaySystemError:
	MEMORY, CPUS, MEM_PER_WORKER = get_mem_func()

def smart_parallelize(func): 
    '''FIRST ARG MUST BE ARG TO BE PARALLELIZED'''

    def wrap(**kwargs): 
        def f2(**kwargs):
            par_args = list(kwargs.keys())[:n_args2parallelize]
            data_par_args = [kwargs[i] for i in par_args]
            results = []
            for i, _ in enumerate(data_par_args[0]):
                kwargs_0 = kwargs.copy()
                for j, _ in enumerate(data_par_args):
                    kwargs_0[par_args[j]] = data_par_args[j][i]
                r = func(**kwargs_0)
                results.append(r)
            return results
        @ray.remote(memory=MEM_PER_WORKER)
        def get_results(**kwargs):
            try:
                args_names = ray.get(args_names_put)
                args_vals  = ray.get(args_vals_put)
                kwargs2 = dict(zip(args_names, args_vals))
                kwargs.update(kwargs2)
            except NameError:
                pass
            results = f2(**kwargs)
            return results
        
        try:
            n_args2parallelize = kwargs['n_args2parallelize']
            # delete n_args2parallelize from kwargs
            del kwargs['n_args2parallelize']
        except KeyError:
            n_args2parallelize = 1

        par_args = list(kwargs.keys())[:n_args2parallelize]
        arg2parallelize_unsplit = [kwargs[i] for i in par_args]

        # split into CPUS chunks
        arg2parallelize = [np.array_split(i, CPUS) for i in arg2parallelize_unsplit]

        arg_names = list(kwargs.keys())[n_args2parallelize:]
        arg_vals  = list(kwargs.values())[n_args2parallelize:]

        if len(arg_names) != 0:
            args_names_put = ray.put(arg_names)
            args_vals_put  = ray.put(arg_vals)

        workers = []
        for i in range(len(arg2parallelize[0])):
            if len(arg2parallelize[0][i]) == 0:
                continue
            # par_arg    = {list(kwargs.keys())[0]:arg2parallelize[i]}
            par_arg = {}
            for j in range(len(par_args)):
                par_arg[par_args[j]] = arg2parallelize[j][i]
            workers.append(get_results.remote(**par_arg))
        result = ray.get(workers)

        r_test = result[0][0]
        try:
            n_outputs = len(r_test)
        except TypeError:
            n_outputs = 1

        results = []
        for i in range(n_outputs):
            results.append([])
        for i in range(len(result)):
            for j in range(len(result[i])):
                for k in range(n_outputs):
                    try:
                        results[k].append(result[i][j][k])
                    except TypeError:
                        results[k].append(result[i][j])
        return results
    return wrap 


if __name__ == "__main__":
    import timeit
    from scipy.integrate import quad

    @smart_parallelize
    def func(x, y):
        fnc = lambda x: np.exp(-x*y)
        return quad(fnc, 0, x)[0]
    
    x = np.ones((25,))
    y = np.ones((25,))*2
    # y = 2
    start  = timeit.default_timer()
    answer = func(x=x, y=y, n_args2parallelize=2)
    stop  = timeit.default_timer()
    print(stop - start)
    print(answer)


    start  = timeit.default_timer()
    answer = []
    for i, val in enumerate(x):
        sleep(1)
        answer.append(val+y)
    stop = timeit.default_timer()
    print(stop - start)

