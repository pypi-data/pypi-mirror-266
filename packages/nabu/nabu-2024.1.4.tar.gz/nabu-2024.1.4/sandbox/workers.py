import sys
from os import getpid
from distributed import Client, get_worker


# sur SLURMCluster... peut-on faire autrement ?
def wprint(msg):
    wname = get_worker().name
    fname = "/tmp/workers.log"
    fid = open(fname, "a")
    fid.write(msg + "\n")
    fid.flush()
    fid.close()


def wprint2(msg):
    print(msg, file=sys.stderr, flush=True)




class WorkerProcess:
    def __init__(self, wtype):
        self.wtype = "CPU" if wtype == "CPU" else "GPU"
        self.pid = getpid()
        self._init_worker()

    def _init_worker(self):
        wprint("%s: %s" % (self.wtype, sys.executable))
        if self.wtype == "CPU":
            self._init_cpu()
        else:
            self._init_gpu()
        wprint("[%d] Init %s OK" % (self.pid, self.wtype))

    def _init_cpu(self):
        pass

    def _init_gpu(self):
        wprint("initializing GPU...")
        from nabu.cuda.utils import get_cuda_context, __has_pycuda__, __pycuda_error_msg__
        if __has_pycuda__:
            import pycuda.gpuarray as garray
        if not(__has_pycuda__):
            raise ImportError("Could not import pycuda: %s" % __pycuda_error_msg__)
        self.ctx = get_cuda_context()
        wprint("init GPU OK, context = %s, pycuda = %s - %s" % (str(self.ctx), str(__has_pycuda__), __pycuda_error_msg__))
        # push context ?

    def _process_cpu(self, n):
        return sorted(list(range(n)))

    def _process_gpu(self, n):
        self.ctx.push()
        # ~ wprint("pycuda: %s" % str(__has_pycuda__))
        import pycuda.gpuarray as garray # ??
        d_arr = garray.zeros((2048, 2048), "f")
        for i in range(min(n, 1000)):
            d_arr += 1
        return d_arr.get()

    def process(self, n):
        return {"CPU": self._process_cpu, "GPU": self._process_gpu}[self.wtype](n)


def actor_exec_processing(n, iw=-1):
    w = get_worker()
    worker_process = w.actors[list(w.actors.keys())[iw]]
    wprint("[%d] submit n=%d to %s worker" % (worker_process.pid, n, worker_process.wtype))
    res = worker_process.process(n)
    wprint("ok")
    return res




# ~ client = Client("tcp://160.103.228.120:8786")
# ~ W1 = client.submit(
    # ~ WorkerProcess,
    # ~ "GPU",
    # ~ actor=True,
    # ~ workers=[list(client.has_what().keys())[0]]
# ~ )
# ~ W2 = client.submit(
    # ~ WorkerProcess,
    # ~ "CPU",
    # ~ actor=True,
    # ~ workers=[list(client.has_what().keys())[1]]
# ~ )














from dask_jobqueue import SLURMCluster
S = SLURMCluster(cores=8, processes=2, memory="16GB", project="myproject", walltime="00:15:00", queue="deb9-gpu", extra=['--resources GPU=1'], job_extra=['--gres=gpu:1'], python="/scisoft/users/paleo/.venv/python35/bin/python")
S.scale(1)
client = Client(S)

from time import sleep
sleep(4)

W1 = client.submit(
    WorkerProcess,
    "GPU",
    actor=True,
    workers=[list(client.has_what().keys())[0]]
)
W2 = client.submit(
    WorkerProcess,
    "CPU",
    actor=True,
    workers=[list(client.has_what().keys())[1]]
)
