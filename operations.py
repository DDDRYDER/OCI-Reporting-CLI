#
# operations.py - OCI Operations
#
# coding: utf-8
# Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
#
# Maintainer: David Ryder
#
import sys
import json
import oci
import utilities

class Operations:
    def __init__(self, cp, bs, vn ):
        self.s = None # Session
        self.shapes = None
        self.auth = None
        self.valid = False
        self.cp = cp
        self.bs = bs
        self.vn = vn

    def attachVolume( self, compartment_id, instanceName, volumeName, retries=5 ):
        il = self.cp.list_instances( compartment_id ).data
        vl = self.bs.list_volumes( compartment_id  ).data
        instance = jsonListFind( il, "display_name", instanceName )
        volume = jsonListFind( vl, "display_name", volumeName )
        data = oci.core.models.AttachVolumeDetails( )
        data.display_name = instanceName
        data.instance_id = instance.id
        data.type = "iscsi"
        data.volume_id = volume.id
        print( data )
        cp.attach_volume( data )

    def detachVolume( self, compartment_id, volumeName ):
        volList = self.bs.list_volumes( compartment_id ).data
        #print( volumeName, volList )
        volAttachements = self.cp.list_volume_attachments( compartment_id ).data
        vol = jsonListFind( volList, "display_name", volumeName ) # find the volume
        print( "VOL ", vol )
        va = jsonListFind( volAttachements, "volume_id", vol.id ) # find the volume attachment id
        volumeId = va.id # id of the volume attachment
        cp.detach_volume( volumeId )

    def listBootVolumes( self, compartment_id, availability_domain ):
        print( compartment_id, availability_domain )
        resource_path = "/bootVolumes/"
        method = "GET"
        header_params = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        query_params = {
            "availabilityDomain": availability_domain,
            "compartmentId": compartment_id
        }
        return cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            query_params=query_params,
            header_params=header_params,
            response_type="list[Instance]")

    def listBootVolumeAttachments( self, compartment_id, availability_domain ):
        resource_path = "/bootVolumeAttachments/"
        method = "GET"
        header_params = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        query_params = {
            "availabilityDomain": availability_domain,
            "compartmentId": compartment_id
        }
        return self.cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            query_params=query_params,
            header_params=header_params,
            response_type="list[Instance]")

    def launchInstance( self, launch_instance_details ):
        resource_path = "/instances/"
        method = "POST"
        header_params = { "accept": "application/json", "content-type": "application/json" }
        return cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            header_params=header_params,
            body=launch_instance_details,
            response_type="Instance")

    def terminateInstance( self, compartment_id, instanceName, preserveBootVolume=True ):
        instance = jsonListFind( cp.list_instances( compartment_id ).data, "display_name", instanceName )
        self.cp.update_instance( instance.id, { "displayName": "X_" + instanceName })
        print( "Terminating: ", instance.display_name, "..."+instance.id[-6:])
        resource_path = "/instances/{instanceId}".format( instanceId=instance.id )
        method = method = "DELETE"
        path_params = { "instanceId": instance.id }
        query_params = { "preserveBootVolume": preserveBootVolume }
        header_params = {
            "accept": "application/json",
            "content-type": "application/json",
            "if-match": "" }

        r1 = self.cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            query_params=query_params,
            path_params=path_params,
            header_params=header_params )
        print( r1 )

    def bootVolumeUpdate( self, compartment_id, availability_domain, bootVolumeName, bootVolumeNewName ):
        bootVolumes = oci_ListBootVolumes( compartment_id, availability_domain ).data
        bootVolume = jsonListFind( bootVolumes, "display_name", bootVolumeName, exact = False )
        print( "Updating ", "..."+bootVolume.id[-6:], bootVolumeNewName )
        resource_path = "/bootVolumes/{bootVolumeId}".format( bootVolumeId=bootVolume.id )
        method = "PUT"
        header_params = { "accept": "application/json", "content-type": "application/json" }
        data = { "displayName": bootVolumeNewName }
        return cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            header_params=header_params,
            body=data,
            response_type="Instance")

    def bootVolumeAttach( self, compartment_id, instanceName, bootVolumeName ):
        #availability_domain = config["availability_domain"]  # "Rmpq:PHX-AD-1"
        #compartment_id = config["compartment_id"]
        instance = jsonListFind( cp.list_instances( compartment_id ).data, "display_name", instanceName )
        bootVolumes = oci_ListBootVolumes( availability_domain, compartment_id ).data
        bootVolume = jsonListFind( bootVolumes, "display_name", bootVolumeName, exact = False )
        print( bootVolume, instance )
        print( "Attaching ", "..."+bootVolume.id[-6:], " To Instance ", "..."+instance.id[-6:] )
        resource_path = "/bootVolumeAttachments/"
        method = "POST"
        header_params = { "accept": "application/json", "content-type": "application/json" }
        data = { "bootVolumeId": bootVolume.id,
                 "instanceId": instance.id,
                 "displayName": bootVolumeName
                }
        return cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            header_params=header_params,
            body=data,
            response_type="Instance")

    def bootVolumeDetach( self, compartment_id, availability_domain, instanceName, bootVolumeName ):
        # detach the boot volume from the instance
        # instance must be stopped
        instances = self.cp.list_instances( compartment_id ).data
        bootVolumeAttachments = oci_ListBootVolumeAttachments( compartment_id, availability_domain ).data
        instance = jsonListFind( instances, "display_name", instanceName, exact = True )
        #print( instance )
        bootVolumeAttachment = jsonListFind( bootVolumeAttachments, "id", instance.id, exact = True )
        print( "BV ID", bootVolumeAttachment )
        print( "Detatching Boot Volume ", instance.display_name, bootVolumeAttachment.id )
        resource_path = "/bootVolumeAttachments/{bootVolumeAttachmentId}".format( bootVolumeAttachmentId=bootVolumeAttachment.id )
        method = "DELETE"
        path_params = None
        query_params = None
        header_params = {
            "accept": "application/json",
            "content-type": "application/json",
            "if-match": "" }

        r1 = self.cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            query_params=query_params,
            path_params=path_params,
            header_params=header_params)
        print( r1 )

    def bootVolumeDelete( self, compartment_id, availability_domain, bootVolumeName ):
        bootVolumes = oci_ListBootVolumes( compartment_id, availability_domain ).data
        bootVolume = jsonListFind( bootVolumes, "display_name", bootVolumeName, exact = False )
        print( "Deleting Boot Volume ", bootVolume.display_name, bootVolume.id )
        resource_path = "/bootVolumes/{bootVolumeAttachmentId}".format( bootVolumeAttachmentId=bootVolume.id )
        method = "DELETE"
        path_params = None
        query_params = None
        header_params = {
            "accept": "application/json",
            "content-type": "application/json",
            "if-match": "" }

        r1 = self.cp.base_client.call_api(
            resource_path=resource_path,
            method=method,
            query_params=query_params,
            path_params=path_params,
            header_params=header_params)
        print( r1.message )
