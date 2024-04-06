'''An active job running in Andromeda is now self aware to it's own job key'''

from optilogic import pioneer
from os import getenv

pioneer.Job.print_add_record_calls = True
optipy = pioneer.Api(auth_legacy=False)

# active job emits self aware job key
if hasattr(optipy, '_job_id_env') is False:
    pioneer.Job.add_record(key='job_key', message=getenv('JOB_KEY'))    
else:
    pioneer.Job.add_record(key='job_key', message=optipy._job_id_env)
