# -*- coding: UTF-8 -*-
# Copyright (c) 2018, Thomas Hartmann
#
# This file is part of the plus_slurm Project, see: https://gitlab.com/thht/plus-slurm
#
#    plus_slurm is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    plus_slurm is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with obob_subjectdb. If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent / 'nested_folder'))

from plus_slurm import JobCluster
from nested_job_package.jobs import NestedJob
from .test_plus_slurm import trim_outfile


def test_nested():
    job_cluster = JobCluster(python_bin=sys.executable, append_to_path=str(Path(__file__).parent / 'nested_folder'))
    job_cluster.add_job(NestedJob)
    job_cluster.run_local()

    with open(Path(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == 'Nested Job ran.\n'