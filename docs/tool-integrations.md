# Optional decoding, cryptography, and OSINT integrations

This repository provides a cross-platform **catalog and integration layer**,
not copies of third-party projects. External tools must be installed separately
from their upstream sources. The package does not download, build, update, or
execute network-recon tools automatically.

## Use from the command line

```sh
vessell-tools list
vessell-tools doctor
vessell-tools inspect exiftool ./artifact.bin
vessell-tools inspect binwalk ./firmware.bin
vessell-tools inspect zsteg ./image.png
vessell-tools inspect gnupg ./message.gpg
vessell-tools decrypt-openpgp ./message.gpg ./message.txt --authorized
```

`doctor` checks for known executable names on `PATH`; it does not run them.
`inspect` accepts only ExifTool, Binwalk, zsteg, or GnuPG packet listing,
resolves one local regular file, invokes the selected command without a shell,
and returns output to the caller without writing an automatic report. The
adapter is read-only at the command level: it does not extract embedded
content, or contact network services. The separate `decrypt-openpgp` command
requires an explicit `--authorized` acknowledgment, uses the local GnuPG
keyring/prompt without accepting or logging passphrases, writes to a new
owner-only output file, and refuses to overwrite an existing destination.
Parser vulnerabilities remain possible; use an isolated, updated environment
for untrusted files.

The Python API is also available:

```python
from pathlib import Path
from vessell.tooling import discover_tools, run_local_inspector

available = discover_tools()
result = run_local_inspector("exiftool", Path("artifact.bin"))
```

## Catalog

| Tool | Intended role | Integration boundary |
| --- | --- | --- |
| [CyberChef](https://github.com/gchq/CyberChef) | Encoding/decoding recipes, format inspection, hashes, and crypto operations | Browser application; use a trusted local copy for sensitive data. Not invoked by the CLI. |
| [ExifTool](https://github.com/exiftool/exiftool) | Local file metadata | Read-only CLI adapter. |
| [Binwalk](https://github.com/ReFirmLabs/binwalk) | File signatures and embedded structures | Read-only signature scan; extraction is not invoked. |
| [zsteg](https://github.com/zed-0xff/zsteg) | PNG/BMP steganography checks | Read-only CLI adapter. |
| [Steghide](https://steghide.sourceforge.net/) | Supported image/audio steganography | Catalog only. Extraction can require a passphrase and explicit output handling. |
| [OpenStego](https://github.com/syvaidya/openstego) | Image watermarking and data hiding/extraction | Catalog only; use its upstream Java GUI/CLI. |
| [GnuPG](https://gnupg.org/documentation/) | OpenPGP packet inspection and decryption | Read-only packet listing adapter; decrypt with the user's own keyring and upstream prompt. |
| [OpenSSL](https://docs.openssl.org/master/) | Cryptographic formats and explicitly parameterized crypto | PATH discovery only; no generic decryption command is generated. |
| [hashID](https://github.com/pskiry/hashid) | Hash-format identification | Catalog only. Identification is not decryption. |
| [Hashcat](https://github.com/hashcat/hashcat) | Offline password-hash recovery | Catalog only; no cracking job or wordlist is configured or launched. Use only with data and systems you own or are authorized to assess. |
| [OSINT Framework](https://github.com/lockfale/OSINT-Framework) | Directory of public-source research resources | Reference directory, not a single executable. |
| [SpiderFoot](https://github.com/smicallef/spiderfoot) | Modular OSINT | Catalog only; modules may query third parties or targets. Review scope and module settings before use. |
| [Sn1per](https://github.com/1N3/Sn1per) | Active security reconnaissance/scanning | Catalog only; no target-scanning adapter. Use solely with explicit authorization and scope. |
| [Mosint](https://github.com/alpkeskin/mosint) | Email-address OSINT | Catalog only; no target lookup adapter. Use a lawful, appropriately scoped purpose. |
| [user-scanner](https://github.com/kaifcodec/user-scanner) | Email/username OSINT | Catalog only; performs external collection and is not invoked by this package. |

The stable IDs, activities, and executable aliases live in
`vessell.tooling.catalog`. Availability means only that a command name was
found on `PATH`; it does not verify provenance, version, integrity, licensing,
or safety.

## Decoding versus cryptography

Base64, hexadecimal, URL escaping, and similar encodings are reversible
representations, not encryption. Hashes are one-way digests: a hash identifier
can suggest an algorithm, but cannot recover the original value by decoding.
Actual decryption requires the matching format/cipher and, depending on the
scheme, a key or passphrase and parameters such as an IV. No integration here
guesses, stores, logs, or transmits secret key material.

Network OSINT and active reconnaissance are different from local artifact
decoding. A tool's presence in the catalog does not authorize a lookup, scan,
or contact with a third-party service.
