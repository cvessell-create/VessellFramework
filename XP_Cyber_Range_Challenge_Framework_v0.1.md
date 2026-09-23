---
name: xp-cyber-range-challenge-framework
description: >
  A reusable challenge framework for XP Cyber Range / NICE-style operations. Organizes
  tasks into network recovery, malware triage, forensics, identity and access control,
  Linux administration, patching, and evidence submission. Built from last-year challenge
  examples and adapted into a reusable operational template.
---

# XP Cyber Range Challenge Framework
## Version 0.1 — Research Candidate

## Status
This document is an operational framework and challenge taxonomy for building a repeatable
process for XP range activities. It is not a substitute for the official assignment brief.

## Purpose
Provide a reusable structure for solving mixed cyber challenge tasks that combine:
- configuration remediation;
- malware/virus cleanup;
- forensic file recovery;
- permissions and access control work;
- Linux administration;
- patching and hardening;
- evidence capture and submission.

The goal is to convert one-off challenge notes into a structured method that can be reused
across similar labs.

# 1. Challenge Operating Principles

1. Confirm the objective before making changes.
2. Identify the affected system and the operating context.
3. Validate the current network, identity, or system state before remediation.
4. Use the smallest corrective action that restores service.
5. Keep evidence of each step.
6. Preserve forensic integrity when recovering files or evidence.
7. Submit only after verifying the result.

# 2. Core Challenge Categories

## A. Configuration Management Gone Awry
Focus area:
- IP misconfiguration
- incorrect subnet mask
- wrong default gateway
- interface naming issues
- routing problems between VLANs or segments
- broken AD reachability

Typical actions:
- check interface with `ipconfig /all`, `ip link show`, or `ip addr show`
- confirm interface name using `netsh interface show interface` or `ip link show`
- correct IP and gateway with command-line tools
- flush stale address if needed
- test with ping and tracert

Operational pattern:
`VERIFY -> IDENTIFY INTERFACE -> SET STATIC IP -> SET GATEWAY -> TEST PATH -> CONFIRM REACHABILITY`

## B. Dangerous Drive / Malware Triage
Focus area:
- infected removable media or mapped drives
- EICAR detection or malicious file artifacts
- ClamWin scans
- quarantine or deletion of malicious files

Typical actions:
- enable hidden files and file extensions
- scan the drive
- identify infected files
- remove infected files using secure deletion procedures
- rescan and confirm no detections remain

Operational pattern:
`SCAN -> IDENTIFY MALWARE -> REMOVE -> VERIFY CLEAN STATE`

## C. Forensically Finding Files
Focus area:
- disk management
- hidden partitions or unassigned drive letters
- forensic evidence on removable storage
- transferring files without altering them

Typical actions:
- open Disk Management
- assign a drive letter to the correct volume
- enable hidden items and extensions
- search for files modified after a date threshold
- copy files to evidence location using `scp` or secure transfer
- preserve original file integrity

Operational pattern:
`DISCOVER STORAGE -> ASSIGN DRIVE -> IDENTIFY EVIDENCE -> COPY TO SECURE LOCATION -> PRESERVE INTEGRITY`

## D. Helpdesk / User Workstation Nightmares
Focus area:
- mouse configuration
- desktop icon visibility
- mapped network drive issues
- proxy settings causing internet failures

Typical actions:
- adjust mouse primary button settings
- enable desktop icons
- map network share to a drive letter
- disable bad proxy settings
- confirm connectivity to internet or gateway

Operational pattern:
`OBSERVE USER REPORT -> VERIFY SYSTEM CONFIGURATION -> RESOLVE ONLY THE AFFECTING ISSUE -> TEST FUNCTION`

## E. Domain Controller / Identity & Access Control
Focus area:
- Active Directory user and group management
- group creation and permission assignment
- account disablement
- log-on restrictions
- domain policy enforcement

Typical actions:
- create or update security groups
- assign users to groups
- add or remove permissions to shares
- disable compromised or inactive accounts
- set log-on restrictions to allow access only to approved machines
- apply GPOs for password and account lockout policy

