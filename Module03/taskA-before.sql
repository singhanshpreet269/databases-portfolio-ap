   EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician = 'Beier';
   EXPLAIN QUERY PLAN SELECT * FROM machine WHERE machine_name = 'cnc-02';
   EXPLAIN QUERY PLAN SELECT * FROM maint_job WHERE technician LIKE '%ei%';