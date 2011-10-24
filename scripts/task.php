#!/usr/bin/php -q
<?php

// Load config
$CONFIG = file_get_contents('../conf/config.json');
$CONFIG = json_decode($CONFIG);

// Compute the task filename
$taskfile = $CONFIG->paths->tasks . '/' . $argv[1];

// Read the task file
$task = file_get_contents($taskfile);
if (FALSE === $task) {
    fputs(STDERR, 'Unable to read task from ' . $taskfile);
    exit(1);
}

// Perform the task
// TODO! :)

// Remove the task once it's completed
unlink($taskfile);

