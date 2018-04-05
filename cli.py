#
# cli.py - CLI for OCI Operations
#
# coding: utf-8
# Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
#
# Maintainer: David Ryder
#
import sys
import json
import re
import oci # OCI SDK
from utilities import jsonListFind, jsonListFind2, jsonListFindAll
from operations import Operations

# Arguments
#
# python oci-cli.py <config-file> <cmd> <cmd options>
#
nArgs = len(sys.argv)
if nArgs >= 3:
    configFile = sys.argv[1]
    cmd = sys.argv[2]
    config = oci.config.from_file(file_location=configFile)
    OCI_SSH_KEY_PUB = open( config['ssh_key_pub'], "r" ).read().strip()

else:
    cmd = "help"


# Clients: Compute, Blockstorage, Database, Identity, Load Balancer
cp = oci.core.compute_client.ComputeClient( config )
bs = oci.core.blockstorage_client.BlockstorageClient( config )
vn = oci.core.virtual_network_client.VirtualNetworkClient( config )
db = oci.database.database_client.DatabaseClient( config )
fs = oci.file_storage.FileStorageClient( config )
id = oci.identity.IdentityClient( config )
lb = oci.load_balancer.LoadBalancerClient( config )

o = Operations( cp, bs, vn )

if cmd == "auth":
    print( config )
    print( OCI_SSH_KEY_PUB )
    print( dir( cp  ) )

elif cmd == "compute":
    # list volumes for each instance
    instances = cp.list_instances( compartment_id=config["compartment_id"] ).data
    volumes = bs.list_volumes( config["compartment_id"] ).data
    volAttachements = cp.list_volume_attachments( compartment_id=config["compartment_id"] ).data
    vnics = cp.list_vnic_attachments( compartment_id=config["compartment_id"] ).data
    v = { i.instance_id: vn.get_vnic( i.vnic_id ).data for i in vnics if i.lifecycle_state == "ATTACHED" }
    #print( "VV ", v )

    for i in instances:
        if i.lifecycle_state in ['RUNNING','AVAILABLE']:
            #print( "\n\n INSTANCE ", i.display_name, i.lifecycle_state  )
            #vnic = v[ i['id'] ]
            #print( vnic )
            ip = "NO_IP"
            if i.id in v.keys():
                vnic = v[ i.id ]
                if hasattr( vnic, 'private_ip' ):
                    ip = "%s %s" %(vnic.private_ip, vnic.public_ip )

            # va is a list of volume_id attached to this instance
            va = [ i.volume_id for i in jsonListFindAll( volAttachements, "instance_id", i.id ) if i.lifecycle_state in ['ATTACHED','AVAILABLE'] ]
            # volume attachments matching this instance.id
            volsAttached = [ xx.display_name for xx in  [ jsonListFind( volumes, "id", i) for i in va ] ]
            totalStorage = sum( [ xx.size_in_mbs for xx in  [ jsonListFind( volumes, "id", i) for i in va ] ] )
            out = ", ".join( [ i.display_name, i.lifecycle_state, i.shape, i.region, ip, "..."+i.id[-6:], str( len( volsAttached )), str( totalStorage ), str( volsAttached ) ] )
            print( out )

elif cmd == "storage":
    volAttachements = cp.list_volume_attachments( compartment_id=config["compartment_id"] ).data
    r1 = bs.list_volumes( config["compartment_id"] ).data
    for i in r1:
        volA = jsonListFind( volAttachements, "volume_id", i.id )
        iqn = "???????"
        if hasattr( volA, 'iqn' ):
            iqn = volA.iqn
        out = ", ".join( map( str, [ i.display_name, i.lifecycle_state, i.size_in_mbs, i.id[-6:], "..."+iqn[-6:] ] ) )
        print( out )

elif cmd == "database":
    dbSystems = db.list_db_systems( compartment_id=config["compartment_id"] )
    for i in dbSystems.data:
        dbNodes = db.list_db_nodes( compartment_id=config["compartment_id"], db_system_id=i.id )
        dbnl = [ (x.hostname, x.lifecycle_state) for x in dbNodes.data  ]
        shapeComponents = list( re.findall( r'([a-zA-Z]+)\.([a-zA-Z]+)([0-9]+)\.([0-9]+)', i.shape )[0] )
        out = ", ".join( map( str, [ i.display_name, i.version, i.id[-6:], i.hostname, i.shape ] + shapeComponents +
                                   [ i.cpu_core_count, i.database_edition, i.lifecycle_state, i.availability_domain, dbnl ] ) )
        print( out )

elif cmd == "databasever":
    dbv  =  db.list_db_versions( compartment_id=config["compartment_id"] )
    print( dbv.data )

elif cmd == "images":
    r1 = cp.list_images( config["compartment_id"] ).data
    for i in r1:
        out = ", ".join( map( str, [ i.display_name,  i.id, "..."+i.id[-6:] ] ) )
        print( out )

elif cmd == "availabilityDomains":
    r1 = id.list_availability_domains( config["compartment_id"] ).data
    r1 = id.list_availability_domains( config["tenancy"] ).data
    for i in r1:
        out = ", ".join( map( str, [ i.name, "..."+i.compartment_id[-6:] ] ) )
        print( out )

elif cmd == "filesystems":
    a1 = id.list_availability_domains( config["tenancy"] ).data
    #availabilityDomains = [ i.name for i in r1 ]
    #print( availabilityDomains )
    for ad in a1:
        r1 = fs.list_file_systems( config["compartment_id"], availability_domain=ad.name).data
        for i in r1:
            out = ", ".join( map( str, [ ad.name, i.display_name, "..."+i.id[-6:], i.metered_bytes ] ) )
            print( out )

elif cmd == "compartments":
    r1 = id.list_compartments( config["tenancy"] ).data
    for i in r1:
        out = ", ".join( map( str, [ i.description,  i.id, "..."+i.id[-6:] ] ) )
        print( out )

elif cmd == "loadbalancers":
    lbShapes = lb.list_shapes( config["compartment_id"] ).data
    r1 = lb.list_load_balancers( config["compartment_id"] ).data
    for i in r1:
        rateMbps = re.findall( r'([0-9]+)Mbps', i.shape_name )[0]
        out = ", ".join( map( str, [ i.display_name,  rateMbps, i.shape_name, "..."+i.id[-6:] ] ) )
        print( out )

elif cmd == "users":
    r1 = id.list_users( config["tenancy"] ).data
    for i in r1:
        out = ", ".join( map( str, [ i.description,  i.id, "..."+i.id[-6:] ] ) )
        print( out )

elif cmd == "shapes":
    r1 = cp.list_shapes( config["compartment_id"] ).data
    for i in r1:
        shapeComponents = list( re.findall( r'([a-zA-Z]+)\.([a-zA-Z]+)([0-9]+)\.([0-9]+)', i.shape )[0] )
        out = ", ".join( map( str, [ i.shape ] + shapeComponents ) )
        print( out )

elif cmd == "instances0":
    for i in cp.list_instances( compartment_id=config["compartment_id"] ).data:
        print( i.display_name, i.shape, i.region, i.id[-6:] )

elif cmd == "instances1":
    for i in cp.list_instances( compartment_id=config["compartment_id"] ).data:
        vols = [ (bs.get_volume( i.volume_id ).data.display_name, bs.get_volume( i.volume_id ).data.size_in_mbs) for i in
                    [ cp.get_volume_attachment( i.id ).data for i in
                      cp.list_volume_attachments( compartment_id=config["compartment_id"], instance_id=i.id ).data ] ]
        print( i.display_name, i.shape, i.region, i.id[-6:], vols )

elif cmd == "instanceDetails":
    instanceName = sys.argv[3]
    instances = cp.list_instances( compartment_id=config["compartment_id"] ).data
    instance = jsonListFind( instances, "display_name", instanceName )
    r1 = cp.get_instance( instance.id ).data
    print( r1 )

