python-lxml:
  pkg.installed

/etc/salt/master:
  file.managed: []

/etc/salt/minion:
  file.managed: []

salt-master:
  service.running:
    - watch:
      - file: /etc/salt/master

salt-minion:
  service.running:
    - watch:
      - file: /etc/salt/minion

/root/.ssh/id_rsa:
{% if 'salt_master_private_key' in pillar %}
  file.managed:
    - contents_pillar: salt_master_private_key
    - 0600
{% else %}
  file.absent
{% endif %}
