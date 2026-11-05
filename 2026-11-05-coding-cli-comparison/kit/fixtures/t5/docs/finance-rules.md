# Finance reporting rules

Agreed with Finance, 2026-03.

1. A reporting week starts on **Monday** and is computed in **UTC**, whatever offset the timestamp carries.
2. Rows with status `voided` never count.
3. Refunds are stored as rows with a negative `amount_cents` and `refund_of` set to the original sale id.
   A refund reduces the week of the **original sale**, not the week the refund happened.
4. If the original sale is not in the data set, the refund reduces the week of the refund row itself.