elif cmd == "instanceAction":
    instanceName = sys.argv[3]
    instanceAction = sys.argv[4] # start stop softreset reset
    instance = jsonListFind( cp.list_instances( compartment_id=config["compartment_id"] ).data, "display_name", instanceName )
    r1 = cp.instance_action( instance.id, instanceAction )
    print( r1 )

elif cmd == "createVCN":
    data = oci.core.models.CreateVcnDetails()
    data.cidr_block = "10.0.0.0/16"
    data.display_name = "DDR_VCN1"
    data.compartment_id = config["compartment_id"]
    vn.create_vcn( data )

elif cmd == "subnetCreate":
    vcnName = sys.argv[3] # name of vcn to create subnet
    subnetName = sys.argv[4]
    cidr = sys.argv[5] # "10.0.3.0/24"
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    compartment_id = config["compartment_id"]
    vcn = jsonListFind( vn.list_vcns( compartment_id ).data, "display_name", vcnName )
    subnets = vn.list_subnets( compartment_id, vcn_id = vcn.id ).data
    print( vcn )
    data = oci.core.models.CreateSubnetDetails()
    data.vcn_id = vcn.id
    print( vcnName, data.vcn_id )
    data.availability_domain = availability_domain
    data.cidr_block = cidr
    data.compartment_id = compartment_id=config["compartment_id"]
    data.display_name = subnetName
    ##data.dns_label = "DDRDNS1"
    vn.create_subnet( data )

elif cmd == "subnetUpdate":
    vcnName = sys.argv[3]
    subnetName = sys.argv[4]
    subnetNewName = sys.argv[5]
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    compartment_id = config["compartment_id"]
    vcn = jsonListFind( vn.list_vcns( compartment_id ).data, "display_name", vcnName )
    subnets = vn.list_subnets( config["compartment_id"], vcn_id = vcn.id ).data
    subnet = jsonListFind( subnets, "display_name", subnetName )
    print( "Subnet updating ", "..."+subnet.id[-6:], subnetNewName )
    for i in subnets:
        print( i.display_name, "..."+i.id[-6:] )
    subnet = jsonListFind( subnets, "display_name", subnetName )
    vn.update_subnet(subnet.id, { "displayName": subnetNewName } )

elif cmd == "bootVolumeList":
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    compartment_id = config["compartment_id"]
    bootVols = o.listBootVolumes( compartment_id, availability_domain ).data
    for i in bootVols:
        print( i.display_name, i.lifecycle_state, "..."+i.id[-6:] )

elif cmd == "bootVolumeAttachments":
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    compartment_id = config["compartment_id"]
    bootVolsAtta = o.listBootVolumeAttachments( compartment_id, availability_domain ).data
    for i in bootVolsAtta:
        print( i.display_name, i.lifecycle_state, "..."+i.id[-6:] )

elif cmd == "bootVolumeUpdate":
    bootVolumeName = sys.argv[3] # boot volume name
    bootVolumeNewName = sys.argv[4] # boot volume new name
    o.bootVolumeUpdate( config["compartment_id"], config["availability_domain"], bootVolumeName, bootVolumeNewName)

elif cmd == "bootVolumeAttach":
    instanceName = sys.argv[3] # boot volume name
    bootVolumeName = sys.argv[4] # boot volume name
    o.bootVolumeAttach( config["compartment_id"], instanceName, bootVolumeName )

elif cmd == "bootVolumeDetatch":
    instanceName = sys.argv[3] # boot volume name
    bootVolumeName = sys.argv[3] # boot volume name
    o.bootVolumeDetach( config["compartment_id"], config["availability_domain"], instanceName, bootVolumeName )

elif cmd == "bootVolumeDelete":
    bootVolumeName = sys.argv[3] # boot volume name
    o.bootVolumeDelete( config["compartment_id"], config["availability_domain"], bootVolumeName )

