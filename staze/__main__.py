"""
Invoke cli interface when staze executed as a script:
```py
python -m staze
```
"""
try:
    from .core.cli import cli
except ImportError:
    from staze.core.cli import cli


if __name__ == "__main__":
    cli.main()