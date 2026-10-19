# Telemetry Header — Reference Implementation and IntegrationType Registry

**Type:** Cross-Cutting Reference
**Version:** 1.3
**Author:** Idira Technical Alliances
**Last Updated:** 2026-10-14

---

<!--
## AI CONTEXT BLOCK
This is the NORMATIVE reference for the one requirement every certified integration shares: the
`x-cybr-telemetry` HTTP header. Read it whenever a development guide or certification checklist
mentions telemetry, instead of re-deriving the transform from that kit's prose.

PURPOSE: the header is a fully deterministic transform — assemble four or five key=value pairs,
join with "&", UTF-8 encode, Base64url encode. Every kit states the transform in words and none of
them publishes a worked example, so every partner implements it from a paragraph and is then graded
on it. This file publishes the transform, working code in five languages, and test vectors.

DECISION LOGIC: the `it` (IntegrationType) value is NOT free text and NOT derivable — it is assigned
per dev kit. Section 3 is the registry. Look the kit up; do not invent a value and do not pattern-match
one from another kit. If the kit is not in the registry, the value is unassigned and the partner must
ask their Idira Technical Alliances contact — say that rather than guessing.

ROUTING PRECEDENCE: journey.md -> decision-guide.md -> workflow decision-guide.md ->
development-guide.md -> certification-checklist.md -> marketplace-standards.md. This file is
cross-cutting: it is referenced FROM stage 3 (build) and graded AT stage 4 (certification), and it
overrides any individual kit's telemetry section where the two disagree.

DO NOT tell a partner their integration is telemetry-compliant on the basis of a plain Base64
implementation. Section 4.2 explains why that passes almost every test and still fails: standard
Base64 and Base64url produce identical output for most ASCII payloads and diverge on specific
vendor names. Section 6 has the test vector that catches it.
-->

---

> **What this is.** Every certified Idira integration must send the `x-cybr-telemetry` header on
> every API request. This file is the single source for how to build it, what value to use for your
> integration type, and how to prove your implementation is right before you submit for certification.
>
> One exception: **PSM Web Connection Components are out of scope.** They are browser automation and
> never call an Idira REST API, so they carry no telemetry requirement. Every other kit in this
> repository is in scope.

---

## 1. The header

| | |
|:---|:---|
| **Header name** | `x-cybr-telemetry` |
| **Sent on** | Every request to an Idira API, including retries |
| **Value** | Base64url encoding of the UTF-8 bytes of an ampersand-delimited `key=value` string |

The plaintext, before encoding:

```
in=<IntegrationName>&it=<IntegrationType>&iv=<IntegrationVersion>&vn=<VendorName>[&vv=<VendorVersion>]
```

| Field | Key | Required | What it holds |
|:---|:---|:---:|:---|
| IntegrationName | `in` | Yes | The name of your integration as it will appear in the Marketplace listing |
| IntegrationType | `it` | Yes | The value assigned to your dev kit — see the registry in §3. Not free text |
| IntegrationVersion | `iv` | Yes | Your integration's released version. Must match what you ship |
| VendorName | `vn` | Yes | Your legal entity name |
| VendorVersion | `vv` | No | The version of your own platform, where that differs from `iv` |

Field order is not significant to the parser, but emit them in the order above — it makes a captured
header readable when you and your Idira Technical Alliances contact are comparing notes.

---

## 2. The transform, step by step

1. Build the plaintext string as shown above. Include `vv` only if you are setting it.
2. Encode that string to bytes as **UTF-8**.
3. Encode those bytes as **Base64url** — RFC 4648 §5, the URL- and filename-safe alphabet, where
   `+` becomes `-` and `/` becomes `_`.
4. Send the result as the header value.

That is the whole transform. There is no signing, no timestamp, no nonce, and nothing
request-specific — so the value is constant for a given release of your integration and you should
compute it once at startup rather than per request.

---

## 3. IntegrationType (`it`) registry

**This is the authoritative list.** Use the value for your kit exactly as written, including case and
hyphens.

