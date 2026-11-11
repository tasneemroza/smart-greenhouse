# Phase 9 — Decorator questions

**Pattern / focus:** Decorator.

**Read first:** [Guide 09](../../materials/guides/09-decorator.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example HTTP client wrappers) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to `ActuatorPort`, policy decorators, and `actuator_execution_log` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Decorator in plain language. Why is stacking wrappers a flexible alternative to a combinatorial explosion of subclasses (`LoggingRetryMaxRuntimeActuator`, …)?

Decorator adds extra features without changing the original class. Stacking wrappers is easier because we can combine features without creating many subclasses

2. Name the participants (**component**, **concrete component**, **decorator**, **concrete decorators**). What interface does every decorator present to the caller, and why must that match the wrapped component?

The component is ActuatorPort, the concrete component is the real actuator adapter and the decorators are policy wrappers like logging and max run-time. They use the same interface so they can work together.

3. **Order matters.** Using logging and retry (or logging and max-run-time) as an example, explain how wrapping A around B can change what you observe compared with wrapping B around A.

Order matters because the outer decorator runs first. If logging is outside retry, it may log once, but if logging is inside retry, it may log every attempt.

## B. This phase of the application

4. What is `ActuatorPort` here, and which **at least two** decorators did you stack around the real adapter (for example logging and max run-time)? Where is the chain wired (composition root / factory), and why not inside the HTTP router?

ActuatorPort is the interface for controlling actuators. I used logging and max run-time decorators. They are connected in the factory to keep the HTTP router simple.

5. Max run-time can **short-circuit**: the inner adapter is never called. Why must a blocked attempt still produce a row in `actuator_execution_log` with `success=false` and the policy named in `policy_applied`?

Blocked attempts should also be saved so we know why an action failed. success=false shows the failure and policy_applied shows which policy blocked it.

6. How does max run-time know the actuator has been running too long (for example `actuator_states.updated_at` from Phase 8)? Why is that data from **State**, not something the decorator should invent as a second lifecycle?

Max run-time checks how long the actuator has been running using actuator_states.updated_at. This information comes from the State pattern, so we don't need another lifecycle.

7. `GET /api/actuators/executions` feeds the dashboard execution log. Why persist attempts in the database instead of only printing to stdout? What should the UI show after a blocked attempt and a refresh?

Saving logs in the database keeps the history even after restarting the application. After refreshing, the dashboard should still show the blocked attempt and its reason.

## C. Compare, contrast, and scenarios

8. Contrast Decorator with **Adapter**. Both wrap. One **keeps** the interface and **adds** behaviour; the other **changes** the interface and **translates**. Which is which in this greenhouse (Phase 9 vs Phase 5)?

Decorator adds new behaviour while keeping the same interface. Adapter changes the interface to connect different systems. Phase 9 uses Decorator, while Phase 5 uses Adapter.

9. Contrast Decorator with **inheritance** of combined policies. How does composition let you add or remove a policy without a new subclass for every combination?

With Decorator, we can add or remove policies by changing wrappers. With inheritance, we would need separate classes for different combinations.

10. A classmate’s decorator changes the method signature “a little” (extra required argument, different return type). Another ignores wrap order and cannot explain whether logging runs once per logical call or per inner attempt. Explain why each is a trap.

Changing the method signature breaks the shared interface. Ignoring wrapper order is also a problem because it changes how logging and other policies work.
