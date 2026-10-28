# Restaurant operating rules

Staff manage the rules through `/admin/settings`. Every change requires an
authenticated session and is validated on the backend. Product availability and
price remain controlled through `/admin/menu`.

## Before receiving real orders

The initial commercial values are intentionally not approved. In deployed
environments, ordering stays closed until staff enable **Regras revisadas para
receber pedidos reais**. Review the catalog, prices, neighborhoods, fee, minimum,
payment instructions and opening hours before enabling it. Manual closure always
overrides the weekly schedule.

When delivery is enabled, readiness requires at least one neighborhood. When PIX
is enabled, readiness requires public payment instructions. Development and test
environments bypass the readiness flag so isolated automated tests can run; this
does not authorize a deployed environment to receive real orders.

## Delivery and pickup

The MVP uses one configurable delivery fee for listed neighborhoods in Poços de
Caldas, MG. Neighborhood matching ignores accents, letter case and repeated
spaces. An address in a different city/state or an unlisted neighborhood is
rejected on the server. Pickup does not require an address and never includes a
delivery fee. The minimum order applies to the product subtotal.

## Hours

Weekly hours use `America/Sao_Paulo`, independent of the server timezone. The
administrative form provides one interval per day. Closing earlier than opening
means the interval ends the next day. Opening is inclusive; closing is exclusive.
Dates without service override normal hours, including the after-midnight part
of the previous day's interval. Disabling the automatic schedule retains manual
open/closed control. Public settings include the next scheduled opening when
applicable.

## Payments

PIX, card on delivery and cash can be enabled independently. Public PIX
instructions must contain only information the restaurant authorizes customers
to see. Selecting PIX does not confirm settlement; the team verifies payment.
Never put bank passwords or API secrets in this field.

## Deployment

Apply migrations through `0008_store_operating_rules`, install the pinned tzdata
dependency and deploy the frontend/API together. Existing live readiness starts
false. Final restaurant acceptance, security and database/backup validation remain
tracked by issue #14.
