# S2: Add a bastion host (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 39
- **Files written in the testbed:** none

Check against scenarios/s02-aws-open-ssh/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 3.5/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 4 | The bastion accepts SSH from anywhere, uses an unpinned AMI lookup, and adds a required variable that breaks existing applies. |
| ☁️ AWS architect | 3 | The bastion accepts SSH from anywhere on the internet using long-lived key pairs, and it has no audit logging or encrypted root volume. |
| 🗄️ DBA | – | Not relevant |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🔴 `infra/bastion.tf:68` Don't open port 22 to 0.0.0.0/0. Limit it to a variable allowlist of on-call CIDRs, or replace SSH with SSM Session Manager and drop the…
- 🟠 `infra/variables.tf:107` The new required bastion\_key\_name has no default, so existing plans and applies will fail. Give it a default or make the bastion conditional with a…
- 🟡 `infra/bastion.tf:80` With most\_recent = true, a new AMI will replace the bastion on a later apply. Pin the AMI or add lifecycle ignore\_changes = \[ami\].

**☁️ AWS architect**
- 🔴 `infra/bastion.tf:68` Remove the 0.0.0.0/0 SSH ingress. Use SSM Session Manager with no inbound rules, or limit SSH to a variable CIDR allowlist such as the corporate…
- 🟠 `infra/bastion.tf:93` Drop the EC2 key pair and attach an IAM instance profile with AmazonSSMManagedInstanceCore, so access goes through IAM and sessions are logged to CloudWatch or…
- 🟡 `infra/bastion.tf:88` Add root\_block\_device with encrypted = true. Pin the AMI or ignore\_changes on ami so a new AMI release does not replace the bastion.

<sub>Reviewed branch scenario/s02-aws-open-ssh vs main, including uncommitted changes.</sub>

Want me to help fix these findings?
