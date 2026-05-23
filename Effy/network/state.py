from __future__ import annotations
from dataclasses import dataclass

from Effy._internal.fp import pure

@dataclass(frozen=True, slots=True)
class Peer:
    """Represents a remote network peer in a functional state container."""
    address: tuple[str, int]
    last_seen_ticks: int = 0
    latency: int = 0

@dataclass(frozen=True, slots=True)
class NetworkState:
    """An immutable container tracking active peers and network events for the local scene loop.
    
    Attributes:
        peers: A tuple of known remote peers.
        incoming_messages: A tuple of unhandled messages received this frame.
    """
    peers: tuple[Peer, ...] = ()
    incoming_messages: tuple[tuple[bytes, tuple[str, int]], ...] = ()

    @pure
    def update_peer(self, address: tuple[str, int], current_ticks: int) -> NetworkState:
        """Update a peer's last seen tick or add them if they are new."""
        updated = False
        new_peers = []
        for p in self.peers:
            if p.address == address:
                new_peers.append(Peer(p.address, current_ticks, p.latency))
                updated = True
            else:
                new_peers.append(p)
                
        if not updated:
            new_peers.append(Peer(address, current_ticks, 0))
            
        return NetworkState(tuple(new_peers), self.incoming_messages)

    @pure
    def push_message(self, data: bytes, source: tuple[str, int]) -> NetworkState:
        """Add a received message to the state queue."""
        new_msgs = self.incoming_messages + ((data, source),)
        return NetworkState(self.peers, new_msgs)
        
    @pure
    def clear_messages(self) -> NetworkState:
        """Clear all messages from the queue (typically called at the end of a scene update)."""
        return NetworkState(self.peers, ())
