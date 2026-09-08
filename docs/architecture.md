# Application Architecture

## Overview

Sushi App is planned as a mobile-first web application with separate customer and restaurant experiences. The architecture keeps presentation, business rules and persistence concerns independent so each area can evolve and be tested safely.

## Components

### Frontend

The frontend will use Next.js, React and TypeScript. It will provide:

- a customer menu, product configuration, cart, checkout and order tracking flow;
- an authenticated restaurant area for orders, products and categories;
- responsive layouts optimized for mobile ordering.

The frontend communicates with the backend through HTTP and does not access the database directly.

### Backend

The FastAPI backend owns:

- request validation;
- business rules and price calculations;
- product, category and order operations;
- administrator authorization;
- database access through SQLAlchemy.

Routes receive HTTP requests and delegate data operations to service and persistence layers as those layers are introduced.

### Database

PostgreSQL will persist categories, products, add-ons, customers, addresses, orders and order items. Schema changes will be managed through versioned migrations.

The initial relational model is:

```text
Category 1 --- N Product 1 --- N ProductAddon
Customer 1 --- N Address
Customer 1 --- N Order 1 --- N OrderItem 1 --- N OrderItemAddon
Address  1 --- N Order
Product  1 --- N OrderItem
```

Order items keep snapshots of product and add-on names and prices so historical orders remain accurate when the menu changes.

Money values will use fixed-precision decimal database types. Prices and totals must never rely on binary floating-point calculations in the persistent domain model.

## Primary customer flow

```text
Menu -> Product configuration -> Cart -> Checkout -> Order creation -> Status tracking
```

## Primary restaurant flow

```text
Admin login -> Incoming orders -> Order details -> Status update -> Completion
```

## API boundaries

The initial API is organized by resource under `backend/app/routes`. Future business logic should not be placed directly in route handlers. The planned backend structure is:

```text
backend/app/
|-- routes/       # HTTP endpoints
|-- schemas/      # Request and response validation
|-- models/       # SQLAlchemy database models
|-- services/     # Business rules
|-- repositories/ # Database queries
|-- core/         # Configuration and security
`-- main.py       # Application entry point
```

Folders will be added only when their corresponding MVP feature is implemented.

## Configuration and security

- Runtime configuration comes from environment variables.
- `.env` is local and must never be committed.
- `.env.example` documents required variables using non-sensitive values.
- Administrative routes will require authenticated and authorized users.
- Public responses must not expose secrets or internal error details.

## Testing strategy

- Unit tests cover isolated business rules.
- API tests validate HTTP behavior and response contracts.
- Integration tests validate database operations.
- End-to-end tests will cover the complete customer and restaurant acceptance flow before deployment.
