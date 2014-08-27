monitoring-deploy
=================

Deployment wrapper around monitoring-formula.

Deploys (to Vagrant):

* salt master: 'master'
* logstash, sensu, graphite: 'monitoring'

Usage
-----

.. image:: https://raw.githubusercontent.com/ministryofjustice/monitoring-formula/HEAD/monitoring-diagram.png

```
fab vendor_formulas
vagrant up
```


Hosts File
~~~~~~~~~~

To communicate with the instances, you will need the following local hosts entries:

    192.168.33.80 salt.local salt
    192.168.33.81 graphite.local grafana.local sensu.local elasticsearch.local kibana.local

Firewall
~~~~~~~~

The monitoring server requires the following ports to be open incoming from the clients:


* 80 (TCP)
* 2003 (TCP)
* 5762 (TCP)
* 6379 (TCP)
* 2514 (UDP)


