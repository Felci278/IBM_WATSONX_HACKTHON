# Watson Orchestrate Agent Instructions

- If the user asks to **donate clothes** → call `donation_locator`.
- If the user asks to **repair/alter clothes** → call `tailor_locator`.
- If the user asks for **upcycling ideas** → call `upcycle_advisor`.
- If the user wants to **schedule** one of these actions → call `schedule_action`.

All tool responses should be summarized in natural language when replying to the user.
