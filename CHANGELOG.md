# Changelog

## 0.2.0

### Added
- PayChangu Connect: `authorize_link`, `user`, `revoke`, and `PayChanguClient.from_access_token`
- US virtual accounts: customer CRUD, create/deactivate/reactivate account, account activity
- `verify_virtual_account_signature` for VA webhook HMAC verification
- HTTP `PUT` and `DELETE` helpers

## 0.1.0

### Added
- Shared HTTP session with timeouts and typed errors (`APIError`, `ValidationError`, `AuthenticationError`, `NetworkError`)
- Wallet balance (`GET /wallet-balance`)
- Bank transfer direct charge and bank transfer details
- Bank payouts (list banks, initialize, details, list)
- Full bills suite (billers, validate, pay, details, statistics)
- Correct airtime recharge (`POST /bills/buy-airtime`)
- Card charge, verify, and refund helpers
- Webhook HMAC-SHA256 signature verification
- Dataclass request models that omit `None` fields and stringify amounts
- Unit tests with `pytest` and `responses`

### Changed
- MoMo payout payload aligned to API (`mobile`, `mobile_money_operator_ref_id`, `charge_id`)
- Payment model: only `amount`, `currency`, `callback_url`, and `return_url` are required
- Package layout restructured into `resources/` and `models/`
- Python requirement raised to `>=3.9`
- Packaging fixed for `src/` layout; metadata URLs updated

### Removed
- Legacy `/bill_payment/*` airtime endpoints
- Stale payout fields (`mobile_number`, `network`, `reference`)
