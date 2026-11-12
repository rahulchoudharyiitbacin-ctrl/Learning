# Parts list (beginner-friendly)

Prices are **rough estimates in ₹** for Indian hobby stores (Robu.in, Amazon.in, local electronics markets). They change often, so check before buying.

## Phase 1: bench prototype (safe, low voltage, nothing touches mains)

| Part | What it is, in plain words | What it needs / connects to | Approx. ₹ |
|---|---|---|---|
| **ESP32 dev board** (ESP32-WROOM DevKit) | A tiny computer with Wi-Fi. It flips the relays when told to. Programmed from your Mac like an Arduino. | A micro-USB or USB-C cable to your Mac (power + programming). Wires to the relay module. | 350 – 600 |
| **4-channel 5 V relay module** (8-channel if you want more devices) | Electrically controlled switches. The ESP32 sends a tiny signal and the relay physically clicks a switch, like a finger pressing your wall switch. | 5 V and ground from the ESP32 board, plus one signal wire per channel. | 4-ch: 150 – 250 · 8-ch: 300 – 450 |
| **Breadboard + jumper wires + LEDs + resistors kit** | Lets you connect things without soldering. LEDs stand in for the light, fan and socket. | Nothing extra. | 300 – 500 |
| **Raspberry Pi 5 (4 GB)** | A small full computer (runs Linux). It is the "brain": it listens, understands and speaks. | The parts below. | 5,500 – 6,500 |
| Official Pi 5 power supply (27 W, USB-C) | Power for the Pi. Cheap phone chargers cause random crashes. | Wall socket. | 1,000 – 1,200 |
| microSD card, 32–64 GB | The Pi's "hard disk". | Your Mac (or a card reader) to install the operating system once. | 400 – 700 |
| Pi 5 case with fan | Protection and cooling. | Nothing extra. | 500 – 1,000 |
| **USB microphone** | The ears. | A Pi USB port. | 300 – 1,000 |
| **Small USB or 3.5 mm speaker** | The voice. | A Pi USB port (the Pi 5 has no headphone jack, so a USB speaker is easiest). | 300 – 800 |

**Phase 1 total: about ₹9,000 – 12,500.** The Pi accounts for most of it, but you reuse it for Phase 2 (the AI).

### Cheaper alternative (all-in-one, about ₹2,500 – 3,500)

| Part | Approx. ₹ |
|---|---|
| ESP32-S3 dev board (has voice-recognition support) | 700 – 1,200 |
| INMP441 microphone module | 200 – 350 |
| MAX98357A amplifier + small 3 W speaker | 350 – 600 |
| 4-channel relay module + breadboard kit | 450 – 750 |

This one board understands only **fixed phrases** ("turn on the fan"), and Phase 2 AI is much harder on it. It's good for learning; the Raspberry Pi route grows better.

## Phase 1b: the real switchboard (after the prototype works)

| Part | Notes | Approx. ₹ |
|---|---|---|
| Smart relay modules (one per device) | Certified boxes that sit behind your switchboard and take Wi-Fi commands. Choose ones that can run ESPHome or Tasmota firmware so our code can talk to them directly. | 1,000 – 1,500 each |
| Electrician to fit them | **Do not wire mains (230 V) yourself.** | 500 – 1,500 visit |

For 4 devices: about ₹5,000 – 7,500.

## Phase 2: the AI

No new hardware if you have the Pi. Options:
- **Local model on the Pi:** free to run, slower, works offline.
- **Cloud model** (for example Claude Haiku 5.5): smarter and fast, costs a few paise per command and needs internet.

## Tools worth having

- A cheap **multimeter** (₹400 – 800) to check voltages and connections.
- A small screwdriver set (relay modules use screw terminals).
- No soldering iron needed for Phase 1.