Operational pattern:
`IDENTIFY ROLE -> CREATE OR ADJUST GROUP -> APPLY PERMISSIONS -> RESTRICT ACCESS -> VALIDATE ACCESS`

## F. Linux Administration 101
Focus area:
- user management
- sudo access
- service updates
- package maintenance

Typical actions:
- create new Linux users
- grant admin rights via `visudo`
- update services or packages with `yum` or `apt-get`
- verify the service is functioning after update

Operational pattern:
`CREATE USER -> GRANT PRIVILEGES -> VERIFY ENFORCEMENT -> UPDATE SYSTEM -> VALIDATE SERVICE`

## G. Preventative Protection / Hardening
Focus area:
- patching vulnerable systems
- disabling SMB1
- updating outdated software
- detecting and mitigating the threat vector

Typical actions:
- check for updates
- install relevant patch
- disable legacy SMBv1 if required
- confirm the change via validation command
- verify the security control is in place

Operational pattern:
`ASSESS VULNERABILITY -> PATCH OR DISABLE -> VALIDATE CONTROL -> CONFIRM THREAT MITIGATION`

## H. Database Backup and Recovery
Focus area:
- MySQL database discovery
- dump creation using `mysqldump`
- transferring backup files to another host
- creating a restore database
- importing the dump and verifying tables

Typical actions:
- locate MySQL binaries
- create a dump of the relevant database
- secure-transfer the backup file
- create a new database on the restore host
- import the `.sql` dump
- validate data integrity and tables

Operational pattern:
`LOCATE DATABASE -> BACKUP -> TRANSFER -> RESTORE -> VERIFY DATA`

## I. Disk Imaging and Hash Verification
Focus area:
- hidden or unmounted storage;
- forensic imaging;
- source and image hash comparison;
- preservation of original evidence.

Typical actions:
- identify the correct device with `lsblk` or the platform storage tools;
- create an image with an approved imaging command;
- calculate SHA-512 or another assignment-required hash for source and image;
- compare results and record the evidence path.

Operational pattern:
`IDENTIFY DEVICE -> IMAGE -> HASH SOURCE AND IMAGE -> COMPARE -> PRESERVE`

## J. Archive Recovery and File Signature Repair
Focus area:
- malformed or password-protected archives;
- known-plaintext ZIP recovery in an authorized lab;
- altered file headers or signatures;
- recovery of files whose metadata no longer matches their content.

Typical actions:
- preserve the original archive or file before analysis;
- inspect archive members and file headers;
- use approved recovery tools such as 7-Zip or pkcrack only within the lab;
- validate the recovered file type and contents after extraction.

Operational pattern:
`PRESERVE -> IDENTIFY FORMAT -> ANALYZE HEADER OR ARCHIVE -> RECOVER -> VALIDATE`

## K. Packet Capture Analysis
Focus area:
- suspicious hosts and conversations;
- repeated ARP activity;
- SYN floods and unusual connection patterns;
- anomalous SSH or protocol behavior.

Typical actions:
- open the capture in Wireshark;
- review protocol hierarchy, endpoints, conversations, and expert information;
- filter the relevant protocol or host;
- correlate timestamps and packet behavior before flagging a finding.

Operational pattern:
`OPEN CAPTURE -> FILTER -> CORRELATE HOSTS AND EVENTS -> CLASSIFY ACTIVITY -> DOCUMENT`

## L. GPO and Identity Governance
Focus area:
- account and password policy;
- removable-media and Run restrictions;
- organizational units and group-based policy;
- share mapping and access control.

Typical actions:
- define the requirement and affected scope;
- create or update the OU, group, or GPO;
- link and apply the policy at the correct scope;
- validate both policy application and effective access.

Operational pattern:
`DEFINE SCOPE -> CONFIGURE GPO/OU -> APPLY GROUPS -> REFRESH POLICY -> VALIDATE EFFECTIVE STATE`

## M. Linux Host and SSH Hardening
Focus area:
- hostname and DNS consistency;
- static addressing and routes;
- local user and sudo administration;
- SSH cipher, key-exchange, and MAC configuration.

Typical actions:
- record the current host and network state;
- update only the required host, resolver, route, or SSH setting;
- validate syntax before restarting a service;
- confirm connectivity and authorized access after the change.

