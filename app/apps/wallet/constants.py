class TransactionStatusConstant:
    COMPLETED = "Completed"
    PENDING = "Pending"
    CANCELLED = "Cancelled"


class PaymentMethodConstant:
    BANK_TRANSFER = "Bank Transfer"
    GIFT = "Gift"
    CARD = "Card"
    ALL = "All"


class TransactionTypeConstant:
    DEPOSIT = "Deposit"
    WITHDRAWAL = "Withdrawal"
    TRANSFER = "Transfer"


class PaymentProviderConstant:
    BANK = "Bank"
    STRIPE = "Stripe"
    PAYPAL = "Paypal"
