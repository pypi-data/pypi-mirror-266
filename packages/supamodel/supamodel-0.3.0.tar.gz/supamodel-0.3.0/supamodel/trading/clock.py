import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

import pendulum
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    model_validator,
)

from supamodel._logging import logger


class Sizing(BaseModel):
    months: int = 0
    weeks: int = 0
    days: int = 0
    hours: int = 0
    minutes: int = 0
    seconds: int = 0


class Window(BaseModel):
    tail: datetime
    head: datetime


class Clock(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    window_size: Sizing = Sizing(weeks=1)

    @abstractmethod
    def now(self):
        pass

    def now_local(self):
        return self.now("local")

    @computed_field
    @property
    def head(self) -> pendulum.datetime:
        return self.now()

    @computed_field
    @property
    def tail(self) -> pendulum.datetime:
        return self.now().subtract(**self.window_size.model_dump())

    @computed_field
    @property
    def sliding_window(self) -> Window:
        return Window(tail=self.tail, head=self.head)


class LiveClock(Clock):
    def now(self):
        return pendulum.now("utc")


class TestClock(Clock):
    initial_time: datetime = pendulum.now("utc")
    current_time: datetime = pendulum.now("utc")
    step_size: Sizing = Sizing(days=1)

    @model_validator(mode="after")
    def reset_time(self):
        if self.initial_time < self.current_time:
            self.current_time = self.initial_time

    def now(self):
        return pendulum.instance(self.current_time)

    def step(self):
        self.current_time = self.current_time.add(**self.step_size.model_dump())

    def reset(self):
        self.current_time = self.initial_time


class BacktestConfig(BaseModel):
    backtest_id: UUID = Field(default_factory=uuid.uuid4)
    start_time: datetime = pendulum.now("utc")
    end_time: datetime = pendulum.now("utc")

    model_config = ConfigDict(arbitrary_types_allowed=True)


def main_test_clock():
    """
    This function is the main entry point for testing the clock functionality.

    It initializes a `LiveClock` object, sets the current time and start time for a `BacktestConfig` object,
    and creates a `TestClock` object with specific window and step sizes. It then resets the test clock and
    performs a series of operations within a while loop.

    Note: The while loop is currently commented out in the code.

    We're just running out of time for today.


    Args:
        None

    Returns:
        None
    """
    live = LiveClock()
    logger.success(f"{live.tail.to_cookie_string()} - {live.head.to_cookie_string()}")
    current_time = pendulum.now("utc")
    start_time = current_time.subtract(years=1)
    backtest = BacktestConfig(start_time=start_time, end_time=current_time)

    test = TestClock(
        initial_time=backtest.start_time,
        window_size=Sizing(days=3, weeks=0),
        step_size=Sizing(days=1),
    )
    test.reset()
    # bar_dataset = OHLCVDataset()

    # while True:
    #     window = test.sliding_window
    #     tail_cookie = window.tail.to_cookie_string()
    #     head_cookie = window.head.to_cookie_string()
    #     if test.sliding_window.head >= backtest.end_time:
    #         logger.info("Backtest complete!")
    #         break
    #     result = bar_dataset.between(window.tail, window.head, "1 day")

    #     logger.success(
    #         f"Queries a resampled OHLCV between the window tail ('{tail_cookie}') and head ('{head_cookie}')."
    #     )
    #     print(result)
    #     test.step()
    #     print("\n\n")


def main():
    main_test_clock()


if __name__ == "__main__":
    main()
