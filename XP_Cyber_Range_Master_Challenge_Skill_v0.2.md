---
name: xp-cyber-range-master-challenge-skill
description: >
  Master challenge skill for XP Cyber Range and NICE-style labs. Converts a library of
  past challenge examples into a reusable operational framework for network restoration,
  workstation troubleshooting, malware cleanup, Active Directory configuration, Linux
  administration, hardening, forensics, and evidence submission.
---

# XP Cyber Range Master Challenge Skill
## Version 0.2 — Expansion Candidate

## Status
**Skill status:** RESEARCH CANDIDATE / EXPANSION PHASE  
**Authority:** Domain skill; subordinate to assigned instructions, platform rules,
user safety, academic integrity, and the operational doctrine of VesselFramework.  
**Runtime state:** This document is a reusable challenge framework and should be updated as
new challenge families are encountered.

# 1. Purpose

This skill provides a mission-oriented method for solving XP Cyber Range challenges that contain
mixed tasks across multiple systems and roles. It supports the operational pattern used in real
training events:

`ACCESS -> IDENTIFY -> VALIDATE -> FIX -> VERIFY -> DOCUMENT -> SUBMIT`

The skill collects prior examples into a larger reusable framework so it can scale beyond a
single challenge and become a general operating model for future labs.

# 2. Governing Order

Use this precedence when instructions conflict:

1. Assignment brief and grading rubric
2. Platform and environment rules
3. Instructor or curator requirements
4. Domain and course material
5. Challenge-specific notes and evidence
6. Skill framework and operational method

The skill is designed to support execution, not replace the official task brief.

# 3. Framework Integration

This skill is aligned with the VesselFramework package and builds on the same design principles:
- objective-first actions;
- evidence before conclusion;
- root-cause resolution rather than symptom chasing;
- explicit task boundaries and stop conditions;
- provenance-aware documentation;
- repeatable service restoration and verification;
- screenshot-backed submission quality.

It sits alongside the broader package framework as a domain adapter for cyber range operations.

# 4. Challenge Taxonomy

## A. Network Recovery & Configuration Management
Problems include:
- broken static IP configuration;
- subnet mask mismatch;
- gateway problems;
- interface misidentification;
- route failure between systems;
- broken domain reachability;
- stale or duplicate addresses.

Typical workflow:
1. identify the affected interface;
2. verify the current IP settings;
3. confirm the correct gateway and subnet;
4. flush stale addresses if needed;
5. set the correct values;
6. validate via ping, tracert, and route inspection.

Example commands:
- `ipconfig /all`
- `ip link show`
- `ip addr show`
- `sudo ip addr add 172.16.30.100/24 dev ens32`
- `sudo ip route add default via 172.16.30.250`
- `sudo ip addr flush dev ens32`
- `netsh interface show interface`
- `netsh interface ip set address name="Ethernet0" static 172.16.30.55 255.255.255.0 172.16.30.250`

## B. Workstation Troubleshooting & Helpdesk Tasks
Problems include:
- reversed mouse buttons;
- hidden desktop icons;
- missing mapped drives;
- internet issues caused by bad proxy settings;
- local account access when domain authentication fails.

Typical workflow:
1. reproduce the issue from the user report;
2. confirm the configuration state;
3. fix only the specific setting that breaks access;
4. retest the service or function.

## C. Malware Triage & Dangerous Drive
Problems include:
- infected removable media;
- ClamWin detections;
- EICAR signatures or malicious files on mapped drives;
- persistent malware artifacts in user directories.

Typical workflow:
1. inspect the drive and confirm mount state;
2. enable hidden files and extensions;
3. run a malware scan;
4. identify infected items;
5. remove them by secure method;
6. run a validation scan to confirm no detections remain.

Example actions:
- scan E: drive with ClamWin;
- remove infected files using Shift + Delete;
- verify clean state after rescan.

## D. Forensic File Recovery & Evidence Handling
Problems include:
- unassigned volume letters;
- hidden or off-grid file evidence;
- files modified after a defined cutoff date;
- preserving evidence while transporting it securely.

Typical workflow:
1. use Disk Management to reveal all partitions;
2. assign a drive letter where required;
3. enable hidden files and extensions;
4. locate evidence by date or suspicious file type;
5. copy files without modifying original evidence;
6. transfer to the evidence host using secure methods;
7. preserve chain of custody and file integrity.

Example actions:
- assign drive letter E to FlashDrive;
- inspect `E:\Finances` for relevant files;
- use `scp` to move files to a secure desktop or evidence location;
- create archive files for later review;
- use `pdfid` to inspect PDF metadata.

## E. Identity, Access, and Domain Control
Problems include:
- user accounts missing proper groups;
- incorrect permissions on file shares;
- user lockout or disabled accounts;
- access restrictions not aligned with role requirements;
- login policies not enforced.

Typical workflow:
1. identify the required role or system access model;
2. define the correct group or permission assignment;
3. update AD group membership;
4. restrict or disable accounts when needed;
5. validate the domain and share access model.

Example actions:
- create groups such as HRSec and AccountingSec;
- deny unauthorized access to restricted groups;
- disable Rob's account;
- set log-on restrictions for specific machines.

## F. Linux Administration & System Updates
Problems include:
- user accounts missing required privileges;
- package or service updates not completed;
- web server misconfiguration or outdated service version;
- sudo access not enacted.

Typical workflow:
1. create or verify the user account;
2. grant privileges in a safe way;
3. update packages or services;
4. validate service behavior after the change.

Example commands:
- `sudo adduser gthatcher`
- `sudo visudo`
- `sudo yum update`
- `sudo apt-get update && sudo apt-get upgrade`

## G. Security Hardening & Vulnerability Mitigation
Problems include:
- outdated protocol exposure;
- SMB1 vulnerabilities;
- unpatched systems;
- known exploit paths into the domain environment.

Typical workflow:
1. identify the vulnerability and affected service;
2. apply the proper patch or disable the risky legacy feature;
3. validate the control state;
4. confirm the attack vector is mitigated.

Example actions:
- install software updates;
- disable SMB1 with `Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force`;
- validate with `Get-SmbServerConfiguration | Select EnableSMB1Protocol`.

## H. Database Backup, Restore, and Recovery
Problems include:
- corrupted or missing database environment;
- need to secure a backup before recovery;
- restore backup to a separate server or test database;
- verify imported data integrity.

Typical workflow:
1. locate the database engine and version;
2. create a backup dump;
3. transfer it to the recovery host;
4. create the target restore database;
5. import the dump;
6. validate database tables and accessibility.

Example commands:
- `SHOW DATABASES;`
- `SELECT VERSION();`
- `mysqldump -u root -p wordpress > C:\dump.sql`
- `scp dump.sql root@172.16.30.79:/ftp/public/prodbackup`
- `mysql -u root -p wordpresstest < /ftp/public/prodbackup/dump.sql`

# 5. Operational Mission Flow

Use this flow across all challenge types:

`MISSION -> STATE CHECK -> ROOT CAUSE -> CORRECTIVE ACTION -> VALIDATION -> EVIDENCE -> SUBMISSION`

## Step-by-step mission sequence
1. Understand the challenge objective.
2. Identify the system, network segment, or asset involved.
3. Determine the actual breakage and whether it is technical, access, policy, or configuration-related.
4. Record current evidence before making changes.
5. Apply the least disruptive fix.
6. Retest the exact function that was broken.
7. Confirm with a second validation if the issue is high impact or critical.
8. Capture screenshots and notes for grading.
9. Submit only when the evidence package is complete.

# 6. Decision Matrix

## If the issue is network reachability
Check:
- IP configuration;
- gateway; 
- subnet mask; 
- route table;
- interface name;
- domain controller reachability.

## If the issue is workstation usability
Check:
- mouse settings;
- desktop icon settings;
- share mapping;
- proxy settings;
- user profile or local credentials.

## If the issue is access control
Check:
- AD group membership;
- file share permissions;
- log-on restrictions;
- account status;
- GPO policy enforcement.

## If the issue is evidence recovery
Check:
- volume assignment;
- hidden items and extensions;
- file age and timestamps;
- secure transfer path;
- file integrity after copy.

## If the issue is malware or malicious files
Check:
- scan result counts;
- file path and type;
- whether the file is generated or user-created;
- whether malicious content is in a hidden or alternate drive.

## If the issue is patching or mitigation
Check:
- vulnerable service version;
- system update status;
- legacy protocol exposure;
- the correct remediation action.

# 7. Command and Tool Cheat Sheet

## Windows diagnostics
- `ipconfig /all`
- `ping`
- `tracert`
- `netsh interface show interface`
- `netsh interface ip set address name="Ethernet0" static ...`
- `Control Panel > System and Security > Windows Update`
- `Server Manager`
- `Active Directory Users and Computers`
- `Group Policy Management`

## Linux diagnostics
- `ip addr show`
- `ip link show`
- `sudo ip route add default via ...`
- `sudo ip addr flush dev ...`
- `ls`
- `cd`
- `sudo yum update`
- `sudo apt-get update && sudo apt-get upgrade`
- `sudo adduser username`
- `sudo visudo`

## File transfer and evidence movement
- `scp file user@host:/path`
- `cp`
- `mv`
- `tar` or archive tools

## Forensics and malware tools
- ClamWin
- `pdfid`
- File Explorer with hidden items enabled
- Disk Management
- file timeline and date checks

## Database
- `SHOW DATABASES;`
- `SELECT VERSION();`
- `mysqldump -u root -p database > backup.sql`
- `mysql -u root -p database < backup.sql`

# 8. Evidence Capture Standard

Every challenge run should produce a visible record of:

```text
Challenge Name:
System / VM involved:
Problem observed:
Evidence before fix:
Action taken:
Validation after fix:
Final state:
Screenshots collected:
Submission package ready:
```

Evidence should include:
- login screenshots;
- VM screen with affected configuration;
- command output proving the fix;
- final state screenshot; 
- any submission confirmation or grading artifact.

If a result cannot be shown, it should be treated as unverified.

# 8A. Standard Challenge Intake Template

Use this template for every new XP challenge entry:

```text
CHALLENGE INTAKE
Challenge name:
Challenge family:
Date:
System or VM(s):
Objective:
Initial state:
Observed problem:
Likely root cause:
Commands used:
Fix steps taken:
Validation steps:
Outcome:
Evidence captured:
Screenshots stored:
Submission status:
Notes / follow-up:
```

This template is the standard intake record for the framework and should be appended to each new challenge document.

# 9. Lab Completion Checklist

Before submission, verify:

```text
[ ] Correct VM identified
[ ] Objective understood
[ ] Root cause identified
[ ] Required fix applied
[ ] Validation performed
[ ] Evidence captured
[ ] Screenshots saved
[ ] Submission checked
[ ] Final result matches assignment ask
```

# 10. Common Failure Patterns

Watch for these repeated mistakes:
- wrong interface name used for IP changes;
- stale IP or default route left behind;
- domain credentials used when local auth is required;
- evidence deleted before backup or copy;
- fix applied without verifying service restoration;
- incomplete screenshot set for Canvas grading;
- assuming a challenge is complete without final confirmation.

# 10A. Standard Challenge Entry Format

Each new XP challenge should be recorded in this format:

```text
# Challenge Title
## Summary
- Objective:
- Affected systems:
- Root cause:
- Outcome:

## Actions Taken
1. 
2. 
3. 

## Commands Used
- 
- 
- 

## Validation
- 
- 

## Evidence
- screenshot 1
- screenshot 2
- command output

## Submission Notes
- Canvas submission:
- final status:
```

This keeps every challenge entry consistent and easy to expand.

# 11. Challenge Matrix for Future Expansion

Use this matrix to add new XP challenge examples without creating a new disconnected document.

