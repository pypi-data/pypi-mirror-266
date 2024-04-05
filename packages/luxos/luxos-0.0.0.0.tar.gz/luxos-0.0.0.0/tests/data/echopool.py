from __future__ import annotations
import asyncio
import json
import logging
import time
import re
import argparse
import functools
from pathlib import Path


ENDCONFIG = "= DONE ="
SERVERLINE = re.compile(r"server:[(]['](?P<host>[^']+)['][,](?P<port>[^)]+)")

log = logging.getLogger(__name__)


def is_server_line(line) -> None | tuple[str, int]:
    if match := SERVERLINE.search(line.replace(" ", "")):
        return match.group("host"), int(match.group("port"))
    return None


def is_end_server_lines(line):
    return ENDCONFIG in line


async def handle_client(
    reader,
    writer,
    mode: str = "echo",
    delay_s: float | None = None,
    async_delay_s: float | None = None,
):
    data = await reader.read(1024)
    message = data.decode()
    addr = writer.get_extra_info("peername")
    this_addr = reader._transport.get_extra_info("sockname")

    log.debug("received at %s: %s", this_addr, message)
    if mode == "echo+":
        data = f"received by {this_addr}: {message}".encode()
    elif mode in {"json", "json+"}:
        result = {
            "status": "ok",
            "message": f"received from {addr}",
            "reason": "",
            "this": this_addr,
            "peer": addr,
            "result": {"message": message, "input": "", "output": ""},
        }
        try:
            message = json.loads(message)
            result["result"]["input"] = message
            if mode == "json+":
                if message.get("command", None) == "sleep":
                    await asyncio.sleep(float(message["value"]))
                    result["result"]["output"] = f"slept for {message['value']}"

        except Exception as e:
            result["status"] = "failed"
            result["reason"] = str(e)

        data = json.dumps(result, indent=2, sort_keys=True).encode()

    # this instroduces a delay between request <-> reply
    if async_delay_s:
        await asyncio.sleep(async_delay_s)

    writer.write(data)
    await writer.drain()

    writer.close()

    # this block the whole server!
    if delay_s:
        time.sleep(delay_s)


async def main():
    """
    The main function that sets up the server to listen on multiple ports.
    """
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument(
        "--delay", type=float, help="non async delay in s (block the server)"
    )
    p.add_argument(
        "--async-delay", type=float, help="async delay in s (block a single request)"
    )
    p.add_argument("--mode", choices=["echo", "echo+", "json", "json+"], default="echo")
    p.add_argument("--server-file", type=Path)
    p.add_argument("number", type=int)

    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    log.debug("starting %i servers in [%s] mode", args.number, args.mode)

    # Create a server for each port
    client = functools.partial(
        handle_client,
        mode=args.mode,
        delay_s=args.delay,
        async_delay_s=args.async_delay,
    )
    servers = await asyncio.gather(
        *[asyncio.start_server(client, "127.0.0.1", 0) for _ in range(args.number)]
    )

    message = [f"server: {server.sockets[0].getsockname()}" for server in servers]
    message.append(ENDCONFIG)
    txt = "\n".join(message)

    if args.server_file:
        args.server_file.parent.mkdir(parents=True, exist_ok=True)
        args.server_file.write_text(txt)
        log.debug("written servers to %s", args.server_file)
    else:
        print(txt)

    # Keep the main coroutine running
    while True:
        if args.server_file and not args.server_file.exists():
            break
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
