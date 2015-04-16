monitoring-deploy
=================

Deployment wrapper around monitoring-formula.

Deploys (to Vagrant) the following machines:

* master: salt-master, monitoring clients
* monitoring: logstash, sensu, graphite, grafana, kibana, elasticsearch
* client1: monitoring clients

Usage
-----

To fire up the environment::

    pip install -r requirements.txt
    fab vendor_formulas
    vagrant plugin install vagrant-cachier # To speed things up
    vagrant up


Hosts File
~~~~~~~~~~

To communicate with the instances, you will need the following local hosts entries in /etc/hosts::

    192.168.33.40 salt.local salt
    192.168.33.41 graphite.local grafana.local sensu.local elasticsearch.local kibana.local

Firewall
~~~~~~~~

The monitoring server requires the following ports to be open incoming from the clients:

* 80 (TCP)
* 2003 (TCP)
* 5762 (TCP)
* 6379 (TCP)
* 2514 (UDP)

Hacking on the component formulas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If all you want out of this formula is to run the stack then following the
instructions at the start is enough.

If you want to develop one of those formulas salt-shaker doesn't currently have
a nice workflow. To make this easier we see if the repos are checked out (i.e.
if ``../elasticsearch-formula/elasticsearch`` exists) and if any of them
are it will mount them in the right places to use them in preference to the
salt-shaker versions.

This means you can do this::

    cd .. && git clone https://github.com/ministryofjustice/elasticsearch-formula.git

    cd monitoring-deploy
    vagrant reload

    # Make changes in ES formula
    # ...
    # And then just highstate via `vagrant provision`

