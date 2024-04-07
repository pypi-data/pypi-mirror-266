from typing import Any, Optional
from uuid import uuid4

from redis.asyncio.client import PubSub, Redis
from typing_extensions import override

from faststream.broker.message import StreamMessage
from faststream.broker.publisher.proto import ProducerProto
from faststream.broker.types import (
    AsyncDecoder,
    AsyncParser,
    CustomDecoder,
    CustomParser,
)
from faststream.broker.utils import resolve_custom_func
from faststream.exceptions import WRONG_PUBLISH_ARGS, SetupError
from faststream.redis.message import DATA_KEY, PubSubMessage
from faststream.redis.parser import RawMessage, RedisPubSubParser
from faststream.redis.schemas import INCORRECT_SETUP_MSG
from faststream.types import AnyDict, SendableMessage
from faststream.utils.functions import timeout_scope


class RedisFastProducer(ProducerProto):
    """A class to represent a Redis producer."""

    _connection: "Redis[bytes]"
    _decoder: AsyncDecoder[StreamMessage[PubSubMessage]]
    _parser: AsyncParser[PubSubMessage]

    def __init__(
        self,
        connection: "Redis[bytes]",
        parser: Optional[CustomParser[PubSubMessage]],
        decoder: Optional[CustomDecoder[StreamMessage[PubSubMessage]]],
    ) -> None:
        self._connection = connection
        self._parser = resolve_custom_func(
            parser,  # type: ignore[arg-type,assignment]
            RedisPubSubParser.parse_message,
        )
        self._decoder = resolve_custom_func(
            decoder, RedisPubSubParser.decode_message)

    @override
    async def publish(  # type: ignore[override]
        self,
        message: SendableMessage,
        *,
        correlation_id: str,
        channel: Optional[str] = None,
        list: Optional[str] = None,
        stream: Optional[str] = None,
        maxlen: Optional[int] = None,
        headers: Optional[AnyDict] = None,
        reply_to: str = "",
        rpc: bool = False,
        rpc_timeout: Optional[float] = 30.0,
        raise_timeout: bool = False,
    ) -> Optional[Any]:
        if not any((channel, list, stream)):
            raise SetupError(INCORRECT_SETUP_MSG)

        psub: Optional[PubSub] = None
        if rpc:
            if reply_to:
                raise WRONG_PUBLISH_ARGS

            reply_to = str(uuid4())
            psub = self._connection.pubsub()
            await psub.subscribe(reply_to)

        msg = RawMessage.encode(
            message=message,
            reply_to=reply_to,
            headers=headers,
            correlation_id=correlation_id,
        )

        if channel is not None:
            await self._connection.publish(channel, msg)
        elif list is not None:
            await self._connection.rpush(list, msg)
        elif stream is not None:
            await self._connection.xadd(
                name=stream,
                fields={DATA_KEY: msg},
                maxlen=maxlen,
            )
        else:
            raise AssertionError("unreachable")

        if psub is None:
            return None

        else:
            m = None
            with timeout_scope(rpc_timeout, raise_timeout):
                # skip subscribe message
                await psub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=rpc_timeout or 0.0,
                )

                # get real response
                m = await psub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=rpc_timeout or 0.0,
                )

            await psub.unsubscribe()
            await psub.aclose()  # type: ignore[attr-defined]

            if m is None:
                if raise_timeout:
                    raise TimeoutError()
                else:
                    return None
            else:
                return await self._decoder(await self._parser(m))

    async def publish_batch(
        self,
        *msgs: SendableMessage,
        list: str,
        correlation_id: str,
    ) -> None:
        batch = (RawMessage.encode(message=msg, correlation_id=correlation_id,
                 reply_to=None, headers=None,) for msg in msgs)
        await self._connection.rpush(list, *batch)
