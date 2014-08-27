# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

base_dir = File.dirname(__FILE__)
[ 'salt/master/vagrant/templates', 'salt/minions/vagrant/templates' ].each do |dir|
  unless File.exists?("#{base_dir}/#{dir}/key")
    key = OpenSSL::PKey::RSA.new 2048
    open "#{base_dir}/#{dir}/key", 'w' do |io| io.write key.to_pem end
    open "#{base_dir}/#{dir}/key.pub", 'w' do |io| io.write key.public_key.to_pem end
  end
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.define "master", primary: true do |master|

    # mount salt required folders
    master.vm.synced_folder "salt", "/srv/salt/"
    master.vm.synced_folder "pillars", "/srv/pillars/"
    #master.vm.synced_folder "vendor/_root", "/srv/salt-formulas", type: "rsync", rsync__args: ["--verbose", "--archive", "--delete", "-z", "-L"]
    master.vm.synced_folder "vendor/_root", "/srv/salt-formulas"
    master.vm.synced_folder "vendor/formula-repos", "/srv/formula-repos"

    master.vm.box = "precise64"
    master.vm.box_url = "http://files.vagrantup.com/precise64.box"
    master.vm.hostname = "master"

    master.vm.network :private_network, ip: "192.168.33.80"

    master.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "1024"]
      v.name = "master"
    end
      
    master.vm.provision :salt do |salt|

      master_config_dir   = 'salt/master/vagrant/templates/'
      salt.install_master = true
      salt.master_config  = master_config_dir + "master"
      salt.master_key     = master_config_dir + 'key'
      salt.master_pub     = master_config_dir + 'key.pub'
      salt.seed_master = { master: salt.master_pub}

      minion_config_dir   = 'salt/minions/vagrant/templates/'
      salt.minion_config  = minion_config_dir + "minion.master"
      salt.minion_key     = minion_config_dir + 'key'
      salt.minion_pub     = minion_config_dir + 'key.pub'

      salt.verbose = true

    end

  end

  config.vm.define "monitoring" do |monitoring|

    monitoring.vm.synced_folder "data/graphite/whisper", "/srv/graphite/storage/whisper", mount_options: ['dmode=777', 'fmode=666'], create: true
    monitoring.vm.synced_folder "data/elasticsearch", "/var/lib/elasticsearch", mount_options: ['dmode=777', 'fmode=666'], create: true

    monitoring.vm.box = "precise64"
    monitoring.vm.box_url = "http://files.vagrantup.com/precise64.box"
    monitoring.vm.hostname = "monitoring"

    monitoring.vm.network :private_network, ip: "192.168.33.81"

    monitoring.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "2048"]
      v.name = "monitoring"
    end
      
    monitoring.vm.provision :salt do |salt|

      minion_config_dir   = 'salt/minions/vagrant/templates/'
      salt.minion_config  = minion_config_dir + "minion.monitoring"
      salt.minion_key     = minion_config_dir + 'key'
      salt.minion_pub     = minion_config_dir + 'key.pub'

      salt.verbose = true
    end

  end

  config.vm.define "client1" do |node|

    node.vm.box = "precise64"
    node.vm.box_url = "http://files.vagrantup.com/precise64.box"
    node.vm.hostname = "client1"

    node.vm.network :private_network, ip: "192.168.33.82"

    node.vm.provider "virtualbox" do |v|
      v.customize ["modifyvm", :id, "--memory", "1024"]
      v.name = node.vm.hostname
    end
      
    node.vm.provision :salt do |salt|

      minion_config_dir   = 'salt/minions/vagrant/templates/'
      salt.minion_config  = minion_config_dir + "minion.client"
      salt.minion_key     = minion_config_dir + 'key'
      salt.minion_pub     = minion_config_dir + 'key.pub'

      salt.verbose = true
    end

  end

  #script = <<-SCRIPT
  #  mkdir -p /etc/salt
  #  cp /srv/salt/minions/vagrant/templates/minion /etc/salt/minion
  #  service salt-minion restart
  #  sleep 5 # This might not be needed, but why rush these things?
  #  salt-call state.highstate --local --retcode-passthrough pillar="{htaccess_users: ~}"
  #SCRIPT
  #config.vm.provision :shell, inline: script, keep_color: false

end
