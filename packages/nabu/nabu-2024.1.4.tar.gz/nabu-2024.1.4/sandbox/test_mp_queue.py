import os
from time import time, sleep
from multiprocessing import Process, Queue, current_process
path = os.path
from integrator.integrator import StackIntegrator
from integrator.app.utils import get_distributed_integrator_params

os.environ["OMP_NUM_THREADS"] = "4"

def worker(ai_config, dataset, out_dir, task_queue, out_queue):

    os.environ["OMP_NUM_THREADS"] = "4"
    S = StackIntegrator(ai_config)
    sleep(5)
    S.set_new_dataset(dataset, out_dir, 200)
    print("OK!")

    for task in iter(task_queue.get, 'STOP'):
        i_min, i_max = task
        res = S.process_stack(i_min, i_max)
        out_queue.put(res)


def worker_scan(ai_config, dataset, out_dir):
    S = StackIntegrator(ai_config)
    sleep(5)
    S.set_new_dataset(dataset, out_dir, 200)
    print("OK!")

    for i in range(int(25e3)):
        i_min, i_max = (200 * i, 200 * (i+1))
        res = S.process_stack(i_min, i_max)


def integrate_dataset(ai_config, dataset, out_dir, n_proc):


    tasks = []
    for i in range(int(25e3 / 200)):
        tasks.append((200 * i, 200 * (i+1)))


    # Create queues
    task_queue = Queue()
    done_queue = Queue()

    # Start worker processes
    for i in range(n_proc):
        Process(target=worker, args=(ai_config, dataset, out_dir, task_queue, done_queue)).start()


    input("Start ?")

    # Submit tasks
    for task in tasks:
        task_queue.put(task)




    # Get and print results
    print('Unordered results:')
    for i in range(len(tasks)):
        print('\t', done_queue.get())

    # Tell child processes to stop
    for i in range(n_proc):
        task_queue.put('STOP')



conf, ai_config, cluster, datasets, output_files = get_distributed_integrator_params("/home/esrf/paleo/tmp/xrdct_sessions/ihma109/test.conf")
integrate_dataset(ai_config, datasets[-19], path.dirname(output_files[-19]), 8)