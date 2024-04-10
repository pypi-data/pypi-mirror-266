from os import getpid
from time import sleep
from multiprocessing import Process
import sys

from silx.gui import qt
from nabu.resources.processconfig import ProcessConfig

from nabu.app.fullfield_cuda import CudaFullFieldPipeline


"""
Idéalement, on ne crée qu'une seule fois un objet "CudaFullFieldPipeline".
Ca engendrerait moins de problèmes de création/suppression de contextes.
Pour ce faire :
  - Créer cet objet dans OuterThread, et partager avec InnerThread.
    Par sûr que ça marche avec les QThread
  - Créer un InnerThread persistant (donc un objet CudaFullFieldPipeline persistant)
    qui agit comme un serveur : OuterThread envoie des messages de reconstruction
    (ex. queue). Là encore, pas sûr qu'on puisse utiliser ça avec QThread

Pour tomwer, le nombre de slices à reconstruire est variable !
Donc dans tous les cas, certainement on détruit InnerThread
"""


# This thread always use the same FullFieldPipeline instance
class InnerThread1(qt.QThread):

    def __init__(self, proc, subregion, **kwargs):
        super().__init__(**kwargs)
        self.pipeline = CudaFullFieldPipeline(
            proc, subregion, cuda_options={"cleanup_at_exit": False}
        )

    def run(self, subregion):
        print("In Inner QThread v1")
        self.pipeline.process_chunk(sub_region=subregion)
        print("End Inner QThread v1")

    def __del__(self):
        print("Inner QThread v1 being destroyed. Deleting cuda context")
        self.pipeline.ctx.pop()


# This thread creates a new FullFieldPipeline object each time
class InnerThread2(qt.QThread):

    def __init__(self, fname, subregion, **kwargs):
        super().__init__(**kwargs)
        self.proc = ProcessConfig(fname)
        self.subregion = subregion
        self.pipeline = CudaFullFieldPipeline(
            self.proc, self.subregion, cuda_options={"cleanup_at_exit": False}
        )

    def run(self):
        print("In Inner QThread v2")
        # necessary if CudaFullFieldPipeline was created in __init__
        self.pipeline.ctx.push()
        #
        self.pipeline.process_chunk()
        print("End Inner QThread v2")
        self.pipeline.ctx.pop()
        del self.pipeline
        sleep(1)

    # ~ def __del__(self):
        # ~ self.pipeline.ctx.pop()
        # ~ print("Destroying Inner QThread v2 - deleting cuda context")


# Thread calling InnerThread1
class OuterThread(qt.QThread):

    def __init__(self, fname, **kwargs):
        super().__init__(**kwargs)
        self.fname = fname

    def run(self):
        fname = self.fname
        print("In Outer QThread")
        I = InnerThread2(fname, (100, 150))
        I.start()
        I.wait()
        print("End Outer Qthread")
        sleep(1)
        del I
        sleep(1)
        # ~ print("Launching a second time")
        # ~ I = InnerThread2(fname, (150, 200))
        # ~ I.start()
        # ~ I.wait()
        # ~ print("End second time")

        # ~ print("Launching a third time")
        # ~ I = InnerThread2(fname, (200, 250))
        # ~ I.start()
        # ~ I.wait()
        # ~ print("End third time")



if __name__ == "__main__":

    fname = "/scratch/paleo/bamboo/nabu.conf"

    T = OuterThread(fname)
    T.start()
    T.wait()





class Pipeline:
    def __init__(self, fname, subregion):
        self.proc = ProcessConfig(fname)
        # ~ self.proc.processing_steps.remove("save")
        self.pipeline = CudaFullFieldPipeline(self.proc, subregion)

    def process_chunk(self, sub_region=None):
        self.pipeline.ctx.push() #
        self.pipeline.process_chunk(sub_region=sub_region)
        # ~ self.pipeline.recs = self.pipeline._d_recs # if no "save"








