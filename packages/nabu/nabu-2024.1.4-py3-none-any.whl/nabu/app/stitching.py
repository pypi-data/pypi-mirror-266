import logging
from nabu.utils import Progress
from nabu.stitching.slurm_utils import split_stitching_configuration_to_slurm_job
from .cli_configs import StitchingConfig
from ..pipeline.config import parse_nabu_config_file
from nabu.stitching.z_stitching import (
    z_stitching,
    StitchingPostProcAggregation,
)
from nabu.stitching.config import dict_to_config_obj
from .utils import parse_params_values

try:
    from sluurp.executor import submit
except ImportError:
    has_sluurp = False
else:
    has_sluurp = True

_logger = logging.getLogger(__name__)


def main():
    args = parse_params_values(
        StitchingConfig,
        parser_description="Run stitching from a configuration file. Configuration can be obtain from `stitching-config`",
    )
    logging.basicConfig(level=args["loglevel"].upper())

    conf_dict = parse_nabu_config_file(args["input-file"], allow_no_value=True)

    stitching_config = dict_to_config_obj(conf_dict)
    stitching_config.settle_inputs()
    if args["only_create_master_file"]:
        # option to ease creation of the master in the following cases:
        # * user has submitted all the job but has been quicked out of the cluster
        # * only a few slurm job for some random version (cluster update...) and user want to retriger only those job and process the aggragation only. On those cases no need to redo it all.
        tomo_objs = []
        for _, sub_config in split_stitching_configuration_to_slurm_job(stitching_config, yield_configuration=True):
            tomo_objs.append(sub_config.get_output_object().get_identifier().to_str())

        post_processing = StitchingPostProcAggregation(
            existing_objs_ids=tomo_objs,
            stitching_config=stitching_config,
        )
        post_processing.process()

    elif stitching_config.slurm_config.partition in (None, ""):
        # case 1: run locally
        _logger.info(f"run stitching locally with {stitching_config}")

        progress = Progress("z-stitching")
        progress.set_name("initialize z-stitching")
        progress.set_advancement(0)
        z_stitching(stitching_config, progress=progress)
    else:
        if not has_sluurp:
            raise ImportError(
                "sluurp not install. Please install it to distribute stitching on slurm (pip install sluurm)"
            )
        # case 2: run on slurm
        # note: to speed up we could do shift research on pre processing and run it only once (if manual of course). Here it will be run for all part
        _logger.info(f"will distribute stitching")

        futures = {}
        # 2.1 launch jobs
        for i_job, (job, sub_config) in enumerate(
            split_stitching_configuration_to_slurm_job(stitching_config, yield_configuration=True)
        ):
            _logger.info(f"submit job nb {i_job}: handles {sub_config.slices}")
            output_volume = sub_config.get_output_object().get_identifier().to_str()
            futures[output_volume] = submit(job, timeout=999999)

        # 2.2 wait for future to be done and concatenate the result
        post_processing = StitchingPostProcAggregation(
            futures=futures,
            stitching_config=stitching_config,
        )
        post_processing.process()

    exit(0)


if __name__ == "__main__":
    main()