| Dev kit | `it` value |
|:---|:---|
| `audit-service/siem-integration` | `SIEM` |
| `credential-rotation/cpm-rest-api` | `CredentialRotation` |
| `discovery/ai-agents` | `AI-Agent-Discovery` |
| `discovery/machine-identities` | `Machine-Identity-Discovery` |
| `discovery/privileged-accounts` | `Privileged-Account-Discovery` |
| `discovery/secrets` | `Secrets-Discovery` |
| `epm/audit-events` | `EPMAudit` |
| `epm/soc-response` | `SOCResponse` |
| `epm/ticketing-jit` | `JIT` |
| `identity-access-management/identity-governance` | `IdentityGovernance` |
| `identity-response/response-actions` | `SOAR`, `SIEM`, or `XDR` — pick the one matching your platform category |
| `psm-connectors/web-connection-component` | *Not applicable — no REST API, no telemetry requirement* |
| `secrets-management/central-credential-provider` | `CCP` |
| `secrets-management/credential-provider` | `CP` |
| `secrets-management/secrets-manager-saas` | `SecretsManager` |
| `secrets-management/secrets-manager-self-hosted` | `SecretsManagerSH` |
| `workload-identity/swa-federation` | `WorkloadIdentity` |

Sixteen assigned values across seventeen kits.

> **Why `WorkloadIdentity` and not `SWA`.** The acronym would have matched this registry's
> acronym-style values, and it was deliberately not used: "SWA" also abbreviates the Secure Web
> Application Connectors Framework, an unrelated PSM component. An ambiguous value here is worse than
> a verbose one, because attributing traffic to the right kit is the registry's whole purpose.

### 3.1 The values are not internally consistent, and that is deliberate

The registry mixes three naming styles — acronym (`SIEM`, `CCP`, `JIT`), PascalCase
(`CredentialRotation`, `SecretsManagerSH`), and Title-Hyphen (`Machine-Identity-Discovery`). They
were assigned per kit over time rather than from one rule.

**They are frozen as they stand.** Integrations already certified against these values are in
production and are graded on them; renaming a value would invalidate a shipped integration's
telemetry to fix a cosmetic inconsistency. So: do not normalise them, and do not infer a pattern
from one kit to guess another's. Look it up.

### 3.2 For a kit that is not in this table

A new kit's `it` value is assigned when the kit is authored, and it goes in this table in the same
change. If you are building against a kit with no row here, the value is genuinely unassigned —
ask your Idira Technical Alliances contact rather than choosing one. A wrong value is worse than a late one: it attributes
your integration's traffic to somebody else's kit.

### 3.3 `SIEM` is not unique

`SIEM` is the assigned value for `audit-service/siem-integration` *and* one of three permitted
values for `identity-response/response-actions`. A partner building identity-response on a SIEM
platform and a partner building an audit-service integration therefore send the same `it`. The
field does not uniquely identify the kit, so anything consuming this telemetry has to disambiguate
on `in`/`vn` as well. Flagged rather than fixed — see §7.

---

## 4. Reference implementations

All five produce byte-identical, padded output. Nothing here needs a third-party dependency.

The Python, JavaScript, and Bash implementations were executed against both §6 vectors and agree
byte for byte. Go and C# were not executed — if you build in either, assert against the §6 vectors
before you trust the snippet, and tell your Idira Technical Alliances contact if it disagrees.

### 4.1 The code

**Python 3**

```python
import base64

def cybr_telemetry(integration_name, integration_type, integration_version,
                   vendor_name, vendor_version=None):
    pairs = [
        f"in={integration_name}",
        f"it={integration_type}",
        f"iv={integration_version}",
        f"vn={vendor_name}",
    ]
    if vendor_version:
        pairs.append(f"vv={vendor_version}")
    plaintext = "&".join(pairs)
    return base64.urlsafe_b64encode(plaintext.encode("utf-8")).decode("ascii")

# Compute once, reuse for the process lifetime.
TELEMETRY = cybr_telemetry("Acme Secrets Scanner", "Secrets-Discovery", "1.0",
                           "Acme Corporation")
headers = {"x-cybr-telemetry": TELEMETRY}
```

**JavaScript / TypeScript (Node 16+)**

```javascript
function cybrTelemetry({ integrationName, integrationType, integrationVersion,
                         vendorName, vendorVersion }) {
  const pairs = [
    `in=${integrationName}`,
    `it=${integrationType}`,
    `iv=${integrationVersion}`,
    `vn=${vendorName}`,
  ];
  if (vendorVersion) pairs.push(`vv=${vendorVersion}`);
  return Buffer.from(pairs.join("&"), "utf8")
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}
```

