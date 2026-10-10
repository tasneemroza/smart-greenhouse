# Phase 5 — Adapter questions

**Pattern / focus:** Adapter.

**Read first:** [Guide 05](../../materials/guides/05-adapter.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example a legacy XML calendar client) as if they were your greenhouse classes.
- When a question asks about *this application*, refer to sensor ports, adapters, readings, and `sensor_readings` from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Adapter in plain language. What problem appears when business code speaks a vendor or legacy protocol (odd field names, units, XML, status codes) directly?

Adapter helps two systems work together when their interfaces are different. Without an adapter, the application code may need to understand different field names, units or data formats which makes the code more complicated and harder to maintain.

2. Name the participants (**target / port**, **adaptee**, **adapter**, **client**). What does the adapter translate, and what must it **not** decide (business policy)?

The target or port is the interface the application expects. The adaptee is the existing system, the adapter translates its data and the client uses the port. The adapter translates data formats and values into a common format but it should not make business decisions.

3. GoF distinguishes an **object adapter** (composition) from a **class adapter** (inheritance). Which does modern code prefer, and why?

Modern code usually prefers an object adapter because it uses composition instead of inheritance. It is more flexible and allows us to change or replace the adapted system more easily.

## B. This phase of the application

4. What is `SensorPort` in this lab, and what normalized value type (for example `Reading`) do adapters return? Why do application services depend on the port rather than on a simulation driver or vendor SDK?

SensorPort is the common interface used to read sensor data. Adapters return a normalized Reading value so that the application gets data in the same format. Application services depend on the port so they do not need to know the details of a simulation driver or vendor SDK.

5. You need three translations onto the same normalized reading: a simulation adapter, a vendor stub, and an MQTT translator that accepts a payload dict. Why is the different raw shape the point of the exercise? How does `source` (`simulation`, `vendor`, or `mqtt`) show which adapter produced the reading, and why must the MQTT translator not open a broker in this phase? Phase 12 may deliver that same dict on a device HTTP route or through an optional broker — why must this phase still not open either transport?

The different raw data shapes show how adapters convert different inputs into the same Reading format. The source field tells us whether the reading came from simulation, a vendor or MQTT. The MQTT translator should only convert the given payload dictionary. It must not connect to a broker, HTTP route or other transport because those belong to a later phase like phase 12.

6. Readings are **appended** to `sensor_readings` (history grows). Why not keep only the latest value in memory or overwrite a single row, and which later phase consumes this history? Why do a manual read, the simulation sampler, and (later) MQTT share **one** writer of that table? Why does the sampler skip devices with tracking off and MQTT devices, and why do sensor cards poll the latest stored reading until Phase 12?

Readings are saved as history for later analysis instead of keeping only the latest value. One writer keeps saving consistent. The sampler skips disabled tracking and MQTT devices because they are not handled by simulation. Sensor cards show the latest stored reading until Phase 12.

7. `POST /api/sensors/{id}/read` runs an adapter, persists, and returns a DTO. What HTTP status is appropriate when the device is missing versus when the adapter fails? Why must the router never see vendor-shaped types?

Return 404 Not Found if the device is missing and 502 Bad Gateway if the adapter fails. The router should handle normal application data, not vendor-specific formats.

## C. Compare, contrast, and scenarios

8. Contrast Adapter with **Facade**. Adapter changes the **shape** of an existing interface; Facade simplifies **how to use** a subsystem. Give a greenhouse-shaped example of each (Adapter this phase; Facade in Phase 7).

Adapter converts one interface into another like converting vendor sensor data into a Reading. Facade simplifies a complex system for example getting the greenhouse status through one operation in Phase 7.

9. Contrast Adapter with **Decorator**. Both wrap an object. What is different about the interface they present to the client?

Adapter changes the interface to make systems work together while Decorator keeps the same interface but adds extra behaviour as logging.

10. A classmate puts irrigation policy (“if moisture &lt; 0.3 then water”) inside the vendor adapter. Why is that a trap? Where should that decision live instead (later Strategy), and what should stay in the adapter?

The adapter should only translate sensor data not decide when to water plants. That decision belongs in a Strategy in a later phase.
