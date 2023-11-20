import datetime
import sys
from pathlib import Path

from sqlalchemy.orm import Session

sys.path = [str(Path.cwd()), *sys.path]
print(sys.path)

from db import engine
from modules.birthdays import Birthday

birthdays = [
    ["Test 1", "20-10-2000"],
    ["Test 2", "21-11-2000"],
    ["Test 3", "22-07-2000"],
]

print(sys.argv)

for birthday in birthdays:
    with Session(engine) as session:
        session.add(
            Birthday(
                name=birthday[0],
                date=datetime.datetime.strptime(birthday[1], "%d-%m-%Y").astimezone(),
            ),
        )
        session.commit()
