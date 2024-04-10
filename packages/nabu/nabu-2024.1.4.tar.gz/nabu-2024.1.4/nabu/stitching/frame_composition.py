from copy import copy
from dataclasses import dataclass
import numpy
from math import ceil

from nabu.stitching.overlap import ZStichOverlapKernel


@dataclass
class _FrameCompositionBase:
    def compose(self, output_frame: numpy.ndarray, input_frames: tuple):
        raise NotImplementedError("Base class")


@dataclass
class ZFrameComposition(_FrameCompositionBase):
    """
    class used to define intervals to know where to dump raw data or stitched data according to requested policy.
    The idea is to create this once for all for one stitching operation and reuse it for each frame.
    """

    local_start_y: tuple
    local_end_y: tuple
    global_start_y: tuple
    global_end_y: tuple

    def browse(self):
        for i in range(len(self.local_start_y)):
            yield (
                self.local_start_y[i],
                self.local_end_y[i],
                self.global_start_y[i],
                self.global_end_y[i],
            )

    def compose(self, output_frame: numpy.ndarray, input_frames: tuple):
        if not output_frame.ndim in (2, 3):
            raise TypeError(
                f"output_frame is expected to be 2D (gray scale) or 3D (RGB(A)) and not {output_frame.ndim}"
            )
        for (
            global_start_y,
            global_end_y,
            local_start_y,
            local_end_y,
            input_frame,
        ) in zip(
            self.global_start_y,
            self.global_end_y,
            self.local_start_y,
            self.local_end_y,
            input_frames,
        ):
            if input_frame is not None:
                output_frame[global_start_y:global_end_y] = input_frame[local_start_y:local_end_y]

    @staticmethod
    def compute_raw_frame_compositions(frames: tuple, key_lines: tuple, overlap_kernels: tuple, stitching_axis):
        """
        compute frame composition for raw data

        warning: we expect frames to be ordered y downward and the frame order to keep this ordering
        """
        assert len(frames) == len(overlap_kernels) + 1 == len(key_lines) + 1

        global_start_ys = [0]

        # extend shifts and kernels to have a first shift of 0 and two overlaps values at 0 to
        # generalize processing
        local_start_ys = [0]

        local_start_ys.extend(
            [ceil(key_line[1] + kernel.overlap_size / 2) for (key_line, kernel) in zip(key_lines, overlap_kernels)]
        )
        local_end_ys = list(
            [ceil(key_line[0] - kernel.overlap_size / 2) for (key_line, kernel) in zip(key_lines, overlap_kernels)]
        )
        local_end_ys.append(frames[-1].shape[stitching_axis])

        for (
            new_local_start_y,
            new_local_end_y,
            kernel,
        ) in zip(local_start_ys, local_end_ys, overlap_kernels):
            global_start_ys.append(global_start_ys[-1] + (new_local_end_y - new_local_start_y) + kernel.overlap_size)

        # global end can be easily found from global start + local start and end
        global_end_ys = []
        for global_start_y, new_local_start_y, new_local_end_y in zip(global_start_ys, local_start_ys, local_end_ys):
            global_end_ys.append(global_start_y + new_local_end_y - new_local_start_y)

        return ZFrameComposition(
            local_start_y=tuple(local_start_ys),
            local_end_y=tuple(local_end_ys),
            global_start_y=tuple(global_start_ys),
            global_end_y=tuple(global_end_ys),
        )

    @staticmethod
    def compute_stitch_frame_composition(frames, key_lines: tuple, overlap_kernels: tuple, stitching_axis: int):
        """
        compute frame composition for stiching.
        """
        assert len(frames) == len(overlap_kernels) + 1 == len(key_lines) + 1
        assert stitching_axis in (0, 1, 2)

        # position in the stitched frame;
        local_start_ys = [0] * len(overlap_kernels)
        local_end_ys = [kernel.overlap_size for kernel in overlap_kernels]

        # position in the global frame. For this one it is simpler to rely on the raw frame composition
        composition_raw = ZFrameComposition.compute_raw_frame_compositions(
            frames=frames,
            key_lines=key_lines,
            overlap_kernels=overlap_kernels,
            stitching_axis=stitching_axis,
        )
        global_start_ys = composition_raw.global_end_y[:-1]
        global_end_ys = composition_raw.global_start_y[1:]

        return ZFrameComposition(
            local_start_y=tuple(local_start_ys),
            local_end_y=tuple(local_end_ys),
            global_start_y=tuple(global_start_ys),
            global_end_y=tuple(global_end_ys),
        )

    @staticmethod
    def pprint_z_stitching(raw_composition, stitch_composition):
        """
        util to display what the output of the z stitch will looks like from composition
        """
        for i_frame, (raw_comp, stitch_comp) in enumerate(zip(raw_composition.browse(), stitch_composition.browse())):
            raw_local_start, raw_local_end, raw_global_start, raw_global_end = raw_comp

            print(
                f"stitch_frame[{raw_global_start}:{raw_global_end}] = frame_{i_frame}[{raw_local_start}:{raw_local_end}]"
            )

            (
                stitch_local_start,
                stitch_local_end,
                stitch_global_start,
                stitch_global_end,
            ) = stitch_comp

            print(
                f"stitch_frame[{stitch_global_start}:{stitch_global_end}] = stitched_frame_{i_frame}[{stitch_local_start}:{stitch_local_end}]"
            )
        else:
            i_frame += 1
            raw_local_start, raw_local_end, raw_global_start, raw_global_end = list(raw_composition.browse())[-1]
            print(
                f"stitch_frame[{raw_global_start}:{raw_global_end}] = frame_{i_frame}[{raw_local_start}:{raw_local_end}]"
            )
