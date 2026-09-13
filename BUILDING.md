# Building the dotjarden community fork

## Prerequisites

- macOS with Xcode and an installed tvOS SDK. Recent checks used Xcode 27 beta / tvOS 27 beta.
- JDK 17 or later and CMake for the QuickJS build.
- Git with recursive submodule support.
- Your own Apple signing identity for a physical Apple TV. Simulator builds do not require device provisioning.

## Complete source checkout

```sh
git clone --recurse-submodules --branch main https://github.com/dotjarden/NuvioTV.git
cd NuvioTV
git submodule update --init --recursive
```

For a released version, check out the wrapper commit recorded in its release notes,
then run `git submodule update --init --recursive` again. Keep the pinned submodule
commits; `--remote` would replace them with newer code. The checkout includes
NuvioMobile and MPVKit; GitHub's automatic ZIP omits these submodule contents.

## Build the tvOS QuickJS dependency

From the NuvioTV directory:

```sh
./scaffolding/build-quickjs-tvos.sh
```

The script fetches the upstream QuickJS wrapper and its dependencies, applies the
included tvOS patch, and publishes the required artifacts into local Maven.

## Build and run

```sh
open NuvioMobile/iosApp/iosApp.xcodeproj
```

Select **NuvioTV** and an Apple TV simulator or paired Apple TV. For a physical
device, select your development team and available bundle/app-group identifiers
for both NuvioTV and its Top Shelf extension. Use your own signing configuration;
upstream signing identities do not belong to this fork's users.

The Xcode build invokes Gradle to generate and link `SharedCore`. Public backend
configuration has defaults in the source. A custom backend can be configured with
`SUPABASE_URL` and its public `SUPABASE_ANON_KEY` through the supported local build
configuration. Do not put private service-role keys or account credentials into a
client application or commit local signing/configuration files.

A simulator build from the wrapper checkout:

```sh
xcodebuild -project NuvioMobile/iosApp/iosApp.xcodeproj \
  -scheme NuvioTV -configuration Debug \
  -destination 'generic/platform=tvOS Simulator' build
```

If using Xcode beta, set `DEVELOPER_DIR` to its `Contents/Developer` directory first.

## Source and release records

Maintain [LICENSE](LICENSE), [NOTICE](NOTICE), [FORK_CHANGES.md](FORK_CHANGES.md), and
dependency notices. A distributed binary's release notes must link the matching
NuvioMobile and NuvioTV commits and these build instructions. Source links must
remain available to recipients of that build. Do not package a dirty checkout as
though it matched a published source commit.

`NuvioMobile/scripts/release-beta.sh` targets the two **dotjarden** repositories.
Its automatic release tags use `dotjarden-tvos-v…` to distinguish fork builds.
Its help describes packaging/publishing; running it can publish releases. No binary
release is required to build locally or contribute a source change.