```text
CHALLENGE FAMILY | PRIMARY SYSTEMS | COMMON ROOT CAUSE | KEY COMMANDS | VALIDATION | EVIDENCE
Network Recovery | Fileshare, Workstation, Domain Controller, Joomla | wrong IP, subnet, gateway, routing | ipconfig, ip addr, netsh, ping, tracert | reachability test | screenshots of config + ping result
Malware Triage | Workstation-Desk | infected files, hidden malware | ClamWin, File Explorer, Shift+Delete | clean scan result | before/after scan screenshots
Forensic Discovery | FlashDrive, Security Desk | hidden partitions, file age, transfer integrity | Disk Management, scp, ls, pdfid | evidence present in secure folder | file transfer + archive screenshots
Helpdesk Troubleshooting | WorkstationDesk | mouse, icons, proxy, drive mapping | Settings, File Explorer, Internet Options | service restored | before/after screenshots
AD & Access Control | Domain Controller | bad groups/permissions, account restrictions | Server Manager, ADUC | access matches role | group membership and share permission screenshots
Linux Admin | Prod-Web, Backup, Prod-Joomla | user creation, sudo, outdated service | adduser, visudo, yum, apt-get | service functions after update | command output + service proof
Hardening | Domain Controller | SMB1 vulnerability, patching | Windows Update, PowerShell Set-SmbServerConfiguration | exploit path closed | config check screenshot
Database Recovery | Database VM, Backup Server | broken backup or restore flow | mysqldump, scp, mysql | DB imported and tables visible | dump + restore output screenshot
Disk Imaging | Linux forensic host, source device | unmounted or hidden evidence device | lsblk, dd, sha512sum | image hash matches recorded source hash | device identification, hash output, evidence path
File Signature Repair | Windows workstation, evidence drive | altered header or metadata | hex editor, file, 7-Zip | file type and recovered content validate | original copy, header view, recovered file
Archive Recovery | Windows/Linux analysis host | encrypted or malformed archive | 7-Zip, pkcrack, unzip | authorized recovery extracts expected file | archive copy, tool output, extracted result
Packet Analysis | Wireshark analysis host | suspicious ARP, SYN, or SSH traffic | Wireshark statistics, filters, conversations | finding tied to host, packets, and timestamps | filtered view, endpoint/conversation evidence
GPO Governance | Domain Controller, managed workstation | policy scope or access assignment error | GPMC, ADUC, gpupdate, gpresult | policy applies and effective access matches role | GPO scope, result, access test
Linux/SSH Hardening | Linux server, SSH client | weak service or network configuration | hostnamectl, ip, sshd -t, systemctl | syntax, connectivity, and authorized access pass | before/after config and validation output
```

When adding a new challenge, append a new row and update the command, validation, and evidence fields.

# 12. Consolidated Operating Playbook

The reusable workflow to apply to every new XP Cyber Range challenge is:

```text
1. Read the objective and determine the system role.
2. Identify the affected VM or asset and the expected service state.
3. Collect baseline evidence before touching the system.
4. Diagnose the likely root cause using logs, config, permissions, version, or network state.
5. Apply the narrowest correct remediation.
6. Re-test the exact broken behavior.
7. Confirm the system is functioning under the task requirement.
8. Capture screenshots and command output for proof.
9. Verify the final state matches the objective.
10. Submit only after the evidence package is complete.
```

This playbook is the long-term structure for future challenge entries.

# 13. Additional Challenge Families Captured from Recent Labs

The recent examples add several new challenge families that should be incorporated into the master framework.

## A. Malware Cleanup and Hidden Persistence
Examples include:
- ClamWin scans on a mapped drive used to find four EICAR signatures;
- removal of hidden malicious files from the E: drive;
- checking for suspicious executable paths such as `C:\Windows\System32\com\net\gov.bat`;
- identifying and deleting malicious content that persists in the Recycle Bin or in hidden directories.

Operational pattern:
`SCAN -> HIDE/SHOW FILES -> DELETE MALWARE -> EMPTY RECYCLE BIN -> RESCAN -> VERIFY CLEAN STATE`

