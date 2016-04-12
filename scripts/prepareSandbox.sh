#!/usr/bin/env bash

setAmbariPassword(){
ambari-admin-password-reset << EOF
admin
admin
EOF
}


buildRepos(){
    cd /tmp/bins

    for fileName in ./*
    do
        tar xvfz $fileName
        targetDir=$(tar -tf $fileName | grep -o '^[^/]\+/' | sort -u)
        ./$targetDir/setup_repo.sh
    done

installPlugin(){
    service httpd start
    yum install -y hawq-plugin
    #rm -rf /etc/yum.repos.d/hawq-plugin*.repo
    cd /var/lib/hawq/
    ./add_hdb_repo.py -u admin -p admin
    ambari-server restart
}

fixHue(){
    if [ $(whoami) != "root" ]; then
        echo Must be root. Bye.
        exit 1
    fi
    add_paths=$(/bin/ls -d /var/www/html/hawq* /var/www/html/PIVO*)
    pushd /etc/httpd/conf.d/
    cp hue.conf hue.conf.save
    for p in $add_paths
    do
        add_proxy=$(basename $p | sed 's/:$//')
        sed -i "6i \  ProxyPass /$add_proxy !" hue.conf
    done
    service httpd restart
    popd

}

modifyConfigs(){

    pip install requests
    python /tmp/scripts/modifyConfigs.py

}

cleanup(){
    dd if=/dev/zero of=/bigemptyfile bs=4096k
    rm -rf /bigemptyfile

}


}
_main() {
    sleep 60
	buildRepos
	fixHue
	setAmbariPassword
	installPlugin
	modifyConfigs
	python /tmp/scripts/installHAWQ.py
    cleanup

}


_main "$@"