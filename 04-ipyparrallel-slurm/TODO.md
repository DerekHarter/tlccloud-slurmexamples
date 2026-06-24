# TODO

- There is an annoying problem with this example currently on the TLC slurm cluster.  The original example
  set ntasks=10, and then calculated the number of workers as ntasks-2, which make sense to get 8 workers and then
  have the controller process and the code execution process, for a total of 10.  The `--ntasks=10` allocation
  to slurm sbatch should work to allow for 10 tasks / cpus to be allocated in the batch job.  However currently
  when run, the 2nd or 3rd srun actually pauses until the first srun completes for some reason.  I initially
  thought we needed to more specifically specify the amount of memory per cpu or other resource to allocate, but
  didn't find a solution doing this.  It does seem that if we allow for more tasks, then the slurm srun subtasks
  allocation will work.  Though I tried an extra 3, 4, 5, 6, 7 up to 10 above the number of worker tasks
  desired, even though we are only starting an addition 2 other processes other than the workers.  
  Using num workers + 10 as the batch ntasks seems to reliably work.  Somewhat more puzzling, some of the
  intermediate values, like ntasks + 5 or ntasks + 6 seem to work sometimes but not others (even though 
  have been essentially testing on an empty cluster so there shouldn't be any other competing jobs).
  I would have expected this number of buffer tasks to be deterministic and the same each time, if it is in
  fact some limit on the number of allocated cpu / task slots for the batch job.  Need to determine how to
  get more logging information from the slurm scheduler / batcher on why it delays the 2nd or 3rd srun.

- Update tal of the strings to use the new python formatted strings, instead of a mix of old style string formatting.