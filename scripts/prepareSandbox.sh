#!/usr/bin/env bash

setAmbariPassword(){
ambari-admin-password-reset << EOF
admin
admin
EOF
}


buildRepos(){
    cd /tmp/bins


    # NEED TO FIX TO ONLY DO PLUGIN AND HDB

    for fileName in ./*.tar.gz
    do
        tar xvfz $fileName
        targetDir=$(tar -tf $fileName | grep -o '^[^/]\+/' | sort -u)
        echo "TARGET=$targetDir"
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
    rm -rf /tmp/bins /tmp/plugins
    rm -f /home/gpadmin/gpdb-sandbox-tutorials/faa.tar.gz
    rm -f /home/gpadmin/gpdb-sandbox-tutorials/faa/*.csv
    dd if=/dev/zero of=/bigemptyfile bs=4096k
    rm -rf /bigemptyfile
}

installMadlib(){
    # cd /tmp/plugins
    chown -R gpadmin: /tmp/plugins
    su gpadmin -l -c "cd /tmp/plugins;tar xvfz madlib*.gz"
    su gpadmin -l -c "source /usr/local/hawq/greenplum_path.sh;cd /tmp/plugins;gppkg -i madlib*.gppkg"
    su gpadmin -l -c "source /usr/local/hawq/greenplum_path.sh;cd /tmp/plugins;\$GPHOME/madlib/bin/madpack install -s madlib -p hawq -c gpadmin@sandbox.hortonworks.com:10432/template1"

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


setupTutorialEnv(){

    # ENABLE HCAT PERMANENTLY

    echo "hcatalog_enable = true" >> /data/hawq/master/postgresql.conf

    # This gets the data for the hdb Tutorials

    echo "SETTING UP TUTORIAL ENVIROMENT"
    su gpadmin -l -c "git clone --depth=1 https://github.com/dbbaskette/hdb-tutorials.git"
    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa/otp;gunzip *.gz"
    su gpadmin -l -c "hadoop fs -mkdir -p /hdb-tutorials/otp"
    su gpadmin -l -c "hadoop fs -mkdir -p /hdb-tutorials/csv"

    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa/csv;hadoop fs -put *.csv /hdb-tutorials/csv/."
    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa/otp;hadoop fs -put otp* /hdb-tutorials/otp/."
    su gpadmin -l -c "rm -rf  /home/gpadmin/hdb-tutorials/faa/otp"

    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa;chmod +x *.sh;./hive-setup.sh"
    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa;hive -f create_hive_load_table.sql"
    su gpadmin -l -c "cd /home/gpadmin/hdb-tutorials/faa;hive -e 'create table faa.otp as select * from faa.ext_otp;'"




    # Gets the Data for the Horton
    #su gpadmin -l -c "mkdir hivedata;cd hivedata;wget http://seanlahman.com/files/database/lahman591-csv.zip;unzip *.zip;rm -f *.zip"



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
	setupTutorialEnv
    #cleanup


}


_main "$@"