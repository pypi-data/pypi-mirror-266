from datetime import datetime
from logging import getLogger
from pathlib import Path

import numpy as np
import pandas as pd
from click import command

from .compare import format_exp_count_col
from .csv import get_count_path
from .data import ClusterMutsDataset
from .data import load_cluster_dataset
from .io import ClusterBatchIO
from .names import BIT_VECTOR_NAME, LOG_OBS_NAME
from .report import ClusterReport
from ..core import path
from ..core.arg import (CMD_DELCLUST,
                        docdef,
                        arg_input_path,
                        opt_max_clusters,
                        opt_brotli_level,
                        opt_parallel,
                        opt_max_procs)
from ..core.parallel import as_list_of_tuples, dispatch
from ..core.report import (calc_dt_minutes,
                           Field,
                           ChecksumsF,
                           TimeBeganF,
                           TimeTakenF,
                           MaxClustsF,
                           ClustNumRunsF,
                           MinIterClustF,
                           MaxIterClustF,
                           ClustConvThreshF,
                           NumUniqReadKeptF,
                           ClustsConvF,
                           ClustsLogLikesF,
                           ClustsRMSDsF,
                           ClustsMeanRsF,
                           ClustsBicF,
                           NumClustsF)

logger = getLogger(__name__)

BTYPE = ClusterBatchIO.btype()


def update_log_counts(best_order: int,
                      top: Path,
                      sample: str,
                      ref: str,
                      sect: str):
    """ Update the expected log counts of unique bit vectors. """
    if best_order < 1:
        raise ValueError(f"Best order must be ≥ 1, but got {best_order}")
    # Build the path for the output file.
    file = get_count_path(top, sample, ref, sect)
    # Load the existing counts.
    original_log_counts = pd.read_csv(file, index_col=BIT_VECTOR_NAME)
    # Copy the observed counts.
    new_log_counts = original_log_counts[LOG_OBS_NAME].to_frame()
    # Copy the expected counts for the orders up to max_order.
    for order in range(1, best_order + 1):
        col = format_exp_count_col(order)
        new_log_counts[col] = original_log_counts[col]
    # Write the updated log counts to the file.
    new_log_counts.to_csv(file)
    return file


def update_batches(dataset: ClusterMutsDataset,
                   best_order: int,
                   brotli_level: int):
    """ Update the cluster memberships in batches. """
    if best_order < 1:
        raise ValueError(f"Best order must be ≥ 1, but got {best_order}")
    orders = np.arange(1, best_order + 1)
    checksums = list()
    for original_batch in dataset.iter_batches():
        new_batch = ClusterBatchIO(sample=dataset.sample,
                                   ref=dataset.ref,
                                   sect=dataset.sect,
                                   batch=original_batch.batch,
                                   resps=original_batch.membership.loc[:, orders])
        _, checksum = new_batch.save(top=dataset.top,
                                     brotli_level=brotli_level,
                                     force=True)
        checksums.append(checksum)
    return checksums


def update_field(report: ClusterReport, field: Field, best_order: int):
    """ Delete clusters from a field of a report. """
    if best_order < 1:
        raise ValueError(f"Best order must be ≥ 1, but got {best_order}")
    original = report.get_field(field)
    if not isinstance(original, dict):
        raise TypeError(f"Expected dict, but got {type(original).__name__}")
    return {order: original[order] for order in range(1, best_order + 1)}


def update_report(original_report: ClusterReport,
                  max_order: int,
                  best_order: int,
                  checksums: list[str],
                  began: datetime,
                  ended: datetime,
                  top: Path):
    if max_order < 1:
        raise ValueError(f"Maximum order must be ≥ 1, but got {max_order}")
    new_report = ClusterReport(
        sample=original_report.sample,
        ref=original_report.ref,
        sect=original_report.sect,
        n_uniq_reads=original_report.get_field(NumUniqReadKeptF),
        max_order=max_order,
        num_runs=original_report.get_field(ClustNumRunsF),
        min_iter=original_report.get_field(MinIterClustF),
        max_iter=original_report.get_field(MaxIterClustF),
        conv_thresh=original_report.get_field(ClustConvThreshF),
        checksums={BTYPE: checksums},
        n_batches=len(checksums),
        converged=update_field(original_report,
                               ClustsConvF,
                               best_order),
        log_likes=update_field(original_report,
                               ClustsLogLikesF,
                               best_order),
        clusts_rmsds=update_field(original_report,
                                  ClustsRMSDsF,
                                  best_order),
        clusts_meanr=update_field(original_report,
                                  ClustsMeanRsF,
                                  best_order),
        bic=update_field(original_report,
                         ClustsBicF,
                         best_order),
        best_order=best_order,
        began=original_report.get_field(TimeBeganF),
        ended=ended,
        taken=(original_report.get_field(TimeTakenF)
               + calc_dt_minutes(began, ended)),
    )
    new_report.save(top, force=True)
    return new_report


def del_orders(report_file: Path,
               max_order: int, *,
               brotli_level: int):
    """ Delete orders from an existing report and dataset. """
    if max_order < 1:
        raise ValueError(f"Maximum order must be ≥ 1, but got {max_order}")
    # Load the original cluster report.
    report = ClusterReport.load(report_file)
    original_max_order = report.get_field(MaxClustsF)
    if max_order < original_max_order:
        began = datetime.now()
        logger.info(f"Began deleting clusters from {report_file} down to "
                    f"order {max_order}")
        dataset = load_cluster_dataset(report_file)
        original_best_order = report.get_field(NumClustsF)
        if max_order < original_best_order:
            # Delete all orders greater than max_order.
            best_order = max_order
            update_log_counts(best_order,
                              top=dataset.top,
                              sample=dataset.sample,
                              ref=dataset.ref,
                              sect=dataset.sect)
            checksums = update_batches(dataset,
                                       best_order,
                                       brotli_level)
        else:
            # There is nothing to delete.
            best_order = original_best_order
            checksums = report.get_field(ChecksumsF)[BTYPE]
        ended = datetime.now()
        update_report(report,
                      max_order,
                      best_order,
                      checksums,
                      began,
                      ended,
                      dataset.top)
        logger.info(f"Ended deleting clusters from {report_file} down to "
                    f"order {max_order}")
    else:
        logger.warning(f"New maximum order ({max_order}) is not less than "
                       f"original ({original_max_order}): nothing to delete")
    return report_file


@docdef.auto()
def run(input_path: tuple[str, ...], *,
        max_clusters: int,
        brotli_level: int,
        max_procs: int,
        parallel: bool) -> list[Path]:
    """ Delete clusters from a dataset that was already clustered. """
    if max_clusters < 1:
        logger.warning(f"Maximum order must be ≥ 1, but got {max_clusters}")
        return list()
    # Find the cluster report files.
    report_files = path.find_files_chain(
        input_path, load_cluster_dataset.report_path_seg_types
    )
    # Cluster each mask dataset.
    return dispatch(del_orders,
                    max_procs,
                    parallel,
                    pass_n_procs=False,
                    args=as_list_of_tuples(report_files),
                    kwargs=dict(max_order=max_clusters,
                                brotli_level=brotli_level))


params = [
    # Input files
    arg_input_path,
    # Clustering options
    opt_max_clusters,
    # Compression
    opt_brotli_level,
    # Parallelization
    opt_max_procs,
    opt_parallel,
]


@command(CMD_DELCLUST, params=params)
def cli(*args, **kwargs):
    """ Delete clusters from a dataset that was already clustered. """
    return run(*args, **kwargs)

########################################################################
#                                                                      #
# © Copyright 2024, the Rouskin Lab.                                   #
#                                                                      #
# This file is part of SEISMIC-RNA.                                    #
#                                                                      #
# SEISMIC-RNA is free software; you can redistribute it and/or modify  #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation; either version 3 of the License, or    #
# (at your option) any later version.                                  #
#                                                                      #
# SEISMIC-RNA is distributed in the hope that it will be useful, but   #
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANT- #
# ABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General     #
# Public License for more details.                                     #
#                                                                      #
# You should have received a copy of the GNU General Public License    #
# along with SEISMIC-RNA; if not, see <https://www.gnu.org/licenses>.  #
#                                                                      #
########################################################################
