import numpy as np
import pytest
from nabu.io.utils import get_compacted_dataslices
from nabu.resources.dataset_analyzer import HDF5DatasetAnalyzer
from nabu.testutils import compare_arrays, __do_long_tests__, get_file
from nabu.io.reader import ChunkReader


@pytest.fixture(scope="class")
def bootstrap(request):
    cls = request.cls

    cls.dataset_fname = get_file("bamboo_reduced.nx")
    cls.tol = 1e-7


def get_compacted_dataslices_as_sorted_tuples(reader):
    slice_to_tuple = lambda s: (s.start, s.stop, s.step)
    data_slices_tuples = list(
        set(
            [
                slice_to_tuple(u.data_slice())
                for u in get_compacted_dataslices(
                    reader.files, subsampling=reader.dataset_subsampling, begin=reader._files_begin_idx
                ).values()
            ]
        )
    )
    return sorted(data_slices_tuples, key=lambda t: t[0])


@pytest.mark.skipif(not (__do_long_tests__), reason="Use __do_long_tests__ for this test")
@pytest.mark.usefixtures("bootstrap")
class TestChunkReader:
    def test_subsampling(self):
        """
        Test reading data from even/odd projections
        """
        dataset_info = HDF5DatasetAnalyzer(self.dataset_fname)

        # Read all projections, then only even-numbered ones, then odd-numbered ones
        # Use the same object to hopefully use less memory (through garbage collection)
        reader = ChunkReader(dataset_info.projections, dataset_subsampling=None)
        reader.load_data()
        first_sino_all = reader.data[:, 0, :].copy()
        compacted_dataslices_all = get_compacted_dataslices_as_sorted_tuples(reader)

        reader = ChunkReader(dataset_info.projections, dataset_subsampling=(2, 0))
        reader.load_data()
        first_sino_even = reader.data[:, 0, :].copy()
        compacted_dataslices_even = get_compacted_dataslices_as_sorted_tuples(reader)

        reader = ChunkReader(dataset_info.projections, dataset_subsampling=(2, 1))
        reader.load_data()
        first_sino_odd = reader.data[:, 0, :].copy()
        compacted_dataslices_odd = get_compacted_dataslices_as_sorted_tuples(reader)

        # Check that the compacted data slices are correct
        assert len(compacted_dataslices_all) == len(compacted_dataslices_even) == len(compacted_dataslices_odd)
        for data_slice_all, data_slice_even, data_slice_odd in zip(
            compacted_dataslices_all, compacted_dataslices_even, compacted_dataslices_odd
        ):
            indices_all = np.arange(100000)[slice(*data_slice_all)]
            indices_even = np.arange(100000)[slice(*data_slice_even)]
            indices_odd = np.arange(100000)[slice(*data_slice_odd)]
            assert indices_all[::2].size == indices_even.size
            assert np.allclose(indices_all[::2], indices_even)
            assert indices_all[1::2].size == indices_odd.size
            assert np.allclose(indices_all[1::2], indices_odd)

        is_close, max_err = compare_arrays(first_sino_all[::2, :], first_sino_even, self.tol, return_residual=True)
        assert is_close, "ChunkReader: something wrong when subsampling for even projections. max_err=%.3e" % max_err
        is_close, max_err = compare_arrays(first_sino_all[1::2, :], first_sino_odd, self.tol, return_residual=True)
        assert is_close, "ChunkReader: something wrong when subsampling for odd projections. max_err=%.3e" % max_err
