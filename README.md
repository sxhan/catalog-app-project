# Udaciy Full Stack Web Developer Nanodegree Project 5: Catalog App
=====================================================================
A database driven web page that allows users to create categories and items,
and allows users to perform CRUD operations on items. This application is built
on Flask, and leverages Facebook's OAuth capabilities.

## Demo Site:
See it in action [here](http://catalog.thoughtforyourthoughts.com/)

## Prerequisites
- [Vagrant](http://vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

## Setup
1. Clone the repository at https://github.com/sxhan/udacity-fsnd-project-5
2. cd into the project directory: `cd udacity-fsnd-project-5`
3. Launch the Vagrant VM: `vagrant up`. This must be done inside the vagrant directory, where there is a file called `Vagrantfile`
4. Login to the vm: `vagrant ssh`
5. cd to the project directory: `cd /vagrant`
6. (Optional) Create a directory called `instance`, and a file called `config.py` inside new directory: `mkdir instance && touch config.py`. This step is required if you'll be using the OAuth features.
7. (Optional) if using OAuth features, place corresponding client/app secrets inside this file as a python dictionary. See examples in the main config file (ie. `/vagrant/config.py`, not `/vagrant/instance/config`) for the format, and the official documentation for each of the providers for how to set this up.
 - For Facebook, visit https://developers.facebook.com. Create an application, and add both the "app_id" and "app_secret" to instance/config.py in the format shown.
8. Run the script called `run.sh` create a new db and start the application server: `./run.sh`
 - You may optionally pass in a command line argument `-p` to specify a port. Port 5000 is used by default, but the VM is configured to allow 8000 and 8080 as well.
9. Access the web application at http://localhost:5000, or whatever port you specified in step 8.
