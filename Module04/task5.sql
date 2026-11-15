PRAGMA foreign_keys = ON;
.print === AFTER INSERT trigger (original) ===
.print alarm count at start:
SELECT COUNT(*) FROM alarm;
.print A: reading rejected by CHECK (9999), alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-02 10:00:00', 9999, 1);
SELECT COUNT(*) FROM alarm;
.print B1: new alarming reading 3.0, alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-02 11:00:00', 3.0, 1);
SELECT COUNT(*) FROM alarm;
.print B2: replay of the same reading via UPSERT, alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-02 11:00:00', 3.1, 1) ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value;
SELECT COUNT(*) FROM alarm;

DROP TRIGGER trg_vib_alarm;
CREATE TRIGGER trg_vib_alarm BEFORE INSERT ON reading FOR EACH ROW
WHEN NEW.value > 2.0 AND (SELECT metric FROM sensor WHERE sensor_id = NEW.sensor_id) = 'vib_rms'
BEGIN
    INSERT INTO alarm(sensor_id, ts, value, reason) VALUES (NEW.sensor_id, NEW.ts, NEW.value, 'vibration over 2.0 mm/s');
END;

.print === BEFORE INSERT trigger ===
.print alarm count at start:
SELECT COUNT(*) FROM alarm;
.print A: reading rejected by CHECK (9999), alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-03 10:00:00', 9999, 1);
SELECT COUNT(*) FROM alarm;
.print B1: new alarming reading 3.0, alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-03 11:00:00', 3.0, 1);
SELECT COUNT(*) FROM alarm;
.print B2: replay of the same reading via UPSERT, alarm count after:
INSERT INTO reading(sensor_id, ts, value, interval_s) VALUES (2,'2026-03-03 11:00:00', 3.1, 1) ON CONFLICT(sensor_id, ts) DO UPDATE SET value = excluded.value;
SELECT COUNT(*) FROM alarm;
