#!/usr/bin/php -q
<?php

# Open connection with syslog
openlog('langex-task', LOG_PID | LOG_PERROR, LOG_LOCAL0);

// Load config
$CONF = file_get_contents(__DIR__ . '/../conf/config.json');
$CONF = json_decode($CONF);

// Compute the task filename
$taskfile = $CONF->paths->tasks . '/' . $argv[1];

// Read the task file
$task = file_get_contents($taskfile);
if (FALSE === $task) {
    fputs(STDERR, 'Unable to read task from ' . $taskfile);
    exit(1);
}

$task = json_decode($task);

// Perform the task
$cmd = $CONF->paths->base . '/scripts/';
chdir($cmd);
switch ($task->action) {
    case 'notify':
        $cmd .= 'task-notify.py';
        break;
    case 'status':
        $cmd .= 'task-status.php';
        break;
    case 'snippet':
        $cmd .= 'task-snippet.py';
        break;
    case 'profile':
        $cmd .= 'task-profile.php';
        break;
    default:
        fputs(STDERR, 'Non supported task action: ' . $task->action);
        syslog(LOG_WARNING, 'Non supported task action: ' . $task->action);
        exit(1);
}

// Launch task process
$out = shell_exec($cmd . ' ' . escapeshellarg($taskfile));
syslog(LOG_INFO, 'Cmd: ' . $cmd . ' - TaskFile: ' . $taskfile . ' -- ' . $out);


// Remove the task once it's completed
unlink($taskfile);