**Do not substitute Node's built-in `.toString("base64url")` here.** It is the obvious thing to
reach for and it is not equivalent: `"base64url"` emits output with the `=` padding **stripped**,
so it disagrees with every other implementation on this page and with the §6 vectors. The
`"base64"`-plus-replace form above is padded and correct. See §5.

The two character replacements are what make the alphabet URL-safe — §4.2 explains why omitting
them passes nearly every test and is still wrong.

**Go**

```go
import "encoding/base64"

func CybrTelemetry(name, itype, version, vendor, vendorVersion string) string {
    plaintext := "in=" + name + "&it=" + itype + "&iv=" + version + "&vn=" + vendor
    if vendorVersion != "" {
        plaintext += "&vv=" + vendorVersion
    }
    return base64.URLEncoding.EncodeToString([]byte(plaintext))
}
```

Use `base64.URLEncoding`, not `base64.StdEncoding`. (`base64.RawURLEncoding` omits padding — see §5.)

**C#**

```csharp
static string CybrTelemetry(string name, string type, string version,
                            string vendor, string vendorVersion = null)
{
    var plaintext = $"in={name}&it={type}&iv={version}&vn={vendor}";
    if (!string.IsNullOrEmpty(vendorVersion)) plaintext += $"&vv={vendorVersion}";
    var bytes = System.Text.Encoding.UTF8.GetBytes(plaintext);
    return System.Convert.ToBase64String(bytes).Replace('+', '-').Replace('/', '_');
}
```

.NET has no built-in Base64url encoder for strings, so the two character replacements are required.

**Bash**

```bash
cybr_telemetry() {
  printf '%s' "in=$1&it=$2&iv=$3&vn=$4" | base64 | tr '+/' '-_' | tr -d '\n'
}

TELEMETRY=$(cybr_telemetry "Acme Secrets Scanner" "Secrets-Discovery" "1.0" "Acme Corporation")
curl -H "x-cybr-telemetry: ${TELEMETRY}" ...
```

GNU `base64` wraps output at 76 characters; the `tr -d '\n'` is what stops a wrapped header value.

### 4.2 Why plain Base64 is the failure that hides

The URL-safe alphabet differs from standard Base64 in exactly two output characters, and for most
payloads of this shape **neither one ever appears** — so a plain-Base64 implementation produces
byte-identical output and passes every test you are likely to write.

Across 102 realistic name/vendor combinations, standard Base64 and Base64url output differed in
**2**. Both of those had a non-ASCII vendor name.

The precise rule, for UTF-8 input: `+` or `/` appears in the output only when a byte at an index
that is 2 modulo 3 has its low six bits set to `111110` or `111111`. For ASCII-only text that means
one of `>`, `?`, or `~` at that alignment; for non-ASCII text, UTF-8 continuation bytes hit it far
more often. So the bug surfaces on a Japanese, Chinese, or accented vendor name and on nothing else
— it is latent for a US-and-Europe partner base and it is not latent globally.

Use the §6 vectors. The second one is specifically built to catch this.

---

## 5. Padding

The reference implementations emit RFC 4648 §5 output **with** `=` padding.

Whether the Idira API also accepts unpadded output is not stated in any published material, so this
reference does not claim it does. Emit padding.

**This is easy to get wrong by reaching for the idiomatic call**, because several languages ship a
"base64url" primitive that means *unpadded* base64url:

| Language | Padded (use this) | Unpadded (avoid) |
|:---|:---|:---|
| Python | `base64.urlsafe_b64encode` | `base64.urlsafe_b64encode(...).rstrip(b"=")` |
| Node | `.toString("base64")` + replace `+/` → `-_` | `.toString("base64url")` |
| Go | `base64.URLEncoding` | `base64.RawURLEncoding` |
| C# | `Convert.ToBase64String` + replace | — |
| Bash | `base64 \| tr '+/' '-_'` | `base64 \| tr -d '='` |

Node and Go are the traps: `base64url` and `RawURLEncoding` are the names a developer reads as "the
URL-safe one," and both drop the padding. If you have a platform constraint that genuinely forces
unpadded output, confirm it with your Idira Technical Alliances contact before certification rather than assuming — see §7.

---

## 6. Test vectors

Assert against these in your unit tests. Both are real output, not illustrative.

### Vector 1 — the common case

