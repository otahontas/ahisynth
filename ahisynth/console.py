from __future__ import annotations
from typing import Tuple, Any

import asyncio

import click

import uvloop
import time
import numpy as np
import sounddevice as sd

from .midi import get_ports, silence, NOTE_ON, NOTE_OFF
from .types import MidiPacket, EventDelta, MidiMessage
from .notes import notes_by_midi, hz_by_midi

MIDI_KB = "Akai LPK25 Wireless:Akai LPK25 Wireless MIDI 1 20:0"


async def async_main() -> None:
    midi_queue: asyncio.Queue[MidiMessage] = asyncio.Queue(maxsize=256)
    loop = asyncio.get_event_loop()
    try:
        from_kb, to_kb = get_ports(MIDI_KB, clock_source=True)
    except ValueError as port:
        click.secho(f"{port} is not available", fg="red", err=True)
        raise click.Abort

    def read_midi_input(msg: Tuple[MidiPacket, EventDelta], data: Any = None) -> None:
        sent_time = time.time()
        midi_packet, event_delta = msg
        midi_message = (midi_packet, event_delta, sent_time)
        try:
            loop.call_soon_threadsafe(midi_queue.put_nowait, midi_message)
        except BaseException as b:
            click.secho(f"callback failed {b}", fg="red", err=True)

    from_kb.set_callback(read_midi_input)

    try:
        await midi_consumer(midi_queue)
    except asyncio.CancelledError:
        from_kb.cancel_callback()
        silence(to_kb)


async def midi_consumer(midi_queue: asyncio.Queue[MidiMessage]) -> None:
    while True:
        pkt, delta, sent_time = await midi_queue.get()
        if pkt[0] == NOTE_ON:
            click.echo(f"Playing: {notes_by_midi[pkt[1]]}, {hz_by_midi[pkt[1]]}")
            await play(hz_by_midi[pkt[1]])


start_idx = 0

async def play(frequency):
    amplitude = 0.2
    samplerate = 44100.0

    def callback(outdata, frames, time, status):
        global start_idx
        t = (start_idx + np.arange(frames)) / samplerate
        t = t.reshape(-1, 1)
        outdata[:] = amplitude * np.sin(2 * np.pi * frequency * t)
        start_idx += frames

    event = asyncio.Event()

    stream = sd.OutputStream(device=None, channels=1, callback=callback,
                             samplerate=samplerate)
    with stream:
        await event.wait()


@click.command()
def main() -> None:
    uvloop.install()
    asyncio.run(async_main())
