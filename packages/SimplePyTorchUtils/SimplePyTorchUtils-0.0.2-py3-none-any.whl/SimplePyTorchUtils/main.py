import gc
import torch
import random
import numpy as np


def clear_torch_cache():
    """
    Clears the cache of PyTorch tensors allocated on GPU.

    This function performs the following steps:
    1. Collects garbage to release memory that is no longer in use.
    2. Empties the CUDA memory cache to release cached memory.
    3. Collects and releases CUDA Inter-Process Communication (IPC) memory.
    4. Allocates a dummy tensor on CUDA device to trigger memory release.
    5. Deletes the dummy tensor to free its memory allocation.
    6. Empties the CUDA memory cache again to release any remaining cached memory.

    Note:
    It's useful to call this function periodically to avoid memory fragmentation and ensure efficient memory utilization when working with PyTorch on GPU.

    References:
    - PyTorch memory management documentation
    - CUDA memory management documentation

    Returns:
    None
    """
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()
    dummy_tensor = torch.rand(1, 1).to(torch.device("cuda"))
    del dummy_tensor
    torch.cuda.empty_cache()


def truncate(inputs_ids: torch.Tensor, max_size: int):
    """Truncates a torch tensor to the given max_size

    Args:
        inputs_ids (torch.Tensor): The torch array
        max_size (int): The max_size of the array.

    Returns:
        Tensor: Truncated tensor
    """

    max_size = abs(int(max_size))
    if max_size:
        return inputs_ids[:, -abs(int(max_size)) :]
    return inputs_ids


def _join_tensors(tensor_a: torch.Tensor, tensor_b: torch.Tensor, dim: int):
    """Internal function, please use 'join_tensors' instead!"""
    try:
        results = None
        if isinstance(tensor_a, torch.Tensor) and isinstance(tensor_b, torch.Tensor):
            results = torch.cat((tensor_a, tensor_b), dim=dim)
        elif isinstance(tensor_b, torch.Tensor):
            results = tensor_b
        return results
    except:
        return None


def join_tensors(*args, dim: int = 1, truncation_lenght: int = 0):
    """
    Concatenates multiple token tensors along a specified dimension and truncates the result if necessary.

    Parameters:
        *args (Tensor): Tensors to concatenate.
        dim (int, optional): The dimension along which to concatenate the tensors. Defaults to 1.
        truncation_lenght (int, optional): The maximum length to truncate the concatenated tensor to. Defaults to 0 (no truncation).

    Returns:
        Tensor: Concatenated tensor, possibly truncated.
    """
    results = None
    if args:
        for x in args:
            if isinstance(x, torch.Tensor):
                _res = _join_tensors(results, x, dim)
                if isinstance(_res, torch.Tensor):
                    results = _res
            elif isinstance(x, (list, tuple)):
                results = join_tensors(x, dim=dim)
        # Truncation just as a final process, in sub-loops it wont truncate to save time.
        if truncation_lenght:
            return results[:, -abs(int(truncation_lenght)) :]
    return results


def _join_arrays(array_a: np.ndarray | None, array_b: np.ndarray, axis: int):
    """Internal function, please use join_arrays instead!"""
    try:
        if isinstance(array_a, np.ndarray) and isinstance(array_b, np.ndarray):
            return np.concatenate((array_a, array_b), axis=axis)
        elif isinstance(array_b, np.ndarray):
            return array_b
    except:
        return None


def join_arrays(*args, axis: int = 0):
    """
    Concatenates multiple NumPy arrays along a specified axis.

    Parameters:
        *args (ndarray | list[ndarray] | tuple[ndarray, ...]): Arrays to concatenate.
        axis (int, optional): The axis along which to concatenate the arrays. Defaults to 0.

    Returns:
        ndarray: Concatenated array.
    """
    results = None
    if args:
        for x in args:
            if isinstance(x, np.ndarray):
                _res = _join_arrays(results, x, axis)
                if isinstance(_res, np.ndarray):
                    results = _res
            elif isinstance(x, (list, tuple)):
                results = join_arrays(x)
    return results


class SeedContext:
    """
    Context manager for controlling the randomness and seed during generation.

    Parameters:
        seed (int): The seed to be used for random number generation.
        min_seed (int): The minimum value for a random seed (default is 0).
        default_seed (int): The default seed, triggering automatic randomization if used (default is -1).
    Attributes:
        is_deterministic (bool): True if the context is in deterministic mode, False otherwise.
        seed (int): The seed being used for random number generation.
        original_seed (tuple): Tuple containing the original states of random, torch, and numpy.

    Methods:
        __enter__: Sets up the environment for deterministic or random generation.
        __exit__: Restores the original states of random, torch, and numpy and clears the torch cache.

    Example:
        ```python
        with SeedContext(seed=46):
            # Your generation code here
        ```
    """

    def __init__(
        self,
        seed,
        min_seed=0,
        default_seed=-1,
    ):
        """
        Initializes the SeedContext class.

        Parameters:
            seed (int): The seed to be used for random number generation.
            min_seed (int): The minimum value for a random seed (default is 0).
            default_seed (int): The default seed, triggering automatic randomization if used (default is -1).
        """
        self.is_deterministic = True
        self.seed = seed
        self.stop_condition = None
        if seed == default_seed:
            self.is_deterministic = False
            self.seed = random.randint(int(min_seed), int(2**32 - 1))

        self.original_seed = (
            random.getstate(),
            torch.get_rng_state(),
            np.random.get_state(),
        )

    def __enter__(self):
        """
        Sets up the environment for deterministic or random generation.

        Returns:
            SeedContext: The SeedContext instance.
        """
        random.seed(self.seed)
        torch.manual_seed(self.seed)
        np.random.seed(self.seed)
        torch.backends.cudnn.deterministic = self.is_deterministic
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Restores the original states of random, torch, and numpy and clears the torch cache.

        Parameters:
            exc_type: Exception type.
            exc_value: Exception value.
            traceback: Traceback information.
        """
        random.setstate(self.original_seed[0])
        torch.set_rng_state(self.original_seed[1])
        np.random.set_state(self.original_seed[2])
        torch.backends.cudnn.deterministic = False
        clear_torch_cache()
