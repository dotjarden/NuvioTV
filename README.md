# NuvioTV · dotjarden community fork

**Independent community fork maintained by [dotjarden](https://github.com/dotjarden).** Based on [youngchris29-art/NuvioTV](https://github.com/youngchris29-art/NuvioTV) and its [NuvioMobile tvOS branch](https://github.com/youngchris29-art/NuvioMobile/tree/tvos-shared-extraction), built on [NuvioMedia/NuvioMobile](https://github.com/NuvioMedia/NuvioMobile). Original authorship and copyright notices are preserved. This fork is not an official Nuvio release and is not endorsed by the upstream maintainers.

**Modification notice — September 13, 2026:** this distribution includes changes to the Apple TV interface, Live TV, playback controls, account flows, settings, and remote navigation. See [FORK_CHANGES.md](FORK_CHANGES.md), [NOTICE](NOTICE), and the Git history for dates, authors, and scope.

A native Apple TV app using SwiftUI and Nuvio's shared Kotlin business logic. The original Apple TV port and architecture come from youngchris29-art; the underlying mobile project and shared core come from NuvioMedia and their contributors.

## Changes in this fork

- Home with a cinematic background and expandable catalog shelves.
- Combined Search and discovery with content type, genre, catalog, and sort filters.
- Live TV sources, favorites, programme guide, and cached channel loading.
- One playback interface across AVPlayer and MPV, with title information, timeline, subtitles, audio, playback settings, and stream details.
- Revised profile selection, account entry, and supported Nuvio synchronization.
- Organized TV settings and browser-based Remote Setup; add-ons live in Settings.
- Quieter content details, one season menu, a full synopsis, and a separate parental guide.
- Home scroll/focus fixes that restore access to the native top navigation.

Live TV sources and favorites are device-local. Profiles, libraries, watch progress, add-ons, and supported preferences use the existing Nuvio repositories. Playback compatibility still depends on the stream and available engine.

## Install and build

This fork currently provides source builds. Any downloadable builds will appear on [dotjarden's NuvioTV Releases](https://github.com/dotjarden/NuvioTV/releases); upstream binaries do not contain these fork changes.

Use [BUILDING.md](BUILDING.md) to build and sign the app with your own Apple development identity. [INSTALL.md](INSTALL.md) covers sideloading when an unsigned IPA is available.

```sh
git clone --recurse-submodules --branch main https://github.com/dotjarden/NuvioTV.git
cd NuvioTV
```

The project targets tvOS 26 or later; this fork's recent device builds and navigation tests use Xcode 27 beta and tvOS 27 beta. Beta SDK behavior may differ from a stable release.

## Repository layout

- `NuvioMobile/`: app source and shared core, pinned as a Git submodule to an exact commit in [dotjarden/NuvioMobile](https://github.com/dotjarden/NuvioMobile).
- `NuvioMobile/iosApp/NuvioTV/`: SwiftUI Apple TV interface.
- `NuvioMobile/shared/`: Kotlin `SharedCore` business logic.
- `NuvioMobile/MPVKit/`: upstream MPVKit submodule used for compatible playback.
- `scaffolding/`: QuickJS tvOS build script and patch.
- `docs/` and `design/`: development notes and design assets, including historical upstream material.

`main` is the public maintained version. Development also continues on `codex/native-tv-experience`. Preserve the submodule's exact commit when checking out a release.

## Credits and upstream

- [youngchris29-art/NuvioTV](https://github.com/youngchris29-art/NuvioTV): original native Apple TV port, SwiftUI interface, focus-engine work, and integration architecture.
- [youngchris29-art/NuvioMobile](https://github.com/youngchris29-art/NuvioMobile/tree/tvos-shared-extraction): tvOS shared-core extraction and native app foundation.
- [NuvioMedia/NuvioMobile](https://github.com/NuvioMedia/NuvioMobile): original Kotlin Multiplatform app and shared Nuvio business logic.
- [tapframe/NuvioTV](https://github.com/tapframe/NuvioTV): earlier React Native project in the Nuvio lineage.
- [MPVKit](https://github.com/mpvkit/MPVKit), [youngchris29-art's MPVKit fork](https://github.com/youngchris29-art/MPVKit), libmpv, QuickJS, and the other dependencies retain their own authorship and licenses.
- [dotjarden](https://github.com/dotjarden): maintenance and the changes described above. Individual contributions remain credited in Git history.

Report issues specific to this version in [this fork's issue tracker](https://github.com/dotjarden/NuvioTV/issues). Focused bug fixes can be contributed upstream under the original maintainers' contribution policy.

## License and source

Distributed under the inherited **GNU General Public License v3.0**. Keep [LICENSE](LICENSE), [NOTICE](NOTICE), existing copyright notices, and dependency licenses with redistributed copies. The original license has not been replaced.

Corresponding source is available in this repository and its pinned submodules. GitHub's automatic source ZIP does not include submodule contents: use the recursive checkout in [BUILDING.md](BUILDING.md). Release notes must identify the exact app and wrapper commits and provide source/build links for the distributed version.

## Media sources

NuvioTV browses metadata and plays media supplied by user-installed extensions and user-provided sources. It does not host media. Use sources you are authorized to access; third-party extensions and services are maintained independently.
