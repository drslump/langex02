<?php
// Manages status posting
//
//   - Requires an user name (via Http server)
//   - Input (POST)
//     - status:string  -> The status message
//     - to:string      -> If set this must be the username of a friend
//

$CONF = file_get_contents( __DIR__ . '/../conf/config.json');
$CONF = json_decode($CONF);

if (!isset($_SERVER['PHP_AUTH_USER'])) {
    header('WWW-Authenticate: Basic realm="Langex"');
    header('HTTP/1.0 401 Unauthorized');
    echo 'You need to provide valid authentication credentials';
    exit;
}

$USER = $_SERVER['PHP_AUTH_USER'];


if (empty($_POST['status'])) {
  header('HTTP/1.0 400 Bad Request');
  echo 'You need to give a value for the status';
  exit;
}


$data = array();

$data['status'] = $_POST['status'];

// If the message is restricted to someone add it as a list of comma separated usernames
if (!empty($_POST['to'])) {
    $recipients = explode(',', $_POST['to']);
    $recipients = array_map(function($itm){ return trim($itm); }, $recipients);
    $data['to'] = $recipients;
}


// Generate the Path and Id for the message
$ID = uniqid(gmdate('YmdHi-'));
$PATH = $CONF->paths->data . '/' . $USER . '/wall';

// TODO: Improve permission flag
if (!is_dir($PATH)) {
    mkdir($PATH, 0777, true);
}

// Store the message as a new file
file_put_contents($PATH . '/' . $ID, json_encode($data));


// Notify task manager
$task = array(
    'action' => 'status',
    'user'   => $USER,
    'id'     => $ID
);

file_put_contents($CONF->paths->tasks . '/' . $ID, json_encode($data));

