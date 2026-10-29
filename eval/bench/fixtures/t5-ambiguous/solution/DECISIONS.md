# Decisions where the spec was silent

## Whitespace
Leading/trailing whitespace is stripped; whitespace between tokens
("1h 30m") and between amount and unit ("1 h") is tolerated.

## Repeated units
Rejected with ValueError ("1h1h" is almost certainly a data error).

## Invalid input
Anything that is not a sequence of <int><unit> tokens raises
ValueError; nothing is silently ignored.

## Empty input
Empty or whitespace-only strings raise ValueError.

## Bare numbers
A bare number without a unit (e.g. "90") is invalid input and raises
ValueError — guessing seconds vs minutes would hide data bugs.

## Decimals
Not supported: amounts are integers; "1.5h" raises ValueError rather
than silently truncating.
