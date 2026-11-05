# Networks Lingos for the client

- **socket**: an object that the client uses to send and receive message. Creating one does not contact the server; and for UDP there is no handshake.

- **Hostname & Port**: `localhost` means "on this computer" and resolves to `127.0.0.1`.

- **Encode & Decode**: Sockets move bytes and not strings. `.encode()` turns strings into bytes before `sendto`, and `.decode()` turns bytes from `recvfrom` back into strings.

- **Blocking Call**: `recvfrom` sits and waits. If the server dropped the packet then it waits forever, so we use `settimeout(1)` to change the wait into termination in 1 second and raise and exception.

- **RTT**: Time elapsed from `sento` and `recvfrom`, returns Python float in seconds.



