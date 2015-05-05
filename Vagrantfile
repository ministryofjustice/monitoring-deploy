# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
# -*- ruby -*-
VAGRANTFILE_API_VERSION = "2"

stub_name = "mon-v"

precise_box = 'mikepea/precise64_bigpkg_salt'
trusty_box = 'mikepea/trusty64_bigpkg_salt'
#precise_box = 'hashicorp/precise64'
#trusty_box = 'ubuntu/trusty64'

base_dir = File.dirname(__FILE__)
[ 'salt/master/vagrant/templates', 'salt/minions/vagrant/templates' ].each do |dir|
  unless File.exists?("#{base_dir}/#{dir}/key")
    key = OpenSSL::PKey::RSA.new 2048
    open "#{base_dir}/#{dir}/key", 'w' do |io| io.write key.to_pem end
    open "#{base_dir}/#{dir}/key.pub", 'w' do |io| io.write key.public_key.to_pem end
  end
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  minions = [
    { name: 'monitoring-01', memory: '4096', box: precise_box, ip: '192.168.33.41', highstate: true },
    { name: 'client-01', memory: '1024', box: precise_box, ip: '192.168.33.42' },
    { name: 'client-02', memory: '1024', box: trusty_box, ip: '192.168.33.43' },
  ]

  dev_formula = [ 'elasticsearch', 'metrics', 'logstash', 'sensu', 'sentry', 'monitoring' ]
  dynamic_dir = ['_modules', '_grains', '_renderers', '_returners', '_states']

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  config.vm.define "master.#{stub_name}", primary: true do |master|

    # Try to force this to virtualbox, and VMWare. We have to mention vmware_fusion here 
    master.vm.provider "virtualbox"
    master.vm.provider "vmware_fusion"

    # mount salt required folders
    master.vm.synced_folder "salt", "/srv/salt/"
    master.vm.synced_folder "pillars", "/srv/pillars/"
    master.vm.synced_folder "vendor/_root", "/srv/salt-formulas"
    master.vm.synced_folder "vendor/formula-repos", "/srv/formula-repos"

    dev_formula.each do |f|
      master.vm.synced_folder "../#{f}-formula/#{f}/", "/srv/salt/#{f}" if File.directory?("../#{f}-formula/#{f}")

      # This loop takes care of dynamic modules states etc.
      # You need to vagrant provision when you create new states
      # thereafter the changes are synced
      dynamic_dir.each do |ddir|
        if File.directory?("../#{f}-formula/#{ddir}")
          master.vm.synced_folder "../#{f}-formula/#{ddir}/", "/srv/salt-dynamic/#{f}"
          master.vm.provision :shell,
            inline: "mkdir -p /srv/salt/#{ddir} && for f in /srv/salt-dynamic/#{f}/*; do ln -sf $f /srv/salt/#{ddir}; done"
        end
      end
    end

    master.vm.box = "ubuntu/trusty64"
    master.vm.hostname = "master.#{stub_name}"

    master.vm.network :private_network, ip: "192.168.33.40"

    master.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "1024"]
      v.name = "master.#{stub_name}"
    end

    master.vm.provision :shell,
      inline: "apt-get -y install lvm2"

    master.vm.provision :salt do |salt|

      master_config_dir   = 'salt/master/vagrant/templates/'

      salt.install_master = true
      salt.master_config  = master_config_dir + "master"
      salt.master_key     = master_config_dir + 'key'
      salt.master_pub     = master_config_dir + 'key.pub'
      salt.seed_master   = {
        master.vm.hostname => salt.master_pub,
      }

      minion_config_dir   = 'salt/minions/vagrant/templates/'
      salt.minion_config  = minion_config_dir + "minion.master"
      salt.minion_key     = minion_config_dir + 'key'
      salt.minion_pub     = minion_config_dir + 'key.pub'

      salt.install_type = "git"
      salt.install_args = "v2014.1.13"
      minions.each do |m|
        salt.seed_master["#{m[:name]}.#{stub_name}"] = salt.minion_pub
      end

      # Set the minion id
      salt.bootstrap_options = "-i #{master.vm.hostname}"

      salt.run_highstate = true
      salt.verbose = true

    end

  end

  minions.each do |minion|
    config.vm.define "#{minion[:name]}.#{stub_name}" do |vm_config|

      vm_config.vm.box = minion[:box]
      vm_config.vm.hostname = "#{minion[:name]}.#{stub_name}"

      if minion[:name] =~ /monitoring/
        vm_config.vm.synced_folder "data/graphite/whisper", "/srv/graphite/storage/whisper", mount_options: ['dmode=777', 'fmode=666'], create: true
      end

      # Force it to the virtualbox provider - the IPs are fixed so it has to be
      # on virtual box else it will complain about networks not matching
      vm_config.vm.provider "virtualbox"
      vm_config.vm.provider "vmware_fusion"

      vm_config.vm.network :private_network, ip: minion[:ip]
      minion.fetch(:code_repos, []).each do |code_repo|
        vm_config.vm.synced_folder "../#{code_repo[:repo]}", "/srv/vagrant_repos/#{code_repo[:mount]}"
      end

      vm_config.vm.provider "virtualbox" do |v|
        v.customize ["modifyvm", :id, "--memory", minion[:memory]]
        v.name = minion[:name]
      end

      metarole = minion.fetch(:metarole) { minion.fetch(:name).split('-').first }
      minion_config = "minion.#{metarole}"

      vm_config.vm.provision :shell,
        inline: "apt-get -y install lvm2"

      vm_config.vm.provision :salt do |salt|
        minion_config_dir   = 'salt/minions/vagrant/templates/'
        salt.minion_config  = minion_config_dir + minion_config
        salt.minion_key     = minion_config_dir + 'key'
        salt.minion_pub     = minion_config_dir + 'key.pub'

        salt.install_type = "git"
        salt.install_args = "v2014.1.13"
        salt.bootstrap_options = "-i #{vm_config.vm.hostname}"

        salt.verbose = true
        if minion[:highstate]
          salt.run_highstate = true
        end
      end

    end

  end

end
