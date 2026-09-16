<?php
/*
 * Plantilla de configuración del formulario de contacto.
 *
 * Copia este archivo como `config.php` y rellena los valores.
 * `config.php` está en .gitignore y NO debe subirse nunca al repositorio:
 * es el único sitio donde vive la contraseña.
 */

return [
    // Servidor de salida (SMTP)
    'smtp_host' => 'smtp.ionos.es',
    'smtp_port' => 587,
    'smtp_user' => 'info@marescolanofisioterapia.com',

    // Contraseña DEL BUZÓN, no la de la cuenta de IONOS. Son distintas:
    // la del panel de control no sirve para autenticar por SMTP.
    'smtp_pass' => '',

    // Remitente que verá quien reciba el aviso
    'from_email' => 'info@marescolanofisioterapia.com',
    'from_name'  => 'Mar Escolano Fisioterapia',

    // Destinatarios del aviso: dirección => nombre
    'to' => [
        'marescolanofisio@gmail.com'         => 'Mar Escolano',
        'info@marescolanofisioterapia.com'   => 'Buzón de la web',
    ],
];
