# Custom types

from typing import List

EventDelta = float  # in seconds
TimeStamp = float  # time.time()
MidiPacket = List[Int]
MidiMessage = Tuple[MidiPacket, EventDelta, TimeStamp]
