A. Pattern

1. What is a design pattern? What is it not?
A design pattern is a common way to solve a problem when designing software. It gives the idea of how to structure the code. It is not ready-made code, and we don't need to use it for every problem.

2. What are the three GoF pattern families?
Creational- it helps with to create objects.
Structural: it helps with how classes and objects are put together.
Behavioral: it helps with how objects communicate and work together.
These all are important to understand the concept of phase 1.

3. When should we skip a pattern?
We should always skip a pattern if the problem is small and simple as normal code can handle it. If we use a pattern too early, it can make the code more complicated than needed.

B. This phase of the application

4. Why is Phase 1 almost empty?
Phase 1 is mainly about making sure the backend, database, migrations, and frontend are working all of these together. Having an empty but running project shows that the basic setup actually works instead of just having incomplete classes.

5. What belongs in the four backend layers?
domain defines the business rules and main concepts.
application means The logic and use cases of the application.
infrastructure means the database and the other technical things.
interfaces/api means API routes and HTTP-related code.
For example, FastAPI code should not be inside domain.

6. What does GET /health return?
It returns {"status": "ok"} after checking the PostgreSQL connection. This shows that the backend is working and can also connect to the database. /scalar is used for the API documentation and /docs is disabled as required in the project.

7. Why use Alembic before creating business tables?
We use Alembic from the beginning so we can keep track of database changes properly. If we created tables manually first, the database and migration history could become different and cause problems later.

C. Compare, contrast, and scenarios

8. What is dependency direction?
The outer layers can use the inner layers but the domain should stay independent. The domain should not use FastAPI, SQLAlchemy or HTTP Pydantic models because then the business logic would depend on specific technologies.

9. Frontend cannot show the health status. What should you check?
First, we would check if both the frontend and backend are running. Then we should check the API URL, CORS or proxy settings, and if /health gives the correct JSON. This is important in Phase 1 because we first need to make sure the basic application works.

10. What is still missing after Phase 1?
There are still greenhouse features, database tables, the sensor API, business logic, design patterns, and testing to add. The later phases will add these features using the basic structure we already created instead of starting the project again.
