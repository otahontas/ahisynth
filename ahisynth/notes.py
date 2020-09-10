base = {
    12: "C",
    13: "C#",
    14: "D",
    15: "D#",
    16: "E",
    17: "F",
    18: "F#",
    19: "G",
    20: "G#",
    21: "A",
    22: "A#",
    23: "B",
}

notes_by_midi = {
    (octave * 12) + key: value for (key, value) in base.items() for octave in range(8)
}
