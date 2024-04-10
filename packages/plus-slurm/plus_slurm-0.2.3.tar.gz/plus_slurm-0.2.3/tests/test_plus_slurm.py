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

import sys
import os
import plus_slurm
import itertools
import pytest
from .job_package.jobs import (JobWithArgs, JobWithThreeArgs, JobChangesArgs,
                               JobWithAutoFilename, ApptainerJob)

def trim_outfile(file_content):
    out_lines = list()
    start_seen = False

    for line in file_content.split('\n'):
        if line == '##########':
            start_seen = not start_seen
            if not start_seen:
                break
        elif start_seen:
            out_lines.append(line)

    return '\n'.join(out_lines) + '\n'


class LocalJob(plus_slurm.Job):
    def run(self):
        print('I am a local job without arguments')

def test_local():
    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(LocalJob)
    job_cluster.run_local()

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == 'I am a local job without arguments\n'

def test_local_in_package():
    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(JobWithArgs, 'Hello World!')
    job_cluster.run_local()

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == 'Hello World!\n'

def test_local_multiple():
    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(LocalJob)
    job_cluster.add_job(JobWithArgs, 'Hello World!')
    job_cluster.run_local()

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == 'I am a local job without arguments\n'

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_2.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == 'Hello World!\n'

def test_local_multiargs():
    (first, second, third) = ('One', 'Two', 'Four')

    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(JobWithThreeArgs, first, second, third)
    job_cluster.run_local()

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
        assert trim_outfile(out_file.read()) == ('first: %s\n'
              'second: %s\n'
              'third: %s\n' % (str(first), str(second), str(third)))


def test_local_permute_args():
    second_raw = ('Two', 'AlsoTwo')
    third_raw = ('Four', 'OtherFour')

    (first, second, third) = ('One', plus_slurm.PermuteArgument(second_raw), plus_slurm.PermuteArgument(third_raw))

    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(JobWithThreeArgs, first, second, third)
    job_cluster.run_local()

    all_perms = itertools.product(second_raw, third_raw)

    all_expected_outputs = list()
    for cur_perm in all_perms:
        this_second = cur_perm[0]
        this_third = cur_perm[1]

        all_expected_outputs.append('first: %s\n'
                                    'second: %s\n'
                                    'third: %s\n' % (str(first), str(this_second), str(this_third)))

    actual_output_list = list()
    for idx in range(job_cluster.n_jobs_submitted):
        with open(os.path.join(job_cluster.output_folder, 'log', 'out_%d.log' % (idx + 1,)), 'rt') as out_file:
            actual_output_list.append(trim_outfile(out_file.read()))

    assert all_expected_outputs == actual_output_list

def test_local_permute_kwargs():
    second_raw = ('Two', 'AlsoTwo')
    third_raw = ('Four', 'OtherFour')

    (first, second, third) = ('One', plus_slurm.PermuteArgument(second_raw), plus_slurm.PermuteArgument(third_raw))

    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(JobWithThreeArgs, first, third=third, second=second)
    job_cluster.run_local()

    all_perms = itertools.product(second_raw, third_raw)

    all_expected_outputs = list()
    for cur_perm in all_perms:
        this_second = cur_perm[0]
        this_third = cur_perm[1]

        all_expected_outputs.append('first: %s\n'
                                    'second: %s\n'
                                    'third: %s\n' % (str(first), str(this_second), str(this_third)))

    actual_output_list = list()
    for idx in range(job_cluster.n_jobs_submitted):
        with open(os.path.join(job_cluster.output_folder, 'log', 'out_%d.log' % (idx + 1,)), 'rt') as out_file:
            actual_output_list.append(trim_outfile(out_file.read()))

    assert sorted(all_expected_outputs) == sorted(actual_output_list)

def test_local_permute_args_and_kwargs():
    second_raw = ('Two', 'AlsoTwo')
    third_raw = ('Four', 'OtherFour')

    (first, second, third) = ('One', plus_slurm.PermuteArgument(second_raw), plus_slurm.PermuteArgument(third_raw))

    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable)
    job_cluster.add_job(JobWithThreeArgs, first, second, third=third)
    job_cluster.run_local()

    all_perms = itertools.product(second_raw, third_raw)

    all_expected_outputs = list()
    for cur_perm in all_perms:
        this_second = cur_perm[0]
        this_third = cur_perm[1]

        all_expected_outputs.append('first: %s\n'
                                    'second: %s\n'
                                    'third: %s\n' % (str(first), str(this_second), str(this_third)))

    actual_output_list = list()
    for idx in range(job_cluster.n_jobs_submitted):
        with open(os.path.join(job_cluster.output_folder, 'log', 'out_%d.log' % (idx + 1,)), 'rt') as out_file:
            actual_output_list.append(trim_outfile(out_file.read()))

    assert sorted(all_expected_outputs) == sorted(actual_output_list)


def test_run_cannot_change_args_and_kwargs():
    job = JobChangesArgs(['test'],
                         kwarg_list=['kwarg_test'])

    job.run_private()

    assert 'hi' not in job._args[0]
    assert 'hello' not in list(job._kwargs.values())[0]


def test_autofilename():
    job = JobWithAutoFilename(subject_id='subject',
                              included_arg='hello',
                              excluded_arg='bad')

    f_name = job.full_output_path

    assert str(f_name) == '/base/job/subject/subject__included_arg_hello__d4fb2255c2.dat'


@pytest.mark.no_ci
def test_apptainer():
    job_cluster = plus_slurm.ApptainerJobCluster(apptainer_image='oras://ghcr.io/thht/obob-singularity-container/xfce_desktop:latest',
                                                 mount_slurm_folders=False)

    job_cluster.add_job(ApptainerJob)

    job_cluster.run_local()

    with open(os.path.join(job_cluster.output_folder, 'log', 'out_1.log'), 'rt') as out_file:
            assert 'APPTAINER_NAME' in trim_outfile(out_file.read())


def test_sharding(tmp_path):

    job_cluster = plus_slurm.JobCluster(python_bin=sys.executable,
                                        jobs_dir=tmp_path,
                                        max_jobs_per_jobcluster=2)

    job_cluster.add_job(JobWithArgs,
                        my_arg=plus_slurm.PermuteArgument((1, 2, 3, 4)))

    job_cluster.submit(do_submit=False)

    assert len(list(tmp_path.glob('*'))) == 2


def test_extra_slurm_args():
    job_cluster = plus_slurm.JobCluster(extra_slurm_args=['--partition=bla', '--blabla'])
    job_cluster.add_job(LocalJob)

    job_cluster.submit(do_submit=False)
    with open(os.path.join(job_cluster.output_folder, 'slurm', 'submit.sh'), 'rt') as out_file:
        content = out_file.read()
        assert '#SBATCH --partition=bla' in content
        assert '#SBATCH --blabla' in content
    