| Case | Reference | Last-attempt values (120B, North, Qwen, 20B, Dots) | 2-of-3 decision | vs ref | 3-of-5 decision | vs ref | 2-of-3 → 3-of-5 |
|---|---|---|---|---|---|---|---|
| C01 | 792800 | 120B 792800, North 792800, Qwen 792800, 20B 792800, Dots 792800 | **792800** (3/3, k=2) | right | **792800** (5/5, k=3) | right | same |
| C02 | 590320 | 120B 590320, North 2606320, Qwen 590320, 20B 0, Dots 590320 | **590320** (2/3, k=2) | right | **590320** (3/5, k=3) | right | same |
| C03 | 936350 | 120B 936350, North 936350, Qwen 936350, 20B 936350, Dots 936350 | **936350** (3/3, k=2) | right | **936350** (5/5, k=3) | right | same |
| C04 | 2826250 | 120B 2826250, North 2826250, Qwen 2826250, 20B 2826250, Dots 2826250 | **2826250** (3/3, k=2) | right | **2826250** (5/5, k=3) | right | same |
| C05 | 38480 | 120B 38480, North 38480, Qwen 38480, 20B 38480, Dots 38480 | **38480** (3/3, k=2) | right | **38480** (5/5, k=3) | right | same |
| C06 | 0 | 120B 0, North 0, Qwen 0, 20B 0, Dots 0 | **0** (3/3, k=2) | right | **0** (5/5, k=3) | right | same |
| C07 | 13970 | 120B 13970, North 13970, Qwen 13970, 20B 13970, Dots 13970 | **13970** (3/3, k=2) | right | **13970** (5/5, k=3) | right | same |
| C08 | 605580 | 120B 605580, North ∅, Qwen 605580, 20B 605580, Dots 160920 | **605580** (2/3, k=2) | right | **605580** (3/5, k=3) | right | same |
| C09 | 487980 | 120B 487980, North 487980, Qwen 487980, 20B 487980, Dots 487980 | **487980** (3/3, k=2) | right | **487980** (5/5, k=3) | right | same |
| C10 | 558980 | 120B 558980, North 119410, Qwen ∅, 20B 558980, Dots 0 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C11 | 446690 | 120B 446690, North 0, Qwen 446690, 20B 322160, Dots 446690 | **446690** (2/3, k=2) | right | **446690** (3/5, k=3) | right | same |
| C12 | 1666490 | 120B 1666490, North 1666490, Qwen 1666490, 20B 1666490, Dots 1666490 | **1666490** (3/3, k=2) | right | **1666490** (5/5, k=3) | right | same |
| C13 | 107740 | 120B 107740, North 107740, Qwen 107740, 20B 107740, Dots 107740 | **107740** (3/3, k=2) | right | **107740** (5/5, k=3) | right | same |
| C14 | 0 | 120B 0, North 0, Qwen 0, 20B 0, Dots 0 | **0** (3/3, k=2) | right | **0** (5/5, k=3) | right | same |
| C15 | 168680 | 120B 168680, North 168680, Qwen 0, 20B 168680, Dots 138920 | **168680** (2/3, k=2) | right | **168680** (3/5, k=3) | right | same |
| C16 | 376740 | 120B 376740, North 595500, Qwen ∅, 20B 376740, Dots 211260 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C17 | 258180 | 120B 80190, North 371990, Qwen 248490, 20B 258180, Dots 258180 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C18 | 62480 | 120B 62480, North 62480, Qwen 62480, 20B 62480, Dots 39580 | **62480** (3/3, k=2) | right | **62480** (4/5, k=3) | right | same |
| C19 | 1990 | 120B 1990, North 71640, Qwen 83580, 20B 1990, Dots 0 | abstain (best 1/3, k=2) | abstain | abstain (best 2/5, k=3) | abstain | same |
| C20 | 1106090 | 120B 1106090, North 1106090, Qwen 1106090, 20B 1106090, Dots 1106090 | **1106090** (3/3, k=2) | right | **1106090** (5/5, k=3) | right | same |

- 2of3: 16 right, 0 wrong, 4 abstentions out of 20 questions
- 3of5: 16 right, 0 wrong, 4 abstentions out of 20 questions
