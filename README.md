# LangEx 02 - Old Skool (Apache + CGI)

Build a developers oriented social network to share snippets of code.

## Installation

 - Recent Linux distribution with the following requiriments
   - Apache 2.x
   - PHP 5.3
   - Python
   - incron
 - Include the `conf/apache.conf` virtual host configuration file in your Apache setup
 - Modify `conf/config.json` to suit your setup
 - Add the following task to your incron configuration

    /var/www/langex/tasks IN_CREATE /var/www/langex/scripts/task.php $#


