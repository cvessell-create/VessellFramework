"""Metadata for optional third-party inspection, crypto, and OSINT tools."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import StrEnum


class ToolActivity(StrEnum):
    LOCAL_READ_ONLY = "local-read-only"
    LOCAL_KEY_REQUIRED = "local-key-required"
    LOCAL_AUTHORIZED = "local-authorized-use"
    NETWORK_OSINT = "network-osint"
    ACTIVE_RECON = "active-recon"
    REFERENCE_ONLY = "reference-only"


@dataclass(frozen=True)
class ToolDefinition:
    tool_id: str
    name: str
    category: str
    purpose: str
    source_url: str
    activity: ToolActivity
    executables: tuple[str, ...] = ()
    integration: str = ""


@dataclass(frozen=True)
class ToolAvailability:
    tool: ToolDefinition
    executable_path: str | None

    @property
    def available(self) -> bool:
        return self.executable_path is not None


TOOLS: tuple[ToolDefinition, ...] = (
    ToolDefinition(
        "cyberchef",
        "CyberChef",
        "encoding and cryptanalysis",
        "Browser-based recipes for encoding, decoding, hashes, and crypto formats.",
        "https://github.com/gchq/CyberChef",
        ToolActivity.REFERENCE_ONLY,
        integration="Use a trusted local copy for sensitive text; no CLI adapter is assumed.",
    ),
    ToolDefinition(
        "exiftool",
        "ExifTool",
        "metadata",
        "Read metadata and tags from supported local files.",
        "https://github.com/exiftool/exiftool",
        ToolActivity.LOCAL_READ_ONLY,
        ("exiftool",),
        "Read-only metadata inspection is available through run_local_inspector.",
    ),
    ToolDefinition(
        "binwalk",
        "Binwalk",
        "file signatures",
        "Identify embedded file signatures and structures in local binary files.",
        "https://github.com/ReFirmLabs/binwalk",
        ToolActivity.LOCAL_READ_ONLY,
        ("binwalk",),
        "Signature listing only; extraction is deliberately not run by the adapter.",
    ),
    ToolDefinition(
        "zsteg",
        "zsteg",
        "steganography",
        "Inspect PNG and BMP images for common LSB steganography patterns.",
        "https://github.com/zed-0xff/zsteg",
        ToolActivity.LOCAL_READ_ONLY,
        ("zsteg",),
        "Local image inspection is available through run_local_inspector.",
    ),
    ToolDefinition(
        "steghide",
        "Steghide",
        "steganography",
        "Inspect supported image/audio carriers and extract data when authorized.",
        "https://steghide.sourceforge.net/",
        ToolActivity.LOCAL_KEY_REQUIRED,
        ("steghide",),
        "No extraction wrapper; protected payloads require the correct passphrase.",
    ),
    ToolDefinition(
        "openstego",
        "OpenStego",
        "steganography",
        "Java application for watermarking and data hiding/extraction in images.",
        "https://github.com/syvaidya/openstego",
        ToolActivity.LOCAL_KEY_REQUIRED,
        integration="Use the upstream CLI/GUI with user-selected input and output paths.",
    ),
    ToolDefinition(
        "gnupg",
        "GnuPG",
        "cryptography",
        "Inspect and decrypt OpenPGP files with the user's own keyring.",
        "https://gnupg.org/documentation/",
        ToolActivity.LOCAL_READ_ONLY,
        ("gpg", "gpg2"),
        "Packet listing is read-only; decryption stays with upstream GnuPG and its key prompt.",
    ),
    ToolDefinition(
        "openssl",
        "OpenSSL",
        "cryptography",
        "Inspect cryptographic formats and perform explicitly parameterized crypto.",
        "https://docs.openssl.org/master/",
        ToolActivity.LOCAL_KEY_REQUIRED,
        ("openssl",),
        "No generic decrypt command is generated; cipher, format, and key material matter.",
    ),
    ToolDefinition(
        "hashid",
        "hashID",
        "hash identification",
        "Suggest possible hash algorithms from a supplied digest string.",
        "https://github.com/pskiry/hashid",
        ToolActivity.LOCAL_READ_ONLY,
        ("hashid",),
        "Identification only; a digest is not reversibly decrypted.",
    ),
    ToolDefinition(
        "hashcat",
        "Hashcat",
        "authorized password recovery",
        "Offline password-hash recovery for data and systems the operator owns or is authorized to assess.",
        "https://github.com/hashcat/hashcat",
        ToolActivity.LOCAL_AUTHORIZED,
        ("hashcat",),
        "No cracking job is launched or configured by VessellFramework.",
    ),
    ToolDefinition(
        "osint-framework",
        "OSINT Framework",
        "OSINT reference",
        "Directory of public-source research tools and resources.",
        "https://github.com/lockfale/OSINT-Framework",
        ToolActivity.REFERENCE_ONLY,
        integration="A directory/resource, not a single executable or bundled dependency.",
    ),
    ToolDefinition(
        "spiderfoot",
        "SpiderFoot",
        "network OSINT",
        "Modular OSINT automation; selected modules may query third-party services or targets.",
        "https://github.com/smicallef/spiderfoot",
        ToolActivity.NETWORK_OSINT,
        ("sf.py", "spiderfoot"),
        "Not invoked by the local-file adapter; assess scope and module settings first.",
    ),
    ToolDefinition(
        "sn1per",
        "Sn1per",
        "active reconnaissance",
        "Automated security reconnaissance and scanning.",
        "https://github.com/1N3/Sn1per",
        ToolActivity.ACTIVE_RECON,
        ("sniper", "sn1per"),
        "No target-scanning adapter; use only with explicit authorization and scope.",
    ),
    ToolDefinition(
        "mosint",
        "Mosint",
        "network OSINT",
        "Email-address OSINT using external sources and services.",
        "https://github.com/alpkeskin/mosint",
        ToolActivity.NETWORK_OSINT,
        ("mosint",),
        "No target lookup adapter; external collection requires a lawful purpose.",
    ),
    ToolDefinition(
        "user-scanner",
        "user-scanner",
        "network OSINT",
        "Email/username OSINT using external sites and scan vectors.",
        "https://github.com/kaifcodec/user-scanner",
        ToolActivity.NETWORK_OSINT,
        ("user-scanner",),
        "Catalog only; no lookup adapter or automatic target collection.",
    ),
)

_TOOLS_BY_ID = {tool.tool_id: tool for tool in TOOLS}


def list_tools() -> tuple[ToolDefinition, ...]:
    """Return all catalog entries in stable display order."""
    return TOOLS


def get_tool(tool_id: str) -> ToolDefinition:
    """Look up a tool by stable ID; unknown IDs raise KeyError."""
    try:
        return _TOOLS_BY_ID[tool_id]
    except KeyError:
        raise KeyError(f"unknown tool id: {tool_id}") from None


def discover_tools() -> tuple[ToolAvailability, ...]:
    """Check PATH for tool executables without launching them."""
    found: list[ToolAvailability] = []
    for tool in TOOLS:
        executable_path = next(
            (path for name in tool.executables if (path := shutil.which(name))),
            None,
        )
        found.append(ToolAvailability(tool, executable_path))
    return tuple(found)
