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
        _type_: _description_
    """

    max_size = abs(int(max_size))
    if max_size:
        return inputs_ids[:, -abs(int(max_size)) :]
    return inputs_ids


def join_tensors(*args, dim: int = 1, truncate_length: int = 0):
    """
    Concatenates multiple token tensors along a specified dimension and truncates the result if necessary.

    Parameters:
        *args (Tensor): Tensors to concatenate.
        dim (int, optional): The dimension along which to concatenate the tensors. Defaults to 1.
        truncate_length (int, optional): The maximum length to truncate the concatenated tensor to. Defaults to 0 (no truncation).

    Returns:
        Tensor: Concatenated tensor, possibly truncated.
    """
    args = [arg for arg in args if isinstance(arg, torch.Tensor)]
    res = None
    if args:
        res = torch.cat(args, dim=dim)
    if isinstance(truncate_length, int) and isinstance(res, torch.Tensor):
        return truncate(res, truncate_length)
    return res


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
