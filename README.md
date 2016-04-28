# Pivotal HDB on Hortonworks HDP Sandbox

<img src="https://raw.githubusercontent.com/dbbaskette/hdb-on-hdp/gh-pages/images/hdb.jpeg?token=ACbVkUI1WnnUpyJAOIAZbDH4AHJsBj63ks5WM91-wA%3D%3D" width="300">

#### Packer-Based Build Process for adding Pivotal HDB to the Hortonworks HDP Sandbox

**Requirements:**  

* Packer  
* VMware Fusion
* Hortonworks HDP Sandbox 2.4
* Pivotal HDB Package
* Pivotal HDB Ambari Plugin Package
* Apache MADlib for HDB Package

This release only works for the vmware version.
* Download the VMWARE version of Sandbox 2.4 in to the main hdp-on-hpd directory. Leave it in its native downloaded format.
* Place Pivotal HDB and Ambari Plugin packages in ./bins Directory. Leave them in their native *.tar.gz format.
* Place MADlib Package in ./plugins.   Leave in Native *.tar.gz format
* Run ./build.sh vmware
* Output will be a Zip file containing the VM.    Move and unzip where you want to store the VM.  It does not require an import to work.

This release will automatically download the HDB Tutorials (which are not completed).   This process also will load data into Hive for immediate query by PXF

* Boot up the VM
* login to Ambari at <ip>:8080 with admin/admin
* start HDB and PXF
* login to the command line as gpadmin (gpadmin/gpadmin)
* Type:  psql -d template
* from the psql shell type: select * from hcatalog.faa.otp limit 10;

This will directly query the Hive table leveraging the metadata from HCATALOG



logins:

VM:
root/hawq2016
gpadmin/gpadmin
Ambari:
admin/admin
