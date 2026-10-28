# Restaurant customer information review

Draft inputs for issue #44. These notes are not approved customer policies and
must not be presented as published terms. The restaurant must supply and approve
the missing operating details before production acceptance.

## Verified application behavior

- Checkout collects customer name, telephone, order items, optional notes,
  fulfillment and payment choice; delivery also requires an address.
- Staff can see the data needed to prepare and fulfill the order.
- Public tracking is protected by a random tracking reference and omits the
  customer's telephone, address and general order notes.
- Prices are recalculated on the server and changes require reconfirmation.
- PIX, cash and card on delivery are offline payment selections. The application
  does not automatically confirm bank settlement.
- Delivery eligibility and opening rules are controlled by the restaurant.
- Customer accounts, phone verification and personal benefits are not included
  in the first release.

## Restaurant inputs required

| Topic | Information to approve |
| --- | --- |
| Operator and contact | Responsible business identity, public address, customer support and data request channel |
| Ordering | Opening hours, neighborhoods, fees, minimums and expected preparation/delivery times |
| Payments | Authorized public PIX instructions, accepted card/cash rules and payment verification process |
| Changes and cancellation | When an order can be changed/cancelled, how the customer contacts staff and who handles refunds |
| Food information | Ingredients/allergens for each product, cross-contamination limitations and handling of special requests |
| Personal data | Purposes, hosting/service providers, access rules, retention/deletion periods and request handling |
| Approval | Responsible reviewer, approved wording, version/date and links to publish before checkout |

After review, publish the approved content in accessible pages linked from the
footer and checkout. Test links and readability on mobile. Do not invent business
identity, contact channels, retention periods, allergy guarantees or refund rules.
