# Phase 2 — Factory Method questions

## A. Pattern

### 1. State the intent of Factory Method in plain language. What problem appears when callers scatter `new` / constructors (or a growing `if type == ...`) across the application?

**Answer:**
Factory Method keeps object creation in one place. If I create objects everywhere using constructors or many `if` statements, the code can become confusing and harder to change. If I add a new type later, I might need to change many parts of the code. Factory Method helps me avoid this problem.

### 2. Name the main participants of Factory Method (**product**, **concrete product**, **creator**, **concrete creator**, **client**). For each, give one sentence: what it is responsible for.

**Answer:**
**Product:** It is the common object or type that I want to create.

**Concrete product:** It is a specific version of the product with its own settings or behavior.

**Creator:** It defines how the product should be created.

**Concrete creator:** It creates a specific type of product with the correct default values.

**Client:** It asks for a product without needing to know all the details about how it is created.

### 3. How do you add a **new product variant** when creators are polymorphic (new class + registry entry) versus when creation lives in one shared `if/elif` function? Why does that difference matter for extension?

**Answer:**
With polymorphic creators, I can create a new creator class and add it to the registry. I don't need to keep adding more conditions to one big `if/elif` function. This makes it easier to add new sensor types later and keeps the code more organized.

## B. This phase of the application

### 4. In this lab, what is the **product** and what are the **concrete creators**? Why must the API handler (or sensor service) go through a creator/registry instead of constructing `MoistureSensor` / `LightSensor` itself?

**Answer:**
In my project, the product is the `Sensor` object. The concrete creators are `MoistureSensorCreator` and `LightSensorCreator`. My sensor service uses `get_creator()` to find the right creator. This means the API does not need to know all the details about creating each sensor, and adding another sensor type later will be easier.

### 5. `POST /api/sensors` accepts a short `type` key such as `"moisture"` or `"light"`, while the stored/returned field is `device_type` (for example `moisture_sensor`). Why are those two fields different? Who decides the stored `device_type` and `default_config`?

**Answer:**
The `type` is a short name that tells my application which creator to use. The `device_type` is the actual sensor type that is stored in the database and returned by the API. The concrete creator decides the `device_type` and the default configuration. For example, the moisture creator creates a `moisture_sensor` with settings for measuring soil moisture.

### 6. Why is there a single `devices` table with `role="sensor"` instead of a dedicated `sensors` table? What later phase does that choice prepare for?

**Answer:**
I used one `devices` table because different devices can share the same basic structure. The `role="sensor"` tells me that the device is a sensor. This also makes it easier to add other types of devices later. It prepares my project for the Abstract Factory work in Phase 3.

### 7. What should happen when the client posts an **unknown** `type`? Where should that rejection be decided (registry/service vs router constructing a concrete class anyway)?

**Answer:**
If the client sends an unknown type, my application should reject it instead of creating a sensor. In my project, `get_creator()` checks the registry and raises an error if the type is not found. The API then returns HTTP 400. This keeps the sensor creation logic in the factory instead of putting it directly in the router.

## C. Compare, contrast, and scenarios

### 8. Contrast Factory Method with a **simple factory** (one function full of `if type == ...`). When is the simple factory “good enough,” and why does this phase still want polymorphic creators?

**Answer:**
A simple factory is fine for a small project with only a few types. It is easy to understand and quick to implement. But when more types are added, the `if/elif` function can become very large. Factory Method is useful in my project because each creator has its own creation logic, so it is easier to extend.

### 9. Contrast Factory Method with **Abstract Factory** (Phase 3). Factory Method answers which question? Abstract Factory answers which different question? Why is Factory Method enough for Phase 2 sensors?

**Answer:**
Factory Method is mainly about deciding **which object to create**. In my project, it decides which type of sensor should be created and what default settings it should have. Abstract Factory is more about creating a group of related objects that belong together. Factory Method is enough for Phase 2 because I am only creating individual sensors.

### 10. A classmate puts SQLAlchemy session commits (or FastAPI request parsing) **inside** a concrete creator. Why is that a trap? Where should persistence and HTTP stay instead?

**Answer:**
That would mix too many responsibilities in the creator. The creator should only create the sensor and set its default values. In my project, FastAPI request handling stays in the API router, and database operations stay in the repository. The service connects these parts together.
