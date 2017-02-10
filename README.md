# Udaciy Full Stack Web Developer Nanodegree Project 5: Catalog App
=====================================================================
A database driven web page that allows users to create categories and items,
and allows users to perform CRUD operations on items. This application is built
on Flask, and leverages Facebook's OAuth capabilities.

## Demo Site:
TODO

## Prerequisites
- [Vagrant](http://vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

## Setup
1. Clone the repository at https://github.com/sxhan/udacity-fsnd-project-5
2. cd into the project directory and then the vagrant directory: `cd udacity-fsnd-project-5/vagrant`
3. Launch the Vagrant VM: `vagrant up`. This must be done inside the vagrant directory, where there is a file called `Vagrantfile`
4. Login to the vm: `vagrant ssh`
5. cd to the project directory: `cd /vagrant`
6. Run the initialization script `./init.sh`
7. Start the development server via `python run.py`. You may optionally pass in a command line argument `-p` to specify a port. Port 5000 is used by default, but the VM is configured to allow 8000 and 8080 as well.
8. Access the web application at http://localhost:8000, or whatever port you specified in step 7.
