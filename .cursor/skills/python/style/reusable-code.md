# Reusable Code and Code Pathways

- **Write reusable code**: Put behavior on the natural owner (e.g. enum methods like `Provider.suggested_models()`, shared helpers) so callers stay thin and logic lives in one place. Avoid duplicating logic across modules.
- **Consider impact on related code**: When changing code, ask how it affects callers and related logic. Prefer changes that update one path so all callers benefit, rather than adding another branch or copy.
- **Reduce cases**: Prefer one implementation path over many branches or special cases. If the same concept is handled in several places, consolidate so one change propagates correctly and there are fewer pathways to maintain.
- **Refactor instead of handling edge cases**: If the code is handling edge cases (nulls, empty lists, special values), consider refactoring so those cases do not arise—e.g. guarantee shape at the boundary, use types that rule out the edge case, or restructure the flow so the "edge" path goes away. Prefer simplifying the design over adding more branches.
- **Delete dead code**: Remove modules, classes, or functions that are no longer imported or called. Do not leave stub files, deprecated wrappers, or empty packages "for reference"—delete them so the codebase has a single, live path for each capability.
