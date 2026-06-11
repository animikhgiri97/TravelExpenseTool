import asyncio
from demo import run_demo


def test_run_demo_smoke():
    # smoke test: ensure demo runs without raising
    asyncio.run(run_demo())
