<?php
// Manages profile posting
//
//   - Requires an user name (via Http server)
//     - email:string   -> The user email
//     - avatar:string  -> The user avatar as an url
//     - site:string    -> The user web site
//

$CONF = file_get_contents( __DIR__ . '/../conf/config.json');
$CONF = json_decode($CONF);

$USER = $_SERVER['PHP_AUTH_USER'];


// Build the profile path
$PATH = $CONF->paths->data . '/' . $USER;

// If profile exists load it
if (file_exists($PATH . '/profile.json')) {
    $data = file_get_contents($PATH . '/profile.json');
    $data = json_decode($data, true);
} else {
    $data = array();
}

// Set new values
isset($_POST['email']) and $data['email'] = $_POST['email'];
isset($_POST['avatar']) and $data['avatar'] = $_POST['avatar'];
isset($_POST['site']) and $data['site'] = $_POST['site'];

// If the user does not have a random token for secure access generate it now
if (empty($data['token'])) {
    $data['token'] = openssl_random_pseudo_bytes(16);
    $data['token'] = bin2hex($data['token']);
}

// TODO: Improve permission flag
if (!is_dir($PATH)) {
    mkdir($PATH, 0777, true);
}

// Store the message as a new file
file_put_contents($PATH . '/profile.json', json_encode($data));