## B. Windows Forensics and File Signature Repair
Examples include:
- editing file signatures in a hex editor to restore image headers;
- examining suspicious archive content and extracting files from password-protected or malformed archives;
- using 7-Zip to inspect and recover content from corrupted archive structures;
- recovering data from files whose signatures or metadata had been altered.

Operational pattern:
`IDENTIFY SUSPICIOUS FILE -> EXAMINE HEADER/CONTENT -> VALIDATE FORMAT -> RECOVER DATA -> VERIFY SIGNATURE/STRUCTURE`

## C. Backup, Restore, and Database Recovery
Examples include:
- using `mysqldump` to create a database backup;
- moving backup files to a remote server using `scp`;
- restoring a dump into a newly created database;
- verifying database creation and working tables.

Operational pattern:
`BACKUP -> TRANSFER -> CREATE TARGET -> IMPORT -> VERIFY TABLES`

## D. Disk Imaging and Hash Verification
Examples include:
- identifying hidden or unmounted drives with `lsblk`;
- creating a forensic image using `dd`;
- generating SHA-512 hashes for the source device and the image;
- comparing hashes to prove image integrity.

Operational pattern:
`IDENTIFY DRIVE -> CREATE IMAGE -> HASH SOURCE AND IMAGE -> COMPARE -> PRESERVE EVIDENCE`

## E. Password Cracking and Archive Decryption
Examples include:
- using `pkcrack` against a ZIP archive with a known plaintext file;
- creating a known-good archive using a clean copy of a file inside the archive;
- using a matching plaintext file to derive the encryption state and recover the archive;
- transferring recovered files back to the workstation and verifying the results.

Operational pattern:
`IDENTIFY KNOWN-PLAINTEXT -> CREATE MATCHING ARCHIVE -> RUN CRACKING TOOL -> DECRYPT -> EXTRACT -> VERIFY`

## F. Packet Capture Analysis and Network Triage
Examples include:
- reviewing pcap files in Wireshark;
- using statistics, expert information, conversations, and endpoints to identify suspicious hosts;
- detecting repeated ARP requests, SYN floods, and anomalous SSH behavior;
- flagging a host as malicious based on repeated suspicious patterns and packet timing.

Operational pattern:
`OPEN PCAP -> REVIEW PROTOCOL FLOW -> IDENTIFY ANOMALY -> TRACE HOSTS AND EVENTS -> FLAG SUSPICIOUS ACTIVITY`

## G. Hardening and Vulnerability Remediation
Examples include:
- patching vulnerable Linux or Windows systems;
- disabling SMB1 to mitigate EternalBlue exposure;
- updating package repositories and system services;
- adjusting SSH settings to harden weak ciphers, key exchange algorithms, and MACs.

Operational pattern:
`IDENTIFY VULNERABILITY -> CHECK VERSION/CONFIG -> PATCH OR DISABLE -> VALIDATE CONFIG -> CONFIRM MITIGATION`

## H. GPO and Identity Governance
Examples include:
- creating GPOs for account policy enforcement;
- restricting external media, Run access, and network-drive mapping;
- creating OUs and applying group-based policies;
- mapping shares to drive letters from the domain level;
- assigning share permissions and restricting user access to specific files.

Operational pattern:
`DEFINE REQUIREMENT -> CREATE GPO/OU -> ASSIGN GROUPS -> APPLY POLICIES -> VALIDATE ACCESS`

## I. Linux Administrative Hardening
Examples include:
- changing hostnames and DNS entries;
- setting static network configuration on Linux systems;
- creating users with home directories;
- granting sudo rights;
- adjusting `/etc/hosts`, `/etc/resolv.conf`, and SSH settings for connectivity and control.

Operational pattern:
`CONFIGURE HOST -> UPDATE DNS -> SET IP/GATEWAY -> CREATE USER -> GRANT PRIVILEGES -> VALIDATE ACCESS`

# 14. Updated Source References and Research Links

Use the following updated references as the starting set for future challenge expansion and verification:

- Microsoft Learn: SMB Server Configuration
  - https://learn.microsoft.com/en-us/powershell/module/smbshare/set-smbserverconfiguration

- Microsoft Learn: Netsh interface IP command reference
  - https://learn.microsoft.com/en-us/windows-server/networking/technologies/netsh/netsh-interface-ip

- CISA: Risks associated with SMBv1
  - https://www.cisa.gov/news-events/alerts/2017/04/14/risks-associated-use-smbv1

- Wireshark User Documentation
  - https://www.wireshark.org/docs/

- Wireshark Display Filter Reference
  - https://www.wireshark.org/docs/dfref/

- pkcrack project repository
  - https://github.com/keyunluo/pkcrack

- pkcrack README and usage documentation
  - https://github.com/keyunluo/pkcrack#readme

- Linux documentation and administration references
  - https://www.linux.org/docs/

- Linux handbook: hostname and networking change references
  - https://linuxhandbook.com/

- Linuxize: change hostname on Linux
  - https://linuxize.com/post/how-to-change-hostname-in-linux/

- Linux handbook: set DNS and host file references
  - https://linuxhandbook.com/sudo-unable-resolve-host/

- OpenSSH and security hardening references
  - https://www.openssh.com/manual.html

- Wireshark sample captures and analysis method references
  - https://www.wireshark.org/resources#sample-captures

- Microsoft docs: security and network hardening guidance
  - https://learn.microsoft.com/en-us/windows-server/security/

- Microsoft docs: Windows update and patch management
  - https://learn.microsoft.com/en-us/windows/security/operating-system-security/system-security/patch-management/

- Linux package management guidance (apt/yum/zypper)
  - https://documentation.ubuntu.com/server/how-to/software/package-management/
  - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/
  - https://en.opensuse.org/Package_Management

- Hashing and forensics references
  - https://www.nsa.gov/
  - https://www.iana.org/assignments/media-types/media-types.xhtml

- NTFS and ACL references for share permission changes
  - https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/ntfs-permissions

- Active Directory and GPO references
  - https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/appendix-l--group-policy-recommendations
  - https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-active-directory-users-and-computers

- SSH and Linux access hardening references
  - https://www.ssh.com/academy/ssh/sshd_config
  - https://www.cyberciti.biz/faq/how-to-change-shell-to-bash/

# 15. Malware Behavior Triage Capability

The package includes a non-executing static analyzer in `vessel/malware_triage.py` for suspicious
Python source samples. It is intended for authorized range analysis, evidence capture, and
remediation planning.

The analyzer can flag indicators associated with:
- command execution through subprocess calls;
- socket-based control channels and encoded file transfer;
- keyboard capture and SMTP exfiltration;
- logon persistence;
- ARP manipulation and packet capture;
- network discovery and MAC-address changes.

Operational workflow:

`PRESERVE SOURCE -> HASH OR RECORD SAMPLE -> STATIC TRIAGE -> REVIEW LINE EVIDENCE -> CONTAIN -> VERIFY`

Safe operating boundaries:
- analyze source text without importing or executing it;
- use quarantined fixtures or authorized lab samples;
- do not capture real keystrokes, send traffic, alter MAC addresses, or contact external systems;
- preserve the original sample and report before remediation;
- treat a clean signature result as incomplete assurance when the sample or context is limited.

The resulting findings can be converted into the package scan-report format with remediation and
verification fields, making them suitable for challenge evidence and submission records.

# 16. Final Skill Summary

The XP Cyber Range challenge is not a single task; it is a collection of operational problem sets that
a learner must complete across multiple systems and domains. This master skill centralizes the pattern:

`Observe -> Diagnose -> Repair -> Verify -> Document -> Submit`

It is the reusable base layer for future XP challenge work and should continue to expand as more labs are added.

This expanded version now incorporates the new malware, archive recovery, imaging, hash validation,
packet capture investigation, Linux administration, hardening, and GPO challenge families from the most recent lab notes while keeping every new addition tied to verifiable source material.
