# Project: voice-controlled switchboard

## Goal

A device connected to the home switchboard circuits (red light, white light, fan, plug socket, up to about 10 loads) that takes spoken commands through a microphone ("turn off the white light"), switches the right circuit, and answers through a speaker.

- **Phase 1:** fixed voice commands work reliably, offline if possible.
- **Phase 2:** add a small AI so it understands free-form speech ("it's too dark in here") and talks back naturally.

## Safety rules (non-negotiable)

- Home mains (230 V AC) can kill. **Nothing touches mains until the low-voltage prototype works.**
- All early prototyping uses LEDs and a 5 V relay module with **nothing plugged into the relay's switched side**.
- For the real switchboard, prefer **certified smart relay modules** installed by an electrician (for example ones that can run ESPHome or Tasmota firmware). Our device then controls them over Wi-Fi and never carries mains itself.
- If bare relay boards are ever used on mains: properly rated relays, a fuse, a closed non-conductive enclosure, and an electrician doing the wiring.
- Check each load's current against the relay rating. A fan or bulb is fine on a 10 A relay; a heater, geyser or AC is not.

## Proposed architecture

```
 [Mic] ──► Brain ──► (Wi-Fi / MQTT) ──► Switch node ──► relays / smart relays ──► lights, fan, socket
 [Speaker] ◄──┘
```

- **Brain:** listens for a wake word, turns speech into text, works out the intended command, switches, and replies.
  - Phase 1 option A: **ESP32-S3** board using Espressif's ESP-SR offline command recognition (fixed phrases).
  - Phase 1 option B (recommended, and leads into Phase 2): **Raspberry Pi 5** with a USB mic and speaker, running offline speech-to-text (Vosk or Whisper.cpp) and a text-to-speech engine (for example Piper).
  - Phase 2: on the Pi, a small local LLM or a cloud call (for example Claude Haiku 5.5) turns free-form speech into commands like `{"device": "fan", "action": "on"}`.
- **Switch node:** an **ESP32** driving a multi-channel relay module (prototype), later replaced by smart relays.
- Each device has a name, a channel and synonyms, kept in one config file (for example `devices.yaml`).

## Work plan for the coordinator

1. **Research (reader):** compare ESP32-S3 + ESP-SR against Raspberry Pi 5 + Vosk/Whisper for accuracy, latency, offline support and cost in India. Recommend relay modules and certified smart relays available in India.
2. **Design (coordinator):** pick the architecture and write a parts list, a wiring diagram for the low-voltage prototype, and the message format between brain and switch node.
3. **Simulate first (research-worker):** write the ESP32 switch-node firmware and test it in the Wokwi online simulator or with PlatformIO unit tests before any hardware arrives.
4. **Command understanding (research-worker):** write and test, in Python, the text → command parser against a list of 50+ sample phrases, including Hindi/English mixes.
5. **Bench prototype:** the user wires LEDs and a relay module and sends photos; the coordinator checks the wiring against the diagram.
6. **Phase 2:** add LLM-based intent parsing and spoken replies.

## Folder layout

- `firmware/`: ESP32 switch-node code (PlatformIO)
- `brain/`: Raspberry Pi code (speech in, intent, speech out)
- `docs/`: parts list, wiring diagrams, decisions
