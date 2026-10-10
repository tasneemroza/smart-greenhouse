# Phase 4 — Builder questions

**Pattern / focus:** Builder.

**Read first:** [Guide 04](../../materials/guides/04-builder.md) · [Requirements](requirements.md)

## How to answer

- Use your own wording. Do not paste teaching-example types (for example ramen orders) as if they were your greenhouse classes.
- When a question asks about _this application_, refer to locations, zones, `location_id`, and the configuration wizard from the lab.
- Short answers are fine when the question is narrow. Write a few sentences when it asks you to explain or compare.
- Write each answer inside the matching **Your Answer** note. Replace the placeholder; leave the question text unchanged.

## A. Pattern

1. State the intent of Builder in plain language. Why does construction of a complex object need **stepwise assembly** and **validation at the end** (`build()`), instead of a telescoping constructor or a half-filled dict written straight to the database?

Builder creates a complex object step by step. It keeps the code easier to understand and checks that the final configuration is valid before build() returns it. This is safer than a long constructor or saving incomplete data directly.

2. Name the main participants (**product**, **builder**, **optional director**, **client**). Until `build()` succeeds, is the intermediate object a finished domain product? Why does that distinction matter?

The main participants are the product, builder, optional director, and client. Before build() succeeds, the object is only a temporary configuration, not a finished domain product. This matters because only valid products should be used or saved.

3. List at least three kinds of invalid configuration a location/zone `build()` should reject in **this** lab (name, zones, moisture thresholds). Why must those rules live in the **domain** builder, not only in the HTTP layer?

The builder should reject an empty location name, invalid or empty zones, and wrong moisture thresholds such as minimum being higher than maximum. These rules belong in the domain builder because validation should work even when the application is used without the HTTP layer.

## B. This phase of the application

4. What aggregate does the builder produce (location plus zones)? Why does this course use **`location_id`** (and never `greenhouse_id`) as the name for that scope?

The builder produces a location with its zones. The application uses location_id to identify this scope because locations are the main configuration area in this lab. greenhouse_id is not used because it is not the name defined by the application.

5. Describe the path from API request to persistence: DTO → builder steps → `build()` → repository. What must **not** be persisted if `build()` raises `ConfigurationError` (or equivalent)? Why does assigning a device wait until the zone row exists, and why does the client send only `zone_id`?

The request becomes a DTO, then the builder adds the location and zones step by step. build() validates everything, and only then does the repository save it. If build() raises ConfigurationError, nothing should be saved. A device is assigned after the zone exists because it needs a valid zone_id. The client sends only zone_id because the server already knows the zone.

6. Saving a location and its zones must be **one transaction**. What goes wrong if the location row commits and a later zone insert fails? How does that relate to “no half-built aggregates in the database”?

	If the location is saved first and a zone insert fails, the database could contain a location without all its zones. This creates an incomplete aggregate. One transaction makes sure everything is saved together, or everything is rolled back.

7. The configuration wizard UI collects fields in steps. How does that UI map to Builder without turning React (or the HTTP handler) into the place that owns domain validation?

	The React wizard collects the fields step by step and sends them to the API. The HTTP handler passes the data to the Builder. The Builder owns the real domain validation, so React is mainly responsible for collecting and displaying the configuration.

## C. Compare, contrast, and scenarios

8. Contrast Builder with Factory Method and with Abstract Factory. Which pattern answers “which type?”, which answers “which matching kit?”, and which answers “how do we assemble one **valid whole** in steps?”

	Factory Method answers “Which type should I create?”
	Abstract Factory answers “Which matching kit/family should I create?”
	Builder answers “How do I assemble one valid whole step by step?”

9. Fluent method chaining (`builder.add_zone(...).build()`) is a coding style. Why is a fluent interface **not** the same thing as the Builder pattern?

	Fluent chaining is only a coding style where methods return the object so calls can be chained. Builder is a design pattern with step-by-step construction and usually a final build() that creates a valid product. So fluent code alone does not mean it is Builder.

10. A classmate validates thresholds only in FastAPI / Pydantic and leaves `build()` empty. Another mutates builder fields after `build()` while treating the product as immutable. Explain why each is a trap.

	The first is a trap because domain rules should not depend only on FastAPI or Pydantic. The Builder must also protect the domain. The second is a trap because after build(), the product should be treated as a finished and valid object. Changing the builder afterward should not change that product.
