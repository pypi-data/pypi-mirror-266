# Cron Expression Generator

## Description

Cron Expression Generator is a python package which helps to generator cron expressions that can be used to schedule the frquency at which cron jobs run.

## Usage

```python
from cron_expression_generator import generator

cron_expression = str(
    generator.CronExpressionGenerator()
        .minutes(5, every=True)
)

# cron_expression = "* */5 * * * *"
```

## Contributions

1. Create a fork of the project
2. Clone the forked project
3. Install dependencies with ```pip install -r requirements.txt```
4. Setup pre-commit hooks with ```precommit install```
5. Make code changes
6. Push changes
7. Make a PR to the dev branch
8. Awaiting your contributions
