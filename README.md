# Wren for iOS

Wren iOS is a fork of Signal-iOS that I rebranded so it can sit next to the Android and Desktop Wren clients. Right now it is a rebrand and a CI build, nothing more.

Three limits, before anything else:

1. No push notifications. iOS delivers Signal's pushes through Apple's push service (APNs), and those are tied to Signal's own app id and certificate. Wren has a different bundle id and I have no Apple Developer account, so Apple will never wake it. Messages arrive only while the app is open in the foreground. More in [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md).
2. Sideloading lasts 7 days. Without a paid Apple account, a free Apple ID gets you an AltStore or Sideloadly install that expires after a week. You have to re-sign it every 7 days.
3. Nothing here has been built yet. I have no Mac and no Xcode. The code in this repo has never been compiled by me, and the CI workflow has not run. Treat every claim below about the build as untested until a CI run goes green.

## What should work

Signal's own code is unchanged apart from the name, the bundle prefix and the icon, so in principle:

- Registering a new number, or linking as a secondary device to a Signal or Wren account you already have.
- Sending and receiving messages while the app is open.
- Voice and video calls while the app is open.

I have not tested any of it on a device.

## Build it in Xcode

You need a Mac, Xcode, and a free Apple ID.

```
git clone --recurse-submodules https://github.com/munzzyy/wren-ios
cd wren-ios
make dependencies
open Signal.xcworkspace
```

In Xcode, set your Team on the Signal, SignalShareExtension and SignalNSE targets. Turn off Push Notifications, Apple Pay, Communication Notifications and Data Protection, because a free account cannot provision them. Keep App Groups on. If another developer already took `io.github.munzzyy.signal`, set `SIGNAL_BUNDLEID_PREFIX` in the project build settings to a prefix of your own. That also renames the app group, which is what you want.

Free accounts sign for 7 days. After that the app stops launching until you build and install again.

Upstream's [BUILDING.md](BUILDING.md) has the rest.

Two caveats for anyone trying the Xcode route: Signal.entitlements lists more capabilities than a free Apple ID can carry (app groups, keychain sharing, push, associated domains, and more), so you have to remove every one of them or use your own entitlements file, and Signal's Pods submodule points at a private repository, so `make dependencies` may need the public signalapp/Signal-Pods mirror. Neither path has been exercised here yet; the AltStore route below is the one I expect to work first.

## Install the CI build

The workflow in `.github/workflows/build-unsigned.yml` builds `Wren-unsigned.ipa` and uploads it with a SHA-256 file. Run it from the Actions tab, or push a tag that starts with `v` and it also lands in a draft release. GitHub's macOS runners are free for public repos only, so it needs this repo to be public.

The IPA is unsigned. Open it in AltStore or Sideloadly, sign in with your Apple ID, and it signs and installs the app for you. Check the hash first:

```
sha256sum -c Wren-unsigned.ipa.sha256
```

AltStore refreshes in the background when the phone and the computer are on the same network. Sideloadly you have to run again by hand.

## When there is an Apple account

Three options, in the order I would pick them:

1. A paid developer account, Wren's own bundle id, and TestFlight. This works but needs someone 18 or older to pay 99 USD a year.
2. A relay server that links to the account as a device and sends a wake-up through Wren's own APNs key, in the style of MollySocket on Android. It also needs the paid account, because the push key comes from it.
3. Publishing to the App Store under Wren's bundle id with APNs. Same cost, more review.

Details of the relay are in [docs/NOTIFICATIONS.md](docs/NOTIFICATIONS.md). None of this exists yet.

## Upstream

`tools/merge-upstream.sh` merges Signal-iOS main and then runs `tools/rebrand.py`, which puts the bundle prefix, the name and the icon back. `python3 tools/rebrand.py --check` tells you whether anything drifted. The strings files still say Signal. I left them alone to keep merges small.

## License

AGPL-3.0-only, the same as Signal-iOS. See [LEGAL.md](LEGAL.md). Wren is not affiliated with Signal Messenger, LLC or the Signal Foundation. Report security problems as described in [SECURITY.md](SECURITY.md).
