#!/usr/bin/env python3
import asyncio
import time

from pymodbus import Framer
from pymodbus.client import AsyncModbusSerialClient
from src.orca.constants import Constants

LOOP_COUNT = 1000
REGISTER_COUNT = 10

async def run_async_client_test():
    """Run async client."""
    print("--- Testing async client v3.4.1")
    client = AsyncModbusSerialClient(
        "/dev/ttys004",
        framer_name=Framer.RTU,
        baudrate=9600,
    )
    await client.connect()
    assert client.connected

    start_time = time.time()
    for _i in range(LOOP_COUNT):
        rr = await client.read_input_registers(1, REGISTER_COUNT, slave=1)
        if rr.isError():
            print(f"Received Modbus library error({rr})")
            break
    client.close()
    run_time = time.time() - start_time
    avg_call = (run_time / LOOP_COUNT) * 1000
    avg_register = avg_call / REGISTER_COUNT
    print(
        f"running {LOOP_COUNT} call (each {REGISTER_COUNT} registers), took {run_time:.2f} seconds"
    )
    print(f"Averages {avg_call:.2f} ms pr call and {avg_register:.2f} ms pr register.")


if __name__ == "__main__":
    print(Constants.Modbus.READ)
    run_async_client_test()
    asyncio.run(run_async_client_test())
