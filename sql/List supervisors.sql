SELECT client.name,
       supervisor.name, username, enabled, email, phone_number FROM supervisor INNER JOIN client ON supervisor.client_id = client.id
ORDER BY client.name, supervisor.name
