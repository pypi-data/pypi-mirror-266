import asyncio
import logging
from ssl import PROTOCOL_TLSv1_2, Purpose, SSLContext, TLSVersion, create_default_context
from typing import Final

import betterlogging

from natsio.client.config import ClientConfig, TLSConfig
from natsio.client.core import NATSCore
from natsio.messages.core import CoreMsg

log = logging.getLogger(__name__)

INSTALL_TLS: Final[bool] = False


async def callback(msg: CoreMsg) -> None:
    print(f"Received a message: {msg.subject} {msg.payload.decode()}")

    if msg.reply_to is not None:
        await msg.reply(b"done")


def get_ssl_context() -> SSLContext:
    ctx = create_default_context(
        purpose=Purpose.SERVER_AUTH,
    )
    ctx.load_verify_locations(cafile="/Users/corrupt/Code/natsio/certs/rootCA.pem")
    ctx.load_cert_chain(
        certfile="/Users/corrupt/Code/natsio/certs/client-cert.pem",
        keyfile="/Users/corrupt/Code/natsio/certs/client-key.pem",
    )
    return ctx


async def main() -> None:
    betterlogging.basic_colorized_config(level=logging.DEBUG)
    # logging.basicConfig(level=logging.DEBUG)

    tls = None
    if INSTALL_TLS:
        tls = TLSConfig(
            ssl=get_ssl_context(),
            hostname="localhost",
            handshake_first=True,
        )
    config = ClientConfig(
        servers=[
            # "nats://localhost:4223",
            "nats://localhost:4224",
            "nats://localhost:4222",
        ],
        tls=tls,
        allow_reconnect=True,
    )

    # client = NATSCore(config)
    # await client.connect()
    async with NATSCore(config) as client:

        sub = await client.subscribe("foo", callback=callback)
        # await sub.unsubscribe()

        await asyncio.Future()
        # try:
        #     async for msg in sub.messages:
        #         await callback(msg)
        # except asyncio.CancelledError:
        #     print("Subscription cancelled")
    print("Connection closed [main.py]")


def run() -> None:
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Received signal to terminate the app")


if __name__ == "__main__":
    run()
