
# DSD pkg repo
/var/tmp/dsd-apt.key:
  file.managed:
    - contents_pillar: pkgrepo:gpg_key

dsd-apt-key:
  cmd:
    - run
    - name: apt-key add /var/tmp/dsd-apt.key
    - unless: apt-key list | grep '{{ salt['pillar.get']('pkgrepo:keyid', '') }}'
    - require:
      - file: /var/tmp/dsd-apt.key

dsd-deb:
  pkgrepo.managed:
    - humanname: DSD Apt package repo
    - name: deb [arch={{ grains['osarch'] }}] {{ salt['pillar.get']('pkgrepo:url', 'http://repo1.dsd.io/') }} {{ grains['oscodename'] }} main
    - file: /etc/apt/sources.list.d/dsd.list
    - require:
      - cmd: dsd-apt-key
    - require_in:
      - pkg.*


apt-update:
  cmd:
    - run
    - name: apt-get update
    - require:
      - pkgrepo: dsd-deb
    - require_in:
      - pkg.*
    
