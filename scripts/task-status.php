#!/usr/bin/php -q
<?php

function loadjson($path, $assoc=false) {
    $json = file_get_contents($path);
    return json_decode($json);
}

// Launched when a new status is posted

$CONF = loadjson(__DIR__ . '/../conf/config.json');


if (!file_exists($argv[1])) {
    fputs(STDERR, 'First argument must be a valid task file!');
    exit(1);
}


// Obtain the task details from stdin
$task = loadjson($argv[1]);

// Obtain the status data
$status = loadjson($CONF->paths->data . '/' . $task->user . '/wall/' . $task->id);

// Obtain the user profile
$profile = loadjson($CONF->paths->data . '/' . $task->user . '/profile.json');

// Process friends
$recipients = $task->to;
if (empty($recipients)) {
    $recipients = array();

    // It's a global update
    updateWall($CONF->paths->public . '/wall.json', $task, $profile, $status);

    // Get the list of friends to update their feeds
    if ($profile->friends) {
        $recipients = $profile->friends;
    }
}

// The author always gets a copy
$recipients[] = $task->user;

// Mail the message to all the recipients
foreach ($recipients as $recipient) {
    $friend = loadjson($CONF->paths->data . '/' . $recipient . '/profile.json');

    // Skip non-complete friends
    if (!$friend || !$friend->token) continue;

    // Ensure we have a destination path
    $path = $CONF->paths->public . '/users/' . $recipient;
    if (!is_dir($path)) {
        mkdir($path, 0777, true);
    }

    $path .= '/wall-' . $friend->token . '.json';

    updateWall($path, $task, $profile, $status);
}



// Updates a feed
function updateWall($path, $task, $profile, $status) {
    global $CONF;

    $wall = loadjson($path, true);
    if (!$wall) $wall = array();

    // Add the new message to the top
    array_unshift($wall, array(
        'user'      => $task->user,
        'avatar'    => $profile->avatar,
        'gravatar'  => md5($profile->email),
        'site'      => $profile->site,
        'status'    => $status->status,
        'timestamp' => filemtime($CONF->paths->data . '/' . $task->user . '/wall/' . $task->id)
    ));

    // Limit to N elements
    while (count($wall) > 30) array_pop($wall);

    file_put_contents($path, json_encode($wall));
}
