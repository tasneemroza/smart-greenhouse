# Phase 6 — Strategy questions

**Pattern / focus:** Strategy.

**Read first:** [Guide 06](../../materials/guides/06-strategy.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example shipping quotes) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to irrigation (or lighting) policies, location context, and the automation API from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Strategy in plain language. How does the **context** use a strategy, and why must “choose which algorithm” stay separate from “run the algorithm”?

The Strategy pattern lets us choose between different algorithms without changing the main code. In our project it allows us to change the irrigation policy without rewriting the automation service.

2. Name the participants (**strategy**, **concrete strategies**, **context**, **client**). What goes wrong when all policies live as `if/elif` inside the context (or inside an HTTP router)?

The strategy is the common interface, and the concrete strategies are Conservative and Aggressive. The automation service is the context and the client uses the API. Keeping all policies in if/elif blocks makes the code harder to maintain and extend.

3. When should you use Strategy, and when should you skip it (one algorithm only; or the variation is a **lifecycle mode** rather than a chosen policy)?

We use Strategy when we need different algorithms that can be changed easily. We can skip it if there is only one algorithm. If behaviour changes according to lifecycle stages, State may be more suitable.

## B. This phase of the application

The decide(context) method returns an action and a reason. For example with low soil moisture, the aggressive strategy may recommend irrigation earlier while the conservative strategy waits until the moisture is lower.

5. Where do the numbers in `LocationAutomationContext` (or your equivalent) come from? Latest moisture may already be in `sensor_readings` from a manual read, the simulation sampler, or MQTT translation — why does this phase not add a scheduler or a broker? Why must strategies receive a plain context object, not SQLAlchemy rows or FastAPI types? Why are thresholds read from **zones**, not hardcoded in the strategy class?

The moisture values come from sensor_readings and thresholds come from the zone configuration. We reuse existing readings so no new scheduler or broker is needed. A plain context object keeps the strategies independent of the database and API. Zone thresholds allow each zone to have its own settings.

6. The active `strategy_key` is **persisted** per `location_id` (for example in `automation_rules`). Why must `POST .../automation/evaluate` use the **saved** key rather than a key the client sends only in that request? What happens on the next evaluate after the operator changes strategy but moisture stays the same?

The saved strategy_key ensures each location uses its configured policy. When the operator changes the strategy the next evaluation uses the new one. The recommendation may change even if the moisture reading stays the same.

7. Strategy **recommends** (irrigate / wait). It should not itself start a pump. Why keep **decide** separate from **execute**? Which later pattern is meant to carry out the action?

The strategy only recommends whether to irrigate or wait, it does not start the pump. Separating decisions from execution makes the code easier to test. A later Command pattern can represent the action to be executed.

## C. Compare, contrast, and scenarios

8. Contrast Strategy with **State** (Phase 8). Both delegate to an object with the same shape. Who typically **changes** the active object, and is the variation a **policy** or a **lifecycle**?

Strategy changes the selected policy, usually through client or configuration choice. State changes behaviour according to an object's lifecycle. Strategy is about choosing an algorithm while State is about lifecycle changes.

9. Contrast Strategy with **Adapter** (Phase 5) and with **Builder** (Phase 4). Which one translates a foreign API, which one assembles a valid aggregate, and which one swaps an algorithm?

Adapter translates an external interface, Builder constructs a valid object or aggregate and Strategy switches between algorithms.

10. A classmate writes one “mega-strategy” that still contains `if conservative` / `if aggressive` inside a single class. Another strategy class calls the actuator adapter to water immediately. Explain why each is a trap.

A mega-strategy keeps both policies in one class making the code harder to maintain. A strategy that starts the pump mixes decision-making with execution. Strategies should recommend actions, while another component handles execution.
