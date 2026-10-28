from pydantic import ValidationError
from contract import Machine

try:
    Machine(machine_id=1, serial_no="XX-1", site="Bielefeld", installed="unknown")
except ValidationError as e:
    print(e)