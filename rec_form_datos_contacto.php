<?php
// Incluye los archivos necesarios de PHPMailer
require 'PHPMailer/src/PHPMailer.php';
require 'PHPMailer/src/SMTP.php';
require 'PHPMailer/src/Exception.php';

use PHPMailer\PHPMailer\PHPMailer;
use PHPMailer\PHPMailer\Exception;

/*
 * La configuración y la contraseña viven en config.php, que está en .gitignore
 * y por tanto nunca se sube al repositorio. Si despliegas en un servidor nuevo,
 * copia config.php a mano: no llega con `git clone`.
 */
$configPath = __DIR__ . '/config.php';

if (!is_file($configPath)) {
    error_log('Falta config.php junto a rec_form_datos_contacto.php');
    die('El formulario no está configurado. Copia config.sample.php como config.php y rellénalo.');
}

$config = require $configPath;

if (empty($config['smtp_pass'])) {
    error_log('config.php existe pero smtp_pass está vacío');
    die('El formulario no está configurado: falta la contraseña del buzón en config.php.');
}

// Solo se procesan envíos reales del formulario.
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Location: ./contacto.html');
    exit;
}

/*
 * Los campos se leen con ?? '' en lugar de acceder directamente al array. Sin
 * esto, cualquier petición a la que le falte un campo (un bot que postea al
 * endpoint, o un cambio futuro en el formulario) llena la respuesta de avisos
 * "Undefined array key" y se los muestra al visitante.
 */
$nombre   = trim(htmlspecialchars($_POST['name']     ?? '', ENT_QUOTES, 'UTF-8'));
$telefono = trim(htmlspecialchars($_POST['telefono'] ?? '', ENT_QUOTES, 'UTF-8'));
$subject  = trim(htmlspecialchars($_POST['subject']  ?? '', ENT_QUOTES, 'UTF-8'));
$comments = trim(htmlspecialchars($_POST['comments'] ?? '', ENT_QUOTES, 'UTF-8'));
$mail     = filter_var(trim($_POST['Email'] ?? ''), FILTER_VALIDATE_EMAIL);

// Valida que la dirección de correo del usuario sea válida
if (!$mail) {
    die('La dirección de correo proporcionada no es válida.');
}

if ($nombre === '') {
    die('Indica tu nombre para poder responderte.');
}

$mensaje  = "Este mensaje fue enviado por " . $nombre . " \r\n";
$mensaje .= "Email: " . $mail . " \r\n";
$mensaje .= "Teléfono: " . $telefono . " \r\n";
$mensaje .= "Asunto: " . $subject . " \r\n";
$mensaje .= "Mensaje: " . $comments . " \r\n";
$mensaje .= "Enviado el " . date('d/m/Y H:i');

// Configurar PHPMailer
$mailer = new PHPMailer(true);

/*
 * Debe quedarse en 0 en producción. Con un nivel mayor PHPMailer imprime la
 * conversación SMTP en la respuesta: eso envía la salida antes de tiempo, el
 * header('Location: ./gracias.html') del final deja de redirigir, y además el
 * visitante ve el servidor y el usuario SMTP. Súbelo solo para depurar.
 */
$mailer->SMTPDebug = 0;
$mailer->Debugoutput = 'html';

try {
    // Configuración del servidor SMTP
    $mailer->isSMTP();
    $mailer->Host = $config['smtp_host'];
    $mailer->SMTPAuth = true;
    $mailer->Username = $config['smtp_user'];
    $mailer->Password = $config['smtp_pass'];
    $mailer->SMTPSecure = PHPMailer::ENCRYPTION_STARTTLS;
    $mailer->Port = (int) $config['smtp_port'];
    $mailer->CharSet = 'UTF-8';

    // Configuración del correo
    $mailer->setFrom($config['from_email'], $config['from_name']);

    foreach ($config['to'] as $direccion => $nombreDestinatario) {
        $mailer->addAddress($direccion, $nombreDestinatario);
    }

    // Responder al visitante, no al buzón del dominio
    $mailer->addReplyTo($mail, $nombre !== '' ? $nombre : $mail);

    // Contenido
    $mailer->isHTML(false);
    $mailer->Subject = 'Mensaje web MAR ESCOLANO FISIOTERAPIA';
    $mailer->Body = $mensaje;

    // Enviar correo
    $mailer->send();
    header('Location: ./gracias.html');
    exit;
} catch (Exception $e) {
    /*
     * El detalle va al log del servidor, no a la pantalla: ErrorInfo puede
     * revelar el servidor y el usuario SMTP. Para depurar, mira el log de
     * errores de PHP en tu hosting.
     */
    error_log('Fallo al enviar el formulario de contacto: ' . $mailer->ErrorInfo);
    http_response_code(500);
    echo 'No hemos podido enviar tu mensaje en este momento. '
       . 'Por favor, escríbenos a marescolanofisio@gmail.com o llámanos al +34 621 279 029.';
}
