import sys
import time
import random
from optilogic import pioneer

pioneer.Job.print_add_record_calls = True

start_time: float = time.time()
print('start time', start_time)

secs_to_run_for: int = random.randint(5, 15)
print(f'\n\nforecast runtime {secs_to_run_for} seconds')
pioneer.Job.add_record(key='eta', message=f'{secs_to_run_for} seconds')

nintey_six_thousand_bytes: str = 'm' * 96000

tup = (
    bool(1),
    int(1),
    float(1),
    [1],
    (1, 2),
    {1: 2},
    {1, 2},
    b'101',
)

for t in tup:
    pioneer.Job.add_record(key='type', message=t)
    time.sleep(0.1)

pioneer.Job.print_add_record_calls = False
pioneer.Job.add_record(key='96k', message=nintey_six_thousand_bytes)