elif cmd == "instanceLaunchNewBootVol":
    # launch a new instance and attach to a new boot volume
    vcnName = sys.argv[3] # name of vcn
    subnetName = sys.argv[4] # name of subnet
    instanceName = sys.argv[5]
    compartment_id = config["compartment_id"]
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    imageName = "Oracle-Linux-7.4-2017.11.15-0"
    shapeName = "VM.Standard1.2"
    vcn = jsonListFind( vn.list_vcns( compartment_id ).data, "display_name", vcnName )
    subnet = jsonListFind( vn.list_subnets( compartment_id, vcn_id = vcn.id ).data, "display_name", subnetName )
    image = jsonListFind( cp.list_images( compartment_id ).data, "display_name", imageName )
    data = { "availabilityDomain": availability_domain,
             "compartmentId": compartment_id,
             "createVnicDetails":  { "displayName": "VN1", "subnetId": subnet.id },
             "displayName": instanceName,
             "shape": shapeName,
             "imageId": image.id,
             "sourceDetails": { "sourceType": "image", "imageId": image.id },
             "metadata" : {  "ssh_authorized_keys": OCI_SSH_KEY_PUB }
            }
    print( data )
    r1 = cp.launch_instance( data )


    print( r1 )

elif cmd == "instanceLaunchBootVol":
    # launch a new instance and attach to an existing boot volume
    vcnName = sys.argv[3] # name of vcn
    subnetName = sys.argv[4] # name of subnet
    instanceName = sys.argv[5] # name of this instance
    bootVolName = sys.argv[6] # boot volume to attach
    compartment_id = config["compartment_id"]
    availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
    imageName = "Oracle-Linux-7.4-2017.11.15-0"
    shapeName = "VM.Standard1.2"

    # VCN and Subnet
    vcn = jsonListFind( vn.list_vcns( config["compartment_id"] ).data, "display_name", vcnName )
    subnet = jsonListFind( vn.list_subnets( config["compartment_id"], vcn_id = vcn.id ).data, "display_name", subnetName )

    # Boot Volumes
    bootVolume = jsonListFind( o.listBootVolumes( compartment_id, availability_domain ).data, "display_name", bootVolName, exact = False )
    print( "Using Boot Volume ", bootVolume.display_name, bootVolume.id )

    # VNIC
    d1 = oci.core.models.CreateVnicDetails()
    d1.display_name = "VN1"
    d1.subnet_id = subnet.id

    image = jsonListFind( cp.list_images( config["compartment_id"] ).data, "display_name", imageName  )
    #              "imageId": image.id,
    data = { "availabilityDomain": availability_domain,
             "compartmentId": config["compartment_id"],
             "createVnicDetails":  { "displayName": "VN1", "subnetId": subnet.id },
             "displayName": instanceName,
             "shape": shapeName,
             "imageId": image.id,
             "sourceDetails": { "sourceType": "bootVolume", "bootVolumeId": bootVolume.id },
             "metadata" : {  "ssh_authorized_keys": OCI_SSH_KEY_PUB }
            }
    r1 = o.launchInstance( data ) # or cp.launch_instance( data )
    print( r1 )

elif cmd == "instanceTerminate":
    instanceName = sys.argv[3]
    o.terminateInstance( config["compartment_id"], instanceName )

elif cmd == "instanceTerminateMOD":
    # works requries SDK API to modified
    instanceName = sys.argv[3]
    instances = cp.list_instances( compartment_id=config["compartment_id"] ).data
    instance = jsonListFind( instances, "display_name", instanceName )
    kwargs = { 'preserveBootVolume': "True" }
    print( "Terminating: ", instance.display_name, "..."+instance.id[-6:])
    r1 = cp.terminate_instance( instance.id, **kwargs )
    print( r1 )



