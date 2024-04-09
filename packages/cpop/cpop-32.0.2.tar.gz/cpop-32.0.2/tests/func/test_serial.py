import pickle

import pop.hub


def test_sync_serializable():
    return
    hub = pop.hub.Hub()
    serial = pickle.dumps(hub)
    restored = pickle.loads(serial)
    assert restored == hub