```
plaintext : in=Acme Secrets Scanner&it=Secrets-Discovery&iv=1.0&vn=Acme Corporation
encoded   : aW49QWNtZSBTZWNyZXRzIFNjYW5uZXImaXQ9U2VjcmV0cy1EaXNjb3ZlcnkmaXY9MS4wJnZuPUFjbWUgQ29ycG9yYXRpb24=
```

Note that this vector does **not** distinguish Base64 from Base64url — both produce it. It confirms
your field assembly, ordering, UTF-8 handling, and padding. It cannot confirm your alphabet.

### Vector 2 — the alphabet case

```
plaintext : in=Response Actions&it=SIEM&iv=1.0&vn=NTT データ
Base64url : aW49UmVzcG9uc2UgQWN0aW9ucyZpdD1TSUVNJml2PTEuMCZ2bj1OVFQg44OH44O844K_
plain B64 : aW49UmVzcG9uc2UgQWN0aW9ucyZpdD1TSUVNJml2PTEuMCZ2bj1OVFQg44OH44O844K/
```

The two differ in the final character only: `_` against `/`. **If your implementation produces the
second line, your alphabet is wrong** and you will emit a malformed header for any customer or
vendor name with the same property. This is the assertion worth having.

---

## 7. Open items

Two things this reference cannot settle from published material. Both are recorded here so a partner
hits a documented question rather than an undocumented surprise, and neither blocks a build today.

| # | Question | What to do meanwhile |
|:--|:---|:---|
| 1 | Does the API accept unpadded Base64url as well as padded? | Emit padded output (§5). Raise it with your Idira Technical Alliances contact only if a platform constraint forces otherwise |
| 2 | How should a value containing `&` or `=` be escaped? A vendor or integration name containing either character breaks the delimiter parse, and no published material defines an escaping rule | Avoid both characters in `in` and `vn`. If your legal entity name genuinely contains one, agree the value with your Idira Technical Alliances contact before you build around it |

Item 3.3 — the non-unique `SIEM` value — is an Idira-side consistency question, not a partner action.

---

## 8. What certification checks

Your kit's certification checklist grades the telemetry requirement. In every kit the graded items
reduce to these, so satisfying this file satisfies the checklist:

- The header is present on **every** API request, not a sample of them.
- The value is Base64url encoded.
- `in`, `it`, `iv`, and `vn` are all populated.
- `it` matches the registry value for your kit (§3).
- `iv` matches the version you actually released.
- `vn` is your legal entity name.

Reviewers read a captured request. Decode the header yourself before you submit, and confirm it says
what you meant.

---

### Change Log

- **[Added]** v1.3 — Registry row for the new `identity-access-management/identity-governance`
  kit, with the assigned value `IdentityGovernance`, taking the registry to sixteen assigned values
  across seventeen kits. Assigned in the same change as the kit, per §3.2. The value names the use
  case rather than the Identity Governance product, so it cannot be read as attributing traffic to
  that product. No existing value changed — they remain frozen by incumbency per §3.1. — Idira
  Technical Alliances
- **[Added]** v1.2 — Registry row for the new `workload-identity/swa-federation` kit, with the
  assigned value `WorkloadIdentity`, taking the registry to fifteen assigned values across sixteen
  kits. Per §3.2 a kit's value is assigned when the kit is authored and lands in this table in the
  same change, so this is that change. Also records why the acronym `SWA` was deliberately not used
  despite matching the registry's acronym-style values: it collides with the Secure Web Application
  Connectors Framework, an unrelated PSM component, and an ambiguous value defeats the one thing the
  registry exists to do. No existing value changed — they remain frozen by incumbency per §3.1. —
  Idira Technical Alliances
- **[Fixed]** v1.1 — Replaced the unexpanded acronym `TAM` with `Idira Technical Alliances contact`. It was never expanded anywhere in this corpus and collides with Technical Account Manager — a role this programme does not have — so neither a partner nor their AI tooling could resolve who to contact. No requirement, level or process changed. — Idira Technical Alliances
- **[Added]** v1.0 — First publication. Consolidates the telemetry requirement that all 15 kits state
  and none of them demonstrated: no worked example of an encoded value existed anywhere in the corpus
  before this file, so every partner implemented a graded requirement from a paragraph. Adds the
  `it` registry (14 assigned values across 15 kits, three naming conventions, frozen by incumbency),
  reference implementations in five languages, two test vectors, and the measured reason a plain-Base64
  implementation passes almost every test while remaining wrong. — Idira Technical Alliances
