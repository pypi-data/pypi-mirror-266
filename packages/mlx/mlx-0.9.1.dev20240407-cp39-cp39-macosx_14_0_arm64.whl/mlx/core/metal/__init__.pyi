

def get_active_memory() -> int:
    """
    Get the actively used memory in bytes.

    Note, this will not always match memory use reported by the system because
    it does not include cached memory buffers.
    """

def get_cache_memory() -> int:
    """
    Get the cache size in bytes.

    The cache includes memory not currently used that has not been returned
    to the system allocator.
    """

def get_peak_memory() -> int:
    """
    Get the peak amount of used memory in bytes.

    The maximum memory used is recorded from the beginning of the program
    execution.
    """

def is_available() -> bool:
    """Check if the Metal back-end is available."""

def set_cache_limit(limit: int) -> int:
    """
    Set the free cache limit.

    If using more than the given limit, free memory will be reclaimed
    from the cache on the next allocation. To disable the cache, set
    the limit to ``0``.

    The cache limit defaults to the memory limit. See
    :func:`set_memory_limit` for more details.

    Args:
      limit (int): The cache limit in bytes.

    Returns:
      int: The previous cache limit in bytes.
    """

def set_memory_limit(limit: int, *, relaxed: bool = True) -> int:
    """
    Set the memory limit.

    Memory allocations will wait on scheduled tasks to complete if the limit
    is exceeded. If there are no more scheduled tasks an error will be raised
    if ``relaxed`` is ``False``. Otherwise memory will be allocated
    (including the potential for swap) if ``relaxed`` is ``True``.

    The memory limit defaults to 1.5 times the maximum recommended working set
    size reported by the device.

    Args:
      limit (int): Memory limit in bytes.
      relaxed (bool, optional): If `False`` an error is raised if the limit
        is exceeded. Default: ``True``

    Returns:
      int: The previous memory limit in bytes.
    """
