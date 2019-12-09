with numbers as (SELECT * FROM  generate_series(1, (SELECT MAX(id) FROM job))) SELECT generate_series FROM numbers where NOT generate_series in  (SELECT ID FROM job)

with numbers as (SELECT * FROM  generate_series(1, (SELECT MAX(id) FROM supervisor))) SELECT generate_series FROM numbers where NOT generate_series in  (SELECT ID FROM supervisor)
