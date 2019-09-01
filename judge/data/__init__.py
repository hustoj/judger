from .cases import CaseManager, InvalidDataCase
from .store import DataStore, LocalCache


def new_data_store(path, api) -> DataStore:
    manager = DataStore()
    manager.set_cache(LocalCache(path))
    manager.set_remote(api)

    return manager