Operational pattern:
`BASELINE -> CHANGE HOST OR SERVICE CONFIG -> VALIDATE SYNTAX -> RESTART IF NEEDED -> TEST ACCESS`

# 3. Standard Decision Workflow

Use this sequence for every challenge:

`OBJECTIVE -> SYSTEM IDENTIFICATION -> EVIDENCE -> HYPOTHESIS -> REMEDIATION -> TEST -> CONFIRM -> DOCUMENT`

At each stage, ask:
- What is the actual problem?
- Which system is affected?
- What evidence proves the issue?
- What action restores service or compliance?
- How do I verify the fix?
- What screenshots or notes are needed for grading?

# 4. Evidence and Submission Standard

The learner should always produce evidence of:
- login to the correct VM or device;
- system state before the fix;
- the exact command or action taken;
- result after remediation;
- final state confirmation;
- screenshots for grading or Canvas submission.

Evidence is not optional in a range challenge; it is part of the deliverable.

# 5. Common Commands and Tools

## Windows / networking
- `ipconfig /all`
- `netsh interface show interface`
- `netsh interface ip set address name="Ethernet0" static ...`
- `ping`
- `tracert`
- `arp -a` when relevant

## Linux / networking
- `ip addr show`
- `ip link show`
- `sudo ip addr add ...`
- `sudo ip route add default via ...`
- `sudo ip addr flush dev ...`

## File transfer and evidence
- `scp source user@host:/path`
- `ls`
- `cd /d E:\`
- `cp` or `mv` on Linux hosts

## Malware / forensics
- ClamWin scan
- File Explorer with hidden files and extensions enabled
- `pdfid` for PDF metadata scanning
- archive or tar creation in the lab
- `sha512sum` or the platform-approved hashing utility
- `dd` only when the assignment explicitly requires device imaging
- 7-Zip or another approved archive inspection tool
- Wireshark for packet capture analysis

## Active Directory and access control
- Server Manager
- Active Directory Users and Computers
- Group Policy Management
- File Explorer share permissions

## Linux administration
- `sudo adduser username`
- `sudo visudo`
- `sudo yum update`
- `sudo apt-get update && sudo apt-get upgrade`
- `hostnamectl status`
- `ip addr show`
- `ip route show`
- `sshd -t`

## Database
- `SHOW DATABASES;`
- `SELECT VERSION();`
- `mysqldump -u root -p database > backup.sql`
- `mysql -u root -p database < backup.sql`

# 6. Reusable Challenge Execution Template

Use this template when solving a challenge:

```text
Challenge Name:
Objective:
Affected System:
Evidence Collected:
Problem Statement:
Root Cause:
Remediation Steps:
Verification Steps:
Final State:
Screenshots Taken:
Submission Ready:
```

This template can be reused across:
- network restoration;
- domain access issues;
- malware cleanup;
- evidence extraction;
- system hardening;
- backup & restore tasks.

# 7. Risk and Safety Rules

- Do not make unauthorized configuration changes outside the lab scope.
- Do not restore a service without validating the cause.
- Do not delete evidence before preserving it.
- Do not assume a file is benign because it is visible; confirm with the challenge objective.
- Do not rely on memory alone; record the evidence path.
- Do not treat a change as complete until a repeatable check confirms it.

# 8. Challenge-Specific Lessons Learned

From the example challenges, the most repeated success pattern is:
- identify the correct system;
- confirm the exact broken setting;
- fix the smallest root cause;
- validate reachability, access, or integrity;
- document with screenshots and proof.

The most common failure patterns are:
- wrong interface name;
- wrong default gateway;
- stale configuration left behind;
- using the wrong credentials for local vs domain access;
- deleting evidence before preserving it;
- assuming the fix worked without testing.

# 9. Next-Step Buildout

This framework should be used as the foundation for a future challenge skill that includes:
- a mission objective layer;
- a system-specific remediation matrix;
- a template for per-lab evidence logs;
- a skill-specific command cheat sheet;
- a grading checklist tied to Canvas submission.

This is the first reusable package to build from the prior-year challenge notes.
