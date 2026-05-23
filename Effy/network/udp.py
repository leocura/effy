from __future__ import annotations
from dataclasses import dataclass
import socket

from Effy._internal.result import Ok, Err, Result
from Effy._internal.effect import Effect
from Effy.error import EffyError

@dataclass(frozen=True, slots=True)
class UdpSocket:
    """A purely functional representation of a non-blocking UDP socket.
    
    Attributes:
        fd: The internal socket file descriptor.
        address: The bound local address.
    """
    fd: socket.socket
    address: tuple[str, int]

@dataclass(frozen=True, slots=True)
class UdpServer:
    """A higher-level UDP Server representation for tracking clients."""
    sock: UdpSocket

def bind_udp(host: str, port: int) -> Effect[Result[UdpSocket, EffyError]]:
    """Creates an Effect that binds a non-blocking UDP socket."""
    def _run() -> Result[UdpSocket, EffyError]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setblocking(False)
            s.bind((host, port))
            return Ok(UdpSocket(s, (host, port)))
        except Exception as e:
            return Err(EffyError(-1, f"Failed to bind UDP socket: {e}"))
    return Effect(_run)

def send_udp(sock: UdpSocket, data: bytes, target: tuple[str, int]) -> Effect[Result[int, EffyError]]:
    """Creates an Effect that sends data via the UDP socket."""
    def _run() -> Result[int, EffyError]:
        try:
            bytes_sent = sock.fd.sendto(data, target)
            return Ok(bytes_sent)
        except BlockingIOError:
            return Ok(0)
        except Exception as e:
            return Err(EffyError(-1, f"Failed to send UDP data: {e}"))
    return Effect(_run)

def recv_udp(sock: UdpSocket, buffer_size: int = 4096) -> Effect[Result[tuple[bytes, tuple[str, int]] | None, EffyError]]:
    """Creates an Effect that attempts to receive data from the non-blocking UDP socket.
    
    Returns:
        Ok(None) if no data is currently available (EWOULDBLOCK).
        Ok((data, addr)) if data was received.
        Err(EffyError) on error.
    """
    def _run() -> Result[tuple[bytes, tuple[str, int]] | None, EffyError]:
        try:
            data, addr = sock.fd.recvfrom(buffer_size)
            # Ensure type safety for address tuple
            address = (str(addr[0]), int(addr[1]))
            return Ok((data, address))
        except BlockingIOError:
            return Ok(None)
        except Exception as e:
            return Err(EffyError(-1, f"Failed to receive UDP data: {e}"))
    return Effect(_run)
