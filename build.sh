#!/usr/bin/env bash

SANDBOX_BASENAME="HDP_2.4_vmware_v3"
OVFTOOL_BIN="/Applications/VMware Fusion.app/Contents/Library/VMware OVF Tool/ovftool"
VMRUN_BIN="/Applications/VMware Fusion.app/Contents/Library/vmrun"

convertOVA(){


    OVA_NAME="$SANDBOX_BASENAME.ova"
    echo "CONVERTING OVA to VMX"
    "$OVFTOOL_BIN" $OVA_NAME ./$SANDBOX_BASENAME/$SANDBOX_BASENAME.vmx
    echo "CONVERSION COMPLETE"

}



changeRootPasswordVMWARE(){
    echo "Starting $SANDBOX_BASENAME"
    "$VMRUN_BIN" -T fusion start $SANDBOX_BASENAME/$SANDBOX_BASENAME.vmwarevm/$SANDBOX_BASENAME.vmx
    guestIP=$("$VMRUN_BIN" -T fusion getGuestIPAddress $SANDBOX_BASENAME/$SANDBOX_BASENAME.vmwarevm/$SANDBOX_BASENAME.vmx -wait)
    echo "$guestIP is the guest IP"
    echo "CHANGING DEFAULT ROOT PASSWORD"
    ./scripts/rootPasswordChange.sh $guestIP hadoop hawq2016
    echo "ROOT PASSSWORD CHANGED"

}

subVMPath(){
    #sed -i 's/%HOSTNAME%/$fqdn/" /tmp/configs/gpinitsystem_singlenode
    VMPATH="$SANDBOX_BASENAME\/$SANDBOX_BASENAME.vmwarevm\/$SANDBOX_BASENAME.vmx"
    sed -i '' "s/VMPATH/$VMPATH/" ./hdb-on-hdp.json



}




_main() {
    case $1 in
        vmware)
            echo  "BUILD VMWARE MACHINE"
            if [ ! -f ./$SANDBOX_BASENAME/$SANDBOX_BASENAME.vmwarevm/$SANDBOX_BASENAME.vmx ]
            then
                echo "$SANDBOX_BASENAME VMX FILE NOT FOUND"
                convertOVA
                changeRootPasswordVMWARE
                "$VMRUN_BIN" -T fusion stop $SANDBOX_BASENAME/$SANDBOX_BASENAME.vmwarevm/$SANDBOX_BASENAME.vmx
            fi
            subVMPath
            packer build -force -only=vmware hdb-on-hdp.json



            ;;
        vbox)
            echo "BUILD VIRTUAL BOX MACHINE"
            ;;
        *)
            echo "INVALID OPTION"
            exit 1;

    esac

}


_main "$@"