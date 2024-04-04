from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, wait
from abc import ABC, abstractmethod


class Processor(ABC):
  """
  Processor class use multi-processing to process inputs.
  """

  @abstractmethod
  def _process(self, inputs, *args, **kwds):
    """
    Process inputs.
    :param inputs:  inputs to be processed.
    :param args:    additional arguments.
    :param kwds:    additional keyword arguments.
    :return:        processed outputs.
    """
    raise NotImplemented()

  def _batch_process(self, inputs, batch, thread, *args, **kwds):
    """
    Process inputs in parallel.
    :param inputs:  inputs to be processed.
    :param batch:   number of parallel process/threads.
    :param thread:  using thread or cpu process.
    :param args:    additional arguments.
    :param kwds:    additional keyword arguments.
    :return:        processed outputs.
    """
    if isinstance(inputs, list):
      jobs = list()
      with ThreadPoolExecutor(batch) if thread else ProcessPoolExecutor(batch) as executor:
        for x in inputs:
          futures = executor.submit(self._process, x, *args, **kwds)
          jobs.append(futures)
        wait(jobs)
      return [x.result() for x in jobs]
    else:
      return self._process(inputs, *args, **kwds)

  def __call__(self, inputs, batch: int = None, thread: bool = False, *args, **kwds):
    """
    Process inputs in single or parallel.
    :param inputs:  inputs to be processed.
    :param batch:   number of parallel process/threads.
    :param thread:  using thread or cpu process.
    :param args:    additional arguments.
    :param kwds:    additional keyword arguments.
    :return:        processed outputs.
    """
    if batch == 1:
      return self._process(self, inputs, *args, **kwds)
    else:
      return self._batch_process(inputs, batch, thread, *args, **kwds)
