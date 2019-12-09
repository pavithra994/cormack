SELECT
       client_manager.name,
       username,
       email,
       enabled,
       phone_number,

      client.name
FROM client_manager INNER JOIN client on client_manager.client_id = client.id
ORDER BY client.name
