CREATE DATABASE IF NOT EXISTS hospital2;
USE hospital2;
CREATE TABLE IF NOT EXISTS expediente2 (
  id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  nombre varchar(255) NOT NULL,
  diagnostico varchar(450) NOT NULL,
  tratamiento varchar(450) NOT NULL,
  passwordSalt varchar(80) NOT NULL,
  diag_nonce varchar(80) NOT NULL,
  treat_nonce varchar(80) NOT NULL
);
