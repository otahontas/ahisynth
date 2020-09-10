from __future__ import annotations
from typing import Tuple, Any

import asyncio

import click

import uvloop
import time

from .midi import get_ports
from .types import MidiPacket, EventDelta, MidiMessage


async def async_main() -> None:
    message_queue: asyncio.Queue[MidiMessage] = asyncio.Queue(maxsize=256)
    try:
        from_circuit, to_circuit = get_ports("Circuit", clock_source=True)
        from_mono_station, to_mono_station = get_ports("Circuit Mono Station")
    except ValueError as port:
        click.secho(f"{port} is not available", fg="red", err=True)
        raise click.Abort

    def read_midi_input(msg: Tuple[MidiPacket, EventDelta], data: Any = None) -> None:
        sent_time = time.time()
        midi_packet, event_delta = msg
        midi_message = (midi_packet, event_delta, sent_time)
        message_queue.put_nowait(midi_message)

    from_circuit.set_callback(read_midi_input)


@click.command()
def main() -> None:
    uvloop.install()
    asyncio.run(async_main())
