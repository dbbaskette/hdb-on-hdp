#!/usr/bin/env bash

setAmbariPassword(){
ambari-admin-password-reset << EOF
admin
admin
EOF
}


buildRepos(){
    cd /tmp/bins

    for fileName in ./*.tar.gz
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

installMadlib(){
    cd /tmp/bins
    chown -R gpadmin: /tmp/bins
    su gpadmin -l -c "cd /tmp/bins;tar xvfz madlib* --strip=1"
    su gpadmin -l -c "source /usr/local/hawq/greenplum_path.sh;cd /tmp/bins;gppkg -i madlib*.gppkg"
    su gpadmin -l -c "source /usr/local/hawq/greenplum_path.sh;cd /tmp/bins;\$GPHOME/madlib/bin/madpack install -s madlib -p hawq -c gpadmin@sandbox.hortonworks.com:10432/template1"
    # echo "INSTALL PL Extensions"
    # gppkg -i $PLR_FILE
    # gppkg -i $PLPERL_FILE
    # gppkg -i $PLJAVA_FILE
    # gppkg -i $POSTGIS_FILE
    # source /usr/local/greenplum-db/greenplum_path.sh
    # gpstop -r -a
    # psql -d template1 -f $GPHOME/share/postgresql/contrib/postgis-2.0/postgis.sql
    # createlang plr -d template1
    # createlang plperl -d template1
    # createlang pljava -d template1
    # psql -d template1 -f $GPHOME/share/postgresql/pljava/install.sql
    # psql -d gpadmin -f $GPHOME/share/postgresql/contrib/postgis-2.0/postgis.sql
    # createlang plr -d  gpadmin
    # createlang plperl -d gpadmin
    # createlang pljava -d gpadmin
    # psql -d gpadmin -f $GPHOME/share/postgresql/pljava/install.sql
}



installPGCcrypto(){
    gppkg -i $PGCRYPTO_FILE
    psql -d template1 -f $GPHOME/share/postgresql/contrib/pgcrypto.sql
    psql -d gpadmin -f $GPHOME/share/postgresql/contrib/pgcrypto.sql
    echo "source /home/gpadmin/gp-wlm/gp-wlm_path.sh" >> /home/gpadmin/.bashrc
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
	installMadlib
    cleanup


}


_main "$@"