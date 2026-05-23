from __future__ import annotations
from Effy.network.state import NetworkState

def test_network_state_peers() -> None:
    state = NetworkState()
    
    # Adding a new peer
    addr = ("127.0.0.1", 9000)
    state = state.update_peer(addr, 100)
    
    assert len(state.peers) == 1
    assert state.peers[0].address == addr
    assert state.peers[0].last_seen_ticks == 100
    
    # Updating existing peer
    state = state.update_peer(addr, 250)
    assert len(state.peers) == 1
    assert state.peers[0].last_seen_ticks == 250
    
def test_network_state_messages() -> None:
    state = NetworkState()
    addr = ("127.0.0.1", 9000)
    
    state = state.push_message(b"hello", addr)
    state = state.push_message(b"world", addr)
    
    assert len(state.incoming_messages) == 2
    assert state.incoming_messages[0] == (b"hello", addr)
    assert state.incoming_messages[1] == (b"world", addr)
    
    state = state.clear_messages()
    assert len(state.incoming_messages) == 0
