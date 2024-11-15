const mysql = require('mysql2');

// Configura los detalles de conexión a MariaDB
const connection = mysql.createConnection({
    host: '127.0.0.1',
    user: 'root',      // Cambia esto por tu usuario de MariaDB
    password: 'password', // Cambia esto por tu contraseña de MariaDB
    database: 'gestion_proyectos'
});

// Conexión a la base de datos
connection.connect((err) => {
    if (err) {
        console.error('Error al conectar a la base de datos:', err);
        return;
    }
    console.log('Conexión exitosa a la base de datos MariaDB');
});

module.exports = connection;