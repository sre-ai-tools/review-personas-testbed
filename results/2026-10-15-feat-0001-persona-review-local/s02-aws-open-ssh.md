# S2: Add a bastion host (local, headless)

- **Pinned:** feat/0001-persona-review (f6f14ff)
- **Model:** Claude Code default
- **Exit code:** 0
- **Seconds:** 45
- **Files written in the testbed:** none

Check against scenarios/s02-aws-open-ssh/expect.md, skipping (CI) items.

---

<!-- review-personas -->
## 🧩 Persona review: 3.0/10 (advisory)

| Persona | Score | Summary |
|---|---|---|
| 🧑‍💻 App developer | 4 | The new bastion lets SSH in from any IPv4 address, adds a required variable with no default that breaks existing callers, and swaps the instance whenever Amazon publishes a new AMI. |
| ☁️ AWS architect | 2 | This change puts a public SSH bastion open to 0.0.0.0/0 in a single AZ, with no logging or alarms, and SSM Session Manager would avoid the need for it. |
| 🗄️ DBA | – | Not relevant |
| 🎨 UI developer | – | Not relevant |
| 🔌 API contract | – | Not relevant |

**🧑‍💻 App developer**
- 🔴 `infra/bastion.tf:39` Don't hard-code 0.0.0.0/0 for SSH. Add a variable for allowed CIDRs, validate that it isn't open to the world, or use SSM Session Manager instead.
- 🟠 `infra/variables.tf:48` The required bastion\_key\_name has no default, so existing tfvars and callers break. Give it a default or a toggle that makes the bastion optional.
- 🟠 `infra/bastion.tf:60` With most\_recent AMI lookup, every new AMI release replaces the bastion. Pin the AMI or add lifecycle ignore\_changes on ami.

**☁️ AWS architect**
- 🔴 `infra/bastion.tf:68` Port 22 is open to 0.0.0.0/0. Restrict ingress to a variable of trusted admin CIDRs, or better, drop the ingress rule and use SSM Session…
- 🟠 `infra/bastion.tf:88` Replace the key-pair public bastion with SSM Session Manager: attach an instance profile with AmazonSSMManagedInstanceCore, place it in a private subnet, and remove key\_name and…
- 🟠 `infra/bastion.tf:88` Encrypt the root volume (root\_block\_device encrypted = true). Send session/SSH logs to CloudWatch and alarm on login activity.

<sub>Reviewed branch scenario/s02-aws-open-ssh vs main, including uncommitted changes.</sub>

Want me to help fix these, starting with the SSH rule that's open to 0.0.0.0/0?