elif cmd == "volumeAttachments":
    volumeAttachments = cp.list_volume_attachments( compartment_id=config["compartment_id"] ).data
    for i in volumeAttachments:
        print( i )

elif cmd == "vnics":
    instances = cp.list_instances( compartment_id=config["compartment_id"] ).data
    vnics = cp.list_vnic_attachments( compartment_id=config["compartment_id"] ).data
    for i in vnics:
        instance = jsonListFind2( instances, "id", i.instance_id )
        vnic = vn.get_vnic( i.vnic_id ).data
        print( instance.display_name, vnic.private_ip, vnic.public_ip, vnic.mac_address   )


elif cmd == "attachVolume":
    instanceName = sys.argv[3]
    volumeName = sys.argv[4]
    opcAttachVolume( config["compartment_id"], instanceName, volumeName )

elif cmd == "detachVolume":
    volumeName = sys.argv[3]
    opcDetachVolume( config["compartment_id"], volumeName )


# elif cmd == "listVolumes":
#     # list all volumes in this compartment id
#     # basic information about the volume
#     volAttachements = opcListVolumeAttachments()
#     for i in opcListVolumes():
#         volA = jsonListFind( volAttachements, "volumeId", i['id'] )
#         iqn = "???????"
#         if 'iqn' in volA.keys():
#             iqn = volA['iqn']
#         print( i['displayName'], i['state'], "..."+i['id'][-6:], "..."+iqn[-6:] ) # j['compartmentId']

elif cmd == 'iscsiShowAttach':
    volName = sys.argv[3]
    # generate iscsi connect commands for a volume
    volList =  bs.list_volumes( config["compartment_id"] ).data
    volAttachements = cp.list_volume_attachments( compartment_id=config["compartment_id"] ).data
    v = jsonListFind( volList, 'display_name', volName ) # find the volume
    va = jsonListFind( volAttachements, "volume_id", v.id ) # find the volume attachment
    volIqn = va.iqn
    volIp = "{ip}:{port}".format( ip=va.ipv4, port=va.port )
    volId = va.volume_id
    volChapPwd = va.chap_secret

    cmdConnect = "sudo iscsiadm -m node -o new -T {volIqn} -p {volIp} \nsudo iscsiadm -m node -o update -T {volIqn} -n node.startup -v automatic \nsudo iscsiadm -m node -T {volIqn} -p {volIp} -l".format( volIqn=volIqn, volIp=volIp )
    cmdDisconnect = "sudo iscsiadm -m node -T {volIqn} -p {volIp} -u".format( volIqn=volIqn, volIp=volIp )
    print( "# Attach ", volName )
    print( cmdConnect )

elif cmd == 'iscsiShowDetach':
    volName = sys.argv[3]
    # generate iscsi connect commands for a volume
    volList =  bs.list_volumes( config["compartment_id"] ).data
    volAttachements = cp.list_volume_attachments( compartment_id=config["compartment_id"] ).data
    v = jsonListFind( volList, 'display_name', volName ) # find the volume
    va = jsonListFind( volAttachements, "volume_id", v.id ) # find the volume attachment
    volIqn = va.iqn
    volIp = "{ip}:{port}".format( ip=va.ipv4, port=va.port )
    volId = va.volume_id
    volChapPwd = va.chap_secret

    cmdConnect = "sudo iscsiadm -m node -o new -T {volIqn} -p {volIp} \nsudo iscsiadm -m node -o update -T {volIqn} -n node.startup -v automatic \nsudo iscsiadm -m node -T {volIqn} -p {volIp} -l".format( volIqn=volIqn, volIp=volIp )
    cmdDisconnect = "sudo iscsiadm -m node -T {volIqn} -p {volIp} -u".format( volIqn=volIqn, volIp=volIp )
    print( "# Detach ", volName )
    print( cmdDisconnect )

else:
    print( "Usage: python oci-cli.py <config-file> <cmd>" )
    print( "Commands: auth, compute, database, storage, shapes, images, loadbalancers, filesystems, " )
