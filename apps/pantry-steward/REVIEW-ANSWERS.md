# Local review draft — not an official approval

Based on source inspection and the Windows tests in VALIDATION.md. The App Hub
scan packet is in build/review.json; no external reviewer ran.

1. **Claims:** main.splash implements onboarding, manually confirmed inventory,
   expiry ordering, local rule planning, plan acceptance, actual consumption and
   persistence. model.complete is connected to the official contract but live
   online answers were not tested. Listing explicitly says voice is unavailable,
   there is no OCR, and the app does not run when the shell is closed.
2. **Platform/category:** Windows was actually tested. lifestyle fits meal and
   pantry management. No mobile/macOS/Linux platform claim is made.
3. **Capabilities/hosts:** storage saves pantry.json and backups in the app jail;
   model supports the visible online-planning option through the official host.
   There are no direct outbound HTTPS hosts, no net grant and no microphone
   grant. The host, not the app, chooses model providers and handles credentials.
4. **Deception:** no login, key, payment or system-approval imitation is present.
   F is the app's own mark. Screenshots show the genuine official desktop,
   not a painted host. Local rule menus visibly identify their source.
5. **Instructions:** online_plan contains an explicit task for the model to
   produce constrained meal JSON. It is a functional app prompt, not a hidden
   instruction to reviewers. Inventory/profile text is sent as input data.
6. **Abuse:** no abusive wording or text directed at a private individual was
   found in the migrated source; test profiles are synthetic.
7. **Route: human-review.** Publisher identity and privacy text/URL require the
   author's confirmation; live AI remains unverified. Local test signing is not
   production release signing. Passing the automated gate is not competition
   admission or official store approval.
