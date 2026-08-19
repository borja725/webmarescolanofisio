<?php
// Incluye los archivos necesarios de PHPMailer
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';
require 'PHPMailer/src/Exception.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

// Obtener datos del formulario
$nombre = htmlspecialchars($_POST['name'], ENT_QUOTES, 'UTF-8');
$telefono = htmlspecialchars($_POST['telefono'], ENT_QUOTES, 'UTF-8');
$mail = filter_var($_POST['Email'], FILTER_VALIDATE_EMAIL);
$subject = htmlspecialchars($_POST['subject'], ENT_QUOTES, 'UTF-8');


// Valida que la dirección de correo del usuario sea válida
if (!$mail) {
   die('La dirección de correo proporcionada no es válida.');
}

$mensaje = "Este mensaje fue enviado por " . $nombre . " \r\n";
$mensaje .= "Email: " . $mail . " \r\n";
$mensaje .= "Teléfono: " . $telefono . " \r\n";
$mensaje .= "Asunto: " . $subject . " \r\n";
$mensaje .= "Mensaje: " . htmlspecialchars($_POST['comments'], ENT_QUOTES, 'UTF-8') . " \r\n";
$mensaje .= "Enviado el " . date('d/m/Y', time());

// Configurar PHPMailer
$mailer = new PHPMailer(true);
$mailer->SMTPDebug = 3; // Niveles: 0 (sin depuración), 1 (errores y mensajes), 2 (estado), 3 (mensajes de cliente y servidor)
$mailer->Debugoutput = 'html'; // Formato de salida legible

try {
    // Configuración del servidor SMTP
    $mailer->isSMTP();
    $mailer->Host = 'smtp.ionos.es'; // Cambia a tu servidor SMTP
    $mailer->SMTPAuth = true;
    $mailer->Username = 'info@marescolanofisioterapia.com'; // Tu dirección de correo
    $mailer->Password = 'MarEscolano2024.'; // Contraseña del correo
    $mailer->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS; // O ENCRYPTION_SMTPS según tu configuración
    $mailer->Port = 587; // Cambia si usas otro puerto SMTP

    // Configuración del correo
    $mailer->setFrom('info@marescolanofisioterapia.com', 'Mar Escolano Fisioterapia'); // Dirección de envío
    $mailer->addAddress('info@marescolanofisioterapia.com', 'Destinatario'); // Destinatario
    $mailer->addReplyTo($mail, $nombre); // Responder a

    // Contenido
    $mailer->isHTML(false); // Cambiar a true si deseas enviar HTML
    $mailer->Subject = 'Mensaje web MAR ESCOLANO FISIOTERAPIA';
    $mailer->Body = $mensaje;

    // Enviar correo
    $mailer->send();
    header('Location: ./gracias.html');
} catch (Exception $e) {
    echo "Error al enviar el mensaje. Mailer Error: {$mailer->ErrorInfo}";
}
?>