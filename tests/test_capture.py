import asyncio
from nicesheet.capture import run_capture, run_async_capture


def test_simple_capture():
    def simple():
        return 4
    
    assert 4 == run_capture(simple)



def test_simple_capture_with_args():
    def simple(first, second, another=2):
        return first + second + another

    assert 6 == run_capture((simple, 1, 3))
    assert 4 == run_capture((simple, 1, 0, {"another": 3}))

    def simple_kwargs_only(yet=2, another=5):
        return yet + another
    
    assert 7 == run_capture(simple_kwargs_only)
    assert 10 == run_capture((simple_kwargs_only, {"yet": 5}))


def test_simple_async_capture():
    async def simple():
        await asyncio.sleep(0.01)
        return 4
    
    assert 4 == asyncio.run(run_async_capture(simple))