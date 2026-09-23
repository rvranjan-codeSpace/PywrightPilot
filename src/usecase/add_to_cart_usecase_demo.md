# Demo Use Case: Add to Cart & Verify Cart Contents



## The scenario, in plain language

> As a standard SauceDemo user, when I add the Sauce Labs Backpack to my cart from the inventory page, the cart
> badge should show 1, and the cart page should list that item with the correct name, description, price, and a
> Remove button.

## Step 1 — Ask the planner agent

Prompt to type in Claude Code:

> Use the playwright-test-planner agent to plan tests for adding the Sauce Labs Backpack to the cart from the
> inventory page and verifying it appears correctly on the cart page. Limit the plan to exactly 2 test cases
> (happy path only) — no edge cases, no negative scenarios, no a11y checks.


## Step 2 — Review the plan

Open `test_plans/add_to_cart_test_plan.md` and sanity-check it against the real data-test ids above before
generating code from it.

## Step 3 — Ask the generator agent

Prompt:

> Use the playwright-test-generator agent to implement the scenarios in test_plans/add_to_cart_test_plan.md.

W
## Step 4 — Execute test

```bash
pytest tests/cart_test.py -v
```




