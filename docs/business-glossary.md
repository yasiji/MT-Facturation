# Business Glossary

## Core Business Entities
- `Client`: billing account owner (individual or business).
- `Subscriber`: service identity owned by a client (mobile number, internet line, TV account).
- `Offer`: commercial plan definition with pricing and validity.
- `OfferVersion`: immutable pricing/rules snapshot attached to a contract.
- `Contract`: legal/commercial binding between client, subscriber, and offer version.
- `Invoice`: monthly grouped bill per client.
- `InvoiceLine`: billable item included in an invoice.
- `Payment`: money received and allocated to one or multiple invoices.
- `CollectionCase`: overdue tracking object containing collection stage and actions.

## Status Definitions
- Contract status: `draft`, `active`, `suspended`, `terminated`.
- Invoice status: `issued`, `partially_paid`, `paid`, `overdue`.
- Collection stage: `reminder`, `warning`, `suspension_candidate`, `escalated`.

## Billing Semantics
- Billing period is monthly and invoices are client-grouped.
- Issued invoices are immutable except by adjustment/credit flow.
- Payment allocation defaults to oldest unpaid invoice first.

## Service Types
- `mobile`
- `fiber`
- `adsl`
- `tv`
- `addon`
