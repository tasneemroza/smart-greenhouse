# Phase 3 — Abstract Factory questions

## A. Pattern

1. State the intent of Abstract Factory in plain language. What goes wrong when related products are chosen independently (`if format` for each piece) instead of as a **family**?

Abstract Factory creates a group of related products that work together. Choosing them separately can cause incompatible products to be mixed.

2. Name the main participants (**abstract factory**, **concrete factory**, **abstract products**, **concrete products**, **client**). How does choosing a factory at the start **commit** the client to one family?

The abstract factory defines the creation methods, and the concrete factory creates one specific family. The client chooses one factory, so the products come from that same family.

3. When should you use Abstract Factory, and when should you skip it (for example only one product type per request, or mixing siblings is valid)?

Use it when several related products need to work together. Skip it when there is only one product type or mixing products is okay.

## B. This phase of the application

4. In this lab, what is a **device family**, and what does `create_device_set()` (or your equivalent) return? Why must a simulation kit and an edge kit not mix incompatible siblings?

A device family is a group of devices with the same setup, like simulation or edge. `create_device_set()` returns two sensors and two actuators. They should not be mixed because their configurations can be different.

5. Phase 2 Factory Method creators still exist. How does Abstract Factory **compose** them rather than replace them? What would you lose if you deleted the sensor creators and inlined all construction inside the family factory?

Abstract Factory uses the Phase 2 sensor creators to create the sensors. If we deleted them, we would lose reusable sensor creation logic and make the family factory harder to maintain.

6. Why add a `device_family` column on the existing `devices` table (with a default/backfill such as `"simulation"`) instead of a new table per family? What happens to Phase 2 sensor rows if you forget the backfill?

One table keeps all devices together and makes the API simpler. The backfill gives old sensor rows a family. Without it, old rows could have a missing family and cause filtering problems.

7. `POST /api/devices/provision` returns a kit (expected size: two sensors and two actuators). `GET /api/devices` can filter by `family` and `role`. Why must the UI be able to filter by family? Why do `/api/sensors` routes from Phase 2 still need to work?

Family filtering lets the user see the selected simulation or edge devices. The Phase 2 sensor routes must still work so the old functionality is not broken.

## C. Compare, contrast, and scenarios

8. Draw the contrast in one paragraph: Factory Method vs Abstract Factory. Use the questions “which **one** product?” versus “which product **line**?” and mention that Abstract Factory often **uses** Factory Method–style methods inside.

Factory Method asks “which **one** product?” and creates one product, like a sensor. Abstract Factory asks “which product **line**?” and creates a related family. It can also use Factory Method–style methods inside.

9. A DTO or HTTP handler constructs concrete simulation/edge device types directly, bypassing the family factory. What consistency bug can that reintroduce? How should HTTP stay on the abstract factory / service instead?

It can create the wrong family or configuration and mix simulation and edge devices. HTTP should call the service, which uses the correct family factory.

10. Someone proposes a single “god factory” that creates locations, readings, and devices “because we already have a factory.” Why is that a misuse of Abstract Factory?

Abstract Factory should create related products, not unrelated things. Locations, readings, and devices have different responsibilities.
