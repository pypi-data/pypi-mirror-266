from time import time
from threading import Thread
import numpy as np
from tomoscan.io import HDF5File

class Processor:
    def __init__(self, size=8000):
        self.A = np.random.rand(size, size).astype("f")
        self._cnt = 0


    def process(self):
        print("Processing %d..." % self._cnt)
        t0 = time()
        _ = self.A.T.dot(self.A)
        el = time() - t0
        print("process OK in %.2f s" % el)
        self._cnt += 1




class Reader:
    def __init__(self, fname, h5path, start_z=None, end_z=None):
        self.fname = fname
        self.h5path = h5path
        self.set_subregion(start_z, end_z)


    def set_subregion(self, start_z, end_z):
        self.start_z = start_z
        self.end_z = end_z


    def read(self):
        print("Reading (%d, %d)..." % (self.start_z, self.end_z))
        t0 = time()
        with HDF5File(self.fname, "r") as f:
            d = f[self.h5path][:, self.start_z:self.end_z, :]
        el = time() - t0
        print(
            "Read (%d, %d) in %.2f s"
            % (self.start_z, self.end_z, el)
        )
        return d


if __name__ == "__main__":
    fname = "/data/scisofttmp/tomo_datasets/rock/sample_0002_1_1.nx"
    h5path = "entry0000/instrument/detector/data"
    R = Reader(fname, h5path, start_z=0, end_z=100)

    P = Processor()

    reader_thread = Thread(target=R.read)
    reader_thread.start()

    P.process()



def interleaved_read_proc(fname, h5path, n_steps, chunk_size=100):

    R = Reader(fname, h5path, start_z=0, end_z=chunk_size)
    P = Processor(size=5000)

    def read_in_thread(start_z, end_z):
        R.set_subregion(start_z, end_z)
        reader_thread = Thread(target=R.read)
        reader_thread.start()
        return reader_thread

    def wait_for_available_data(reader_thread):
        print("[Processor] waiting for available data...")
        reader_thread.join()
        print("[Processor] OK!")

    t0 = time()

    reader_thread = read_in_thread(0, chunk_size)

    for i in range(1, n_steps+1):
        wait_for_available_data(reader_thread)
        # transfer R -> P
        reader_thread = read_in_thread(i * chunk_size, (i + 1) * chunk_size)
        P.process()

    el = time() - t0
    print("Total time: %.3fs" % el)



"""
Independently:
  - read: 12.3s
  - process: 19.3

In parallel:
  - read: 14.3
  - process: 20.7



[Read][T][Proces][Read][T][Process][Read][T][Process][Read][T][Process]

[Read][T][Process][T][Process][T][Process][T][Process]
         [Read]......[Read]......[Read]......[Read]




[Read][T][Process][Save][Read][T][Process][Save][Read][T][Process][Save][Read][T][Process][Save]


[Read][T][Process]......[T][Process][T][Process][T][Process]
         [Read]......[Read]......[Read]......[Read]
                  [Save]











"""