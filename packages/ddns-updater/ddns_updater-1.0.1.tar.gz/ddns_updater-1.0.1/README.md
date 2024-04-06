# DynDNS Updater

This python package aims to support with regular dynamic DNS updates.

## Installation

The package is deployed as python package on [PyPI](https://pypi.org/).

### Installing Using `pipx`
The easiest way installing the package is using [pipx](https://pipx.pypa.io/stable/):

```bash
pipx install ddns-updater
```

### Alternate Installation Methods

The package can be installed using any method for installing packages from
[PyPI](https://pypi.org/).

## Usage

After installation, the package provides `ddu` as CLI. Running

```bash
ddu -h
```

prints the usage instructions to the terminal.

### Add a new Entry

New DDNS entries are added using `ddu add`. Detailed instructions are printed with `ddu add -h`.
Added entries are stored in the internal data base.

### List All Entries

`ddu list` shows a list of all available entries in the data base. All entries are uniquely
identified by a `UUID4`.

### Delete an Entry

`ddu delete` is available to delete entries from the data base. Entries are identified using the
`UUID`.

### Update

`ddu update` updates the DynDNS entry to the IP address from which the update command is called.

## Provider

This section documents the available DynDNS provider. Usually, they need some kind of
authentication. The authentication data are not stored in the data base. Instead, they are stored
using the [keyring](https://pypi.org/project/keyring/) package.

### All-Inkl

[All-Inkl](https://all-inkl.com/) is a German web hosting provider. A new DynDNS entry is added
through their `KAS`. It is available in the menu via `Tools->DDNS Settings`. After creating a new
entry, a username and password is shown in `KAS`. These data must be passed to the `ddu add`
command.

## Support

<a href="https://www.buymeacoffee.com/nurbscoder" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
