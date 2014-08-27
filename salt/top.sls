base:
  '*':
    - minions.base
    - hardening
    - admins
    - repos.sensu
    - hosts
    - sensu.client
    - metrics.client
    - logstash.client
  'G@roles:master':
    - match: compound
    - minions.master
  'G@roles:monitoring.server':
    - match: compound
    - metrics.server
    - logstash.server
    - sensu.server
