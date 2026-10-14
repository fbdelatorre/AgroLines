"""Seed/check known Stage 2 rows around additive migration, on disposable CI DB."""

import argparse

from sqlalchemy import text
from sqlalchemy.orm import Session

from server.config import get_settings
from server.db import make_engine
from server.models import AuthSession, Credential, Farm, Operation, Season, User
from server.security import digest, hash_password, verify_password

USER_ID = "00000000-0000-0000-0000-000000000031"
FARM_ID = "00000000-0000-0000-0000-000000000032"
SEASON_ID = "00000000-0000-0000-0000-000000000033"
OPERATION_ID = "00000000-0000-0000-0000-000000000034"
SESSION_ID = "00000000-0000-0000-0000-000000000035"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    engine = make_engine(get_settings())
    with Session(engine) as db:
        if not args.verify:
            db.add(User(id=USER_ID, name="Preservação sintética", email="migration@example.com"))
            db.flush()
            db.add(
                Credential(user_id=USER_ID, password_hash=hash_password("Synthetic preserved 123!"))
            )
            # Seed the historical schema, without columns introduced after Stage 2.
            db.execute(
                text("INSERT INTO farms (id, owner_id, name) VALUES (:id, :owner, :name)"),
                {"id": FARM_ID, "owner": USER_ID, "name": "Fazenda preservada"},
            )
            db.add(
                AuthSession(
                    id=SESSION_ID,
                    user_id=USER_ID,
                    access_hash=digest("synthetic-preserved-access"),
                    refresh_hash=digest("synthetic-preserved-refresh"),
                    access_expires=2000000000,
                    refresh_expires=2000000000,
                )
            )
            db.flush()
            db.add(Season(id=SEASON_ID, farm_id=FARM_ID, name="Safra preservada"))
            db.flush()
            db.add(Operation(id=OPERATION_ID, season_id=SEASON_ID, name="Operação preservada"))
            db.commit()
        else:
            assert db.get(User, USER_ID).email == "migration@example.com"
            assert verify_password(
                db.get(Credential, USER_ID).password_hash, "Synthetic preserved 123!"
            )
            assert db.get(Farm, FARM_ID).name == "Fazenda preservada"
            assert db.get(Farm, FARM_ID).work_crs == "EPSG:32723"
            assert db.get(Season, SEASON_ID).farm_id == FARM_ID
            assert db.get(Operation, OPERATION_ID).season_id == SEASON_ID
            assert db.get(AuthSession, SESSION_ID).access_hash == digest(
                "synthetic-preserved-access"
            )
            print("Stage 2 account, Argon2 hash, session, farm, season and operation preserved.")
    engine.dispose()


if __name__ == "__main__":
    main()
