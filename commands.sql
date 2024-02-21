CREATE TABLE info (
  name1 TEXT,
  name2 TEXT,
  name3 TEXT
);

CREATE TABLE actions (
  backup_id SERIAL PRIMARY KEY,
  operation_type TEXT,
  column_name TEXT,
  old_value TEXT,
  new_value TEXT
);

CREATE OR REPLACE FUNCTION backup_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO actions (operation_type, column_name, new_value)
        VALUES ('INSERT', 'name1, name2, name3', 
                CONCAT(NEW.name1, ',', NEW.name2, ',', NEW.name3));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.name1 IS DISTINCT FROM OLD.name1 THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[0], OLD.name1, NEW.name1);
        END IF;
        IF NEW.name2 IS DISTINCT FROM OLD.name2 THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[1], OLD.name2, NEW.name2);
        END IF;
        IF NEW.name3 IS DISTINCT FROM OLD.name3 THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[2], OLD.name3, NEW.name3);
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.name1 IS NULL AND OLD.name2 IS NULL AND OLD.name3 IS NULL THEN
            INSERT INTO actions (operation_type, column_name)
            VALUES ('DELETE', 'name1, name2, name3');
        ELSE
            INSERT INTO actions (operation_type, column_name, old_value)
            VALUES ('DELETE', 'name1, name2, name3', 
                    CONCAT(OLD.name1, ',', OLD.name2, ',', OLD.name3));
        END IF;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER info_backup_trigger
AFTER INSERT OR UPDATE OR DELETE ON info
FOR EACH ROW
EXECUTE FUNCTION backup_changes('name1', 'name2', 'name3');


INSERT INTO info (name1, name2, name3) VALUES ('1','2','3');

UPDATE info SET name1 = 'q' WHERE name1 = '1';
UPDATE info SET name2 = 'w' WHERE name2 = '2';
UPDATE info SET name3 = 'e' WHERE name3 = '3';

DELETE FROM info WHERE name1 = 'q';

INSERT INTO info (name1, name2, name3) VALUES ('1','2','3');


CREATE OR REPLACE FUNCTION manual_backup(steps_to_revert INT)
RETURNS VOID AS $$
DECLARE
    max_backup_id INT;
    revert_to_id INT;
    i INT := 1;
    action RECORD;
    column_names TEXT[];
    old_values TEXT[];
BEGIN
    ALTER TABLE info DISABLE TRIGGER info_backup_trigger;
    
    SELECT MAX(backup_id) INTO max_backup_id FROM actions;
    revert_to_id := max_backup_id - steps_to_revert;
    DELETE FROM info;
    FOR action IN SELECT * FROM actions WHERE backup_id <= revert_to_id LOOP
        column_names := string_to_array(action.column_name, ', '); 
        old_values := string_to_array(action.old_value, ','); 
        CASE action.operation_type
            WHEN 'INSERT' THEN
                EXECUTE 'INSERT INTO info (' || action.column_name || ') VALUES (' || action.new_value || ')';
            WHEN 'UPDATE' THEN
                EXECUTE 'UPDATE info SET ' || action.column_name || ' = $1 WHERE ' || action.column_name || ' = $2' USING action.new_value, action.old_value;
            WHEN 'DELETE' THEN
                EXECUTE 'DELETE FROM info WHERE ' || column_names[1] || ' = $1 AND ' || column_names[2] || ' = $2 AND ' || column_names[3] || ' = $3' USING old_values[1], old_values[2], old_values[3];
        END CASE;
    END LOOP;
    
    DELETE FROM actions WHERE backup_id > revert_to_id;
    
    ALTER TABLE info ENABLE TRIGGER info_backup_trigger;
    
END;
$$ LANGUAGE plpgsql;
SELECT * FROM actions;

SELECT manual_backup(3);
SELECT * FROM actions;
SELECT manual_backup(1);
SELECT * FROM actions;
SELECT * FROM info;
