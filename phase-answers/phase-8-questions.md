# Phase 8 — State questions

**Pattern / focus:** State.

**Read first:** [Guide 08](../../materials/guides/08-state.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example support-ticket states) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to actuator lifecycle, persisted state, and `allowed_commands` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of the State pattern in plain language. What problem appears when lifecycle is modelled as boolean flags and scattered `if` guards?

The State pattern changes an object's behaviour based on its current state. Without it many boolean flags and if conditions make the code confusing and can cause invalid states.

2. Name the participants (**context**, **state interface**, **concrete states**, **client**). How does a successful command lead to a **transition**, and where do **guards** live?

The context is the actuator, the state interface defines the rules and concrete states define each behaviour. The client sends a command. If it is successful the actuator changes state through a transition. Guards are handled in the state or domain logic.

3. What is `allowed_commands` (or equivalent) for? Why is exposing “what can I do **now**?” better than letting the UI guess from a raw state string?

allowed_commands tells the UI which actions are possible right now. It is better than guessing from a state string because the backend already knows which commands are allowed.

## B. This phase of the application

4. Which actuator states did you implement (for example idle, running, error)? Sketch the **legal** transitions (which command or event moves idle → running, running → idle, into error, and out of error).

I implemented idle running and error states. A start command moves idle to running. A stop command moves running to idle. A failure moves the actuator to error. After fixing the problem it can return to idle.

5. Why is actuator state stored in `actuator_states` (or equivalent) rather than only in process memory? What must still be true after you restart the backend?

Actuator state is stored in actuator_states so it is not lost when the backend restarts. After restarting the actuator must still have its last saved state.

6. An **illegal** transition must raise a domain error and **must not** update the database. Why? Which HTTP status is reasonable for that case (400 or 409), and why should the rule live in the domain rather than in React?

An illegal transition should raise a domain error and must not change the database. HTTP 409 is reasonable because the action conflicts with the current state. The rule belongs in the backend so it works even without React.

7. Device JSON gains `state` and `allowed_commands`. How does the dashboard use those fields (badges, disable illegal buttons)? How does this prepare **Phase 10 Command**?

The dashboard uses state to show status badges and allowed_commands to enable or disable buttons. This also prepares Phase 10 because commands will be handled as separate actions.

## C. Compare, contrast, and scenarios

8. Contrast State with **Strategy**. Both look like “context delegates to an object.” Who typically **changes** the active object, and is the variation a **lifecycle** or a **selectable policy**? Give a greenhouse example of each (this phase vs Phase 6).

State represents an object's lifecycle and changes when an event or command happens. Strategy represents a selectable policy. In our greenhouse actuator states change through commands, while Phase 6 uses Conservative or Aggressive irrigation strategies.

9. Contrast State with a pile of booleans (`is_running`, `is_fault`, `is_maintenance`). Why do illegal combinations of flags appear, and how do explicit state objects (or a transition table) prevent that?

Many booleans can create confusing and impossible combinations such as running and idle at the same time. Explicit states allow only valid states and transitions.

10. A classmate puts HTTP status mapping or SQLAlchemy commits **inside** a concrete state class. Another state mutates a flag directly and skips `transition` / `set_state`. Explain why each is a trap.

HTTP status codes and database commits should not be inside state classes because they mix business rules with technical work. Changing a flag directly is also wrong because it skips transition checks and can create invalid states. All state changes should go through transition or set_state.
