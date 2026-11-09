# Design tokens & component API (TOK)

Rules for token tiers, token names, light/dark modes, component names, and props.

Each rule: **Why** it matters, then **Check**, what to verify in a design or in code.

**TOK-1 Three tiers: hex value → primitive → semantic. Components use semantics only.**
Why: AI reading a list of hex values has no idea what they mean or where they belong, so it guesses. With primitives alone, changing one usage cascades everywhere.
Check:
- Build primitives from a colour audit: collect every colour in use, sort them into families (grey, blue…), order each family light → dark, and name them `family-weight` (`grey-100…grey-500`, `blue-100…blue-400`).
- Semantic tokens alias primitives and carry purpose (`--ds-color-bg-fill → grey-100`, `--ds-color-bg-surface-recessed`).
- Components and screens reference semantic tokens only, with no hex or rgb literals.
- The payoff to aim for: Material Design 3 updates one semantic token and the change flows through Gmail, Drive, and Android with no hunting through components.

**TOK-2 Semantic token formula: `color-{element}-{priority}-{state}`.**
Check:
- element: `bg`, `bg-surface`, `bg-fill`, `text`, `border`, `icon`
- priority: `primary`, `secondary`, `tertiary`
- state: `default`, `hover`, `active`, `disabled`
- e.g. `color-bg-surface-secondary-hover`, `color-bg-fill-primary-active`, `color-text-primary-disabled`, `color-border-tertiary-default`, `color-icon-secondary-hover`
- Add a namespace prefix in CSS (`--ds-…`, or your system's prefix).
- The element names follow how a screen is built: `bg` is the product background, `bg-surface` layers on it for depth, and components on those surfaces have a `bg-fill` and a `border`, with `text` and `icon` on top.

**TOK-3 Light and dark are modes of the semantic layer.**
Check: a Primitives collection with no modes, grouped by slash (`color/grey/100`). A separate semantic collection with Light and Dark modes, where each token aliases a different primitive per mode. Switching appearance changes no component.

**TOK-4 Component names: `Base / Purpose / Size / State`.**
Why: "BTN" tells neither people nor AI anything.
Check: the base is a real descriptor (`Button`, not `BTN`). Purpose ∈ Primary, Secondary, Tertiary, Destructive. Size ∈ Large, Medium, Small. State ∈ Default, Hover, Active (+ Disabled, Focus). For example `Button / Secondary / Large / Default`; switching variants changes only one segment.

**TOK-5 Design properties = code props.**
Why: designing components with no regard for code doubles the team's workload.
Check: props are split by meaning: `variant` = emphasis (primary | secondary | tertiary), `tone` = intent (neutral | critical), `size` = T-shirt (sm | md | lg). The Figma component exposes the same three properties with the same values.
