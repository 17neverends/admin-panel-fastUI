CREATE TABLE users (
  id TEXT,
  name TEXT,
  age TEXT
);

CREATE SEQUENCE backup_id_seq START 1;

CREATE TABLE actions (
  backup_id INT PRIMARY KEY DEFAULT nextval('backup_id_seq'),
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
        VALUES ('INSERT', 'id, name, age', 
                CONCAT(NEW.id, ',', NEW.name, ',', NEW.age));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.id IS DISTINCT FROM OLD.id THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[0], OLD.id, NEW.id);
        END IF;
        IF NEW.name IS DISTINCT FROM OLD.name THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[1], OLD.name, NEW.name);
        END IF;
        IF NEW.age IS DISTINCT FROM OLD.age THEN
            INSERT INTO actions (operation_type, column_name, old_value, new_value)
            VALUES ('UPDATE', TG_ARGV[2], OLD.age, NEW.age);
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        IF OLD.id IS NULL AND OLD.name IS NULL AND OLD.age IS NULL THEN
            INSERT INTO actions (operation_type, column_name)
            VALUES ('DELETE', 'id, name, age');
        ELSE
            INSERT INTO actions (operation_type, column_name, old_value)
            VALUES ('DELETE', 'id, name, age', 
                    CONCAT(OLD.id, ',', OLD.name, ',', OLD.age));
        END IF;
        RETURN OLD;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER info_backup_trigger
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW
EXECUTE FUNCTION backup_changes('id', 'name', 'age');




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
    ALTER TABLE users DISABLE TRIGGER info_backup_trigger;
    
    SELECT MAX(backup_id) INTO max_backup_id FROM actions;
    revert_to_id := max_backup_id - steps_to_revert;
    DELETE FROM users;
    FOR action IN SELECT * FROM actions WHERE backup_id <= revert_to_id LOOP
        column_names := string_to_array(action.column_name, ', '); 
        old_values := string_to_array(action.old_value, ','); 
        CASE action.operation_type
            WHEN 'INSERT' THEN
                EXECUTE 'INSERT INTO users (' || action.column_name || ') VALUES (' || action.new_value || ')';
            WHEN 'UPDATE' THEN
                EXECUTE 'UPDATE users SET ' || action.column_name || ' = $1 WHERE ' || action.column_name || ' = $2' USING action.new_value, action.old_value;
            WHEN 'DELETE' THEN
                EXECUTE 'DELETE FROM users WHERE ' || column_names[1] || ' = $1 AND ' || column_names[2] || ' = $2 AND ' || column_names[3] || ' = $3' USING old_values[1], old_values[2], old_values[3];
        END CASE;
    END LOOP;
    
    EXECUTE 'ALTER SEQUENCE backup_id_seq RESTART WITH ' || (revert_to_id + 1);
    
    DELETE FROM actions WHERE backup_id > revert_to_id;
    
    ALTER TABLE users ENABLE TRIGGER info_backup_trigger;
    
END;
$$ LANGUAGE plpgsql;

INSERT INTO users (id, name, age) VALUES ('1','2','3');


DELETE FROM users WHERE id = '1';

INSERT INTO users (id, name, age) VALUES ('1','2','3');
SELECT * FROM actions;



SELECT manual_backup(2);
SELECT * FROM actions;
SELECT * FROM users;


INSERT INTO users (id, name, age) VALUES ('1','2','3');
UPDATE users SET name = 'q' WHERE name = '2';
INSERT INTO users (id, name, age) VALUES ('1','2','3');


SELECT * FROM actions;
SELECT * FROM users;

SELECT manual_backup(3);
SELECT * FROM actions;
SELECT * FROM users;