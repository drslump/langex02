<?php
// Manages profile posting
//
//   - Requires an user name (via Http server)
//     - email:string   -> The user email
//     - avatar:string  -> The user avatar as an url
//     - site:string    -> The user web site
//     - friends:string -> Comma separated list of friend usernames
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


// If we only want to fetch it return it
if (empty($_POST)) {
    header('Content-type: application/json');
    echo json_encode($data);
    exit;
}


// Set new values
isset($_POST['email']) and $data['email'] = $_POST['email'];
isset($_POST['avatar']) and $data['avatar'] = $_POST['avatar'];
isset($_POST['site']) and $data['site'] = $_POST['site'];
if (isset($_POST['friends'])) {
    $friends = explode(',', $_POST['friends']);
    array_walk($friends, function($itm){ return trim($itm); });
    $data['friends'] = $friends;
}

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


// Notify task manager
$task = array(
    'action' => 'profile',
    'user'   => $USER,
);

file_put_contents($CONF->paths->tasks . '/profile-' . $USER . '.json', json_encode($task));

