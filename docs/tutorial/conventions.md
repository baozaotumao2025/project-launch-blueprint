# Tutorial Conventions

> 这里定义 stage 教程的统一写法。  
> 目的是让后续新增的 stage 教程继续保持同一套阅读顺序和解释颗粒度。

## Shared Structure

Each stage tutorial should explain:

1. The stage's responsibility
2. What it depends on
3. How the current implementation works
4. What the stage produces
5. Why isolation or review rules matter
6. Which code files implement the behavior
7. What to test
8. Common mistakes
9. What the next stage is

## Writing Rules

- Keep the first section about the stage's purpose, not the code.
- Keep the implementation section tied to actual files.
- Keep the testing section concrete and observable.
- Keep the mistakes section focused on likely regressions.
- Keep the next-step section aligned with the workflow order.

## Why This Matters

The tutorial series is meant to teach the workflow, not just document it. A common structure makes it easier to compare stages, reuse the same mental model, and extend the series without rewriting the learning experience each time.
