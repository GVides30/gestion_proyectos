const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const db = require('./db'); 
const app = express();
const PORT = 5000;
// Habilitar CORS para todas las rutas
app.use(cors());

// Middleware para las solicitudes preflight OPTIONS
app.options('*', cors());

app.use(bodyParser.json());