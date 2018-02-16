"""
Functional composition of loaders.

"""
from collections import defaultdict

from microcosm.config.model import Configuration


def merge(configs):
    result = Configuration()
    for config in configs:
        result.merge(config)
    return result


def load_each(*loaders):
    """
    Loader factory that combines a series of loaders.

    """
    def _load_each(metadata):
        return merge(
            loader(metadata)
            for loader in loaders
        )
    return _load_each


def dfs(dct, func, prefix=()):
    for key, value in dct.items():
        path = prefix + (key, )
        if isinstance(value, dict):
            dfs(value, func, path)
        else:
            func(path, value)


def traverse(dct, path):
    try:
        value = dct
        for key in path:
            value = value[key]
    except KeyError:
        return None
    else:
        return value


class PartitioningLoader:
    """
    Loader that composes other loaders and can enumerate which config value
    came from each partition.

    """
    def __init__(self, **loaders):
        # NB: as long as we're using Python >= 3.6, the loader dict order is preserved
        self.loaders = loaders
        self.partitions = defaultdict(dict)

    def __getattr__(self, partition):
        """
        Get all (post-merge) config data generated from a specific partition.

        """
        return self.partitions.get(partition)

    def merge_partition(self, partition, path, value):
        """
        Merge a value into a partition for a key path.

        """
        dct = self.partitions[partition]
        *heads, tail = path
        for part in heads:
            dct = dct.setdefault(part, dict())
        dct[tail] = value

    def __call__(self, metadata):
        """
        Load configuration from multiple partitions and preserve where each key
        came from.

        """
        configs = {
            key: loader(metadata)
            for key, loader in self.loaders.items()
        }
        config = merge(configs.values())

        def visit(path, value):
            for partition, config in configs.items():
                # NB: if multiple loaders return the same path/value, we'll duplicate here.
                # The right answer is extend the merge function to perform this tracking.
                if value == traverse(config, path):
                    self.merge_partition(partition, path, value)

        dfs(config, visit)
        return config


def load_partitioned(**loaders):
    return PartitioningLoader(**loaders)


def load_config_and_secrets(config, secrets):
    return PartitioningLoader(config=config, secrets=secrets)
