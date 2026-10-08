# Notifications on iOS

Wren iOS gets no push notifications today. This page says why, and what could change it.

## Why Signal pushes do not reach Wren

On iOS, an app that is not running learns about new data only when Apple's push service (APNs) tells it to wake up. Signal's server sends the wake-up to APNs, and APNs delivers it to the device that registered with a specific app id and a certificate made in Signal's developer account. The device token and the certificate both belong to that app id.

Wren has a different bundle id (`io.github.munzzyy.signal`) and is signed with a free Apple ID. A free account cannot create the push entitlement at all. Even with a paid account, Signal's server would still hold tokens for Signal's app id, not Wren's, and it has no reason to send pushes to anyone else's.

So a Wren install gets its messages by connecting to Signal's server over a websocket, and that connection only stays alive while the app is in the foreground. iOS suspends a backgrounded app within seconds. Anything sent while Wren is closed waits on the server until you open it again.

I looked for a way around this and there is none that works without an Apple account. Background fetch and silent tricks do not give reliable delivery, and I will not claim they do.

## What changes with an Apple account

A paid developer account lets Wren own its bundle id, make its own APNs key, and turn on Push Notifications. That only helps if something sends pushes to that key, and Signal's server does not. Two designs can work.

### Relay server

Same idea as MollySocket on Android.

1. A small server holds a websocket to Signal as a linked device of your account, so it sees messages the moment they arrive.
2. When a message arrives, it sends an empty wake-up through APNs, using Wren's key and the token Wren registered with it.
3. Wren wakes, opens its own connection to Signal, and fetches the message. The relay never needs message content.

Things to get right:

- The relay is a linked device, so it can read your messages if it wants to. It should run on hardware you control, or the design should send only a wake-up and drop the payload. Whoever runs it has to be trusted.
- The APNs payload must hold no sender or text. Apple sees the token and the timing.
- The relay needs its own device slot, and Signal allows a limited number of linked devices.
- Wren has to ask for a notification extension and stay inside the wake-up budget Apple gives it, or iOS stops delivering.

### TestFlight or App Store without a relay

These fix signing and the 7-day limit. They do not fix pushes by themselves. Without the relay, a TestFlight build behaves like the sideloaded one while the app is closed.

## What I will not do

I will not ship anything that pretends to notify while the app is closed. If the relay gets built, the README will say how it works and who runs it.
