'''
# `ionoscloud_autoscaling_group`

Refer to the Terraform Registry for docs: [`ionoscloud_autoscaling_group`](https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class AutoscalingGroup(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroup",
):
    '''Represents a {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group ionoscloud_autoscaling_group}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        datacenter_id: builtins.str,
        location: builtins.str,
        max_replica_count: jsii.Number,
        min_replica_count: jsii.Number,
        name: builtins.str,
        policy: typing.Union["AutoscalingGroupPolicy", typing.Dict[builtins.str, typing.Any]],
        replica_configuration: typing.Union["AutoscalingGroupReplicaConfiguration", typing.Dict[builtins.str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["AutoscalingGroupTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group ionoscloud_autoscaling_group} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datacenter_id: Unique identifier for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        :param location: Location of the data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#location AutoscalingGroup#location}
        :param max_replica_count: The maximum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        :param min_replica_count: The minimum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        :param name: User-defined name for the Autoscaling Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param policy: policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        :param replica_configuration: replica_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#id AutoscalingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3146dd62880db8c4a4a679ae36d31172810f23595b23353b8018fae683b4d75)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = AutoscalingGroupConfig(
            datacenter_id=datacenter_id,
            location=location,
            max_replica_count=max_replica_count,
            min_replica_count=min_replica_count,
            name=name,
            policy=policy,
            replica_configuration=replica_configuration,
            id=id,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a AutoscalingGroup resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AutoscalingGroup to import.
        :param import_from_id: The id of the existing AutoscalingGroup that should be imported. Refer to the {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AutoscalingGroup to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e086ea468bafd4c868fa25a191755facf3c01266c1ff7a5bb47db0a613324ca)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putPolicy")
    def put_policy(
        self,
        *,
        metric: builtins.str,
        scale_in_action: typing.Union["AutoscalingGroupPolicyScaleInAction", typing.Dict[builtins.str, typing.Any]],
        scale_in_threshold: jsii.Number,
        scale_out_action: typing.Union["AutoscalingGroupPolicyScaleOutAction", typing.Dict[builtins.str, typing.Any]],
        scale_out_threshold: jsii.Number,
        unit: builtins.str,
        range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        :param scale_in_action: scale_in_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        :param scale_in_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        :param scale_out_action: scale_out_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        :param scale_out_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        :param unit: Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        :param range: Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        value = AutoscalingGroupPolicy(
            metric=metric,
            scale_in_action=scale_in_action,
            scale_in_threshold=scale_in_threshold,
            scale_out_action=scale_out_action,
            scale_out_threshold=scale_out_threshold,
            unit=unit,
            range=range,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicy", [value]))

    @jsii.member(jsii_name="putReplicaConfiguration")
    def put_replica_configuration(
        self,
        *,
        availability_zone: builtins.str,
        cores: jsii.Number,
        ram: jsii.Number,
        cpu_family: typing.Optional[builtins.str] = None,
        nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param availability_zone: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        :param cores: The total number of cores for the VMs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        :param ram: The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        :param cpu_family: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        :param nic: nic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        :param volume: volume block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        value = AutoscalingGroupReplicaConfiguration(
            availability_zone=availability_zone,
            cores=cores,
            ram=ram,
            cpu_family=cpu_family,
            nic=nic,
            volume=volume,
        )

        return typing.cast(None, jsii.invoke(self, "putReplicaConfiguration", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#create AutoscalingGroup#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#default AutoscalingGroup#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#update AutoscalingGroup#update}.
        '''
        value = AutoscalingGroupTimeouts(
            create=create, default=default, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="policy")
    def policy(self) -> "AutoscalingGroupPolicyOutputReference":
        return typing.cast("AutoscalingGroupPolicyOutputReference", jsii.get(self, "policy"))

    @builtins.property
    @jsii.member(jsii_name="replicaConfiguration")
    def replica_configuration(
        self,
    ) -> "AutoscalingGroupReplicaConfigurationOutputReference":
        return typing.cast("AutoscalingGroupReplicaConfigurationOutputReference", jsii.get(self, "replicaConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "AutoscalingGroupTimeoutsOutputReference":
        return typing.cast("AutoscalingGroupTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="datacenterIdInput")
    def datacenter_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datacenterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="locationInput")
    def location_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "locationInput"))

    @builtins.property
    @jsii.member(jsii_name="maxReplicaCountInput")
    def max_replica_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicaCountInput"))

    @builtins.property
    @jsii.member(jsii_name="minReplicaCountInput")
    def min_replica_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minReplicaCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="policyInput")
    def policy_input(self) -> typing.Optional["AutoscalingGroupPolicy"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicy"], jsii.get(self, "policyInput"))

    @builtins.property
    @jsii.member(jsii_name="replicaConfigurationInput")
    def replica_configuration_input(
        self,
    ) -> typing.Optional["AutoscalingGroupReplicaConfiguration"]:
        return typing.cast(typing.Optional["AutoscalingGroupReplicaConfiguration"], jsii.get(self, "replicaConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AutoscalingGroupTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "AutoscalingGroupTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="datacenterId")
    def datacenter_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datacenterId"))

    @datacenter_id.setter
    def datacenter_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa64c750b5399ce01da6d4e11088ee4c48367961ecf1c44f2ee899a04a021b0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datacenterId", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0e3648c651a76707b9cd8410b25e85cc93402e8bdbe2fe2fd1bac10b1541429)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="location")
    def location(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "location"))

    @location.setter
    def location(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33627bbb96f63f0a19f6b4227fe8e98eb628acf7d6a5d6d5b58402e2e6e7dd28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "location", value)

    @builtins.property
    @jsii.member(jsii_name="maxReplicaCount")
    def max_replica_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicaCount"))

    @max_replica_count.setter
    def max_replica_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13fac770d256340aac888c3ece63afaf41f65d6645126008b33dd5b5ca9532ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxReplicaCount", value)

    @builtins.property
    @jsii.member(jsii_name="minReplicaCount")
    def min_replica_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minReplicaCount"))

    @min_replica_count.setter
    def min_replica_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__14d0b42b145f0bdecd33b6a5f6f29c297e8586a933bda594d5a1926807677d46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minReplicaCount", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5eec38da3536bf995579a222f399ce03f33ff418f4e09671c17c535e2c8d6bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "datacenter_id": "datacenterId",
        "location": "location",
        "max_replica_count": "maxReplicaCount",
        "min_replica_count": "minReplicaCount",
        "name": "name",
        "policy": "policy",
        "replica_configuration": "replicaConfiguration",
        "id": "id",
        "timeouts": "timeouts",
    },
)
class AutoscalingGroupConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        datacenter_id: builtins.str,
        location: builtins.str,
        max_replica_count: jsii.Number,
        min_replica_count: jsii.Number,
        name: builtins.str,
        policy: typing.Union["AutoscalingGroupPolicy", typing.Dict[builtins.str, typing.Any]],
        replica_configuration: typing.Union["AutoscalingGroupReplicaConfiguration", typing.Dict[builtins.str, typing.Any]],
        id: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["AutoscalingGroupTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param datacenter_id: Unique identifier for the resource. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        :param location: Location of the data center. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#location AutoscalingGroup#location}
        :param max_replica_count: The maximum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        :param min_replica_count: The minimum value for the number of replicas on a VM Auto Scaling Group. Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        :param name: User-defined name for the Autoscaling Group. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param policy: policy block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        :param replica_configuration: replica_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#id AutoscalingGroup#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(policy, dict):
            policy = AutoscalingGroupPolicy(**policy)
        if isinstance(replica_configuration, dict):
            replica_configuration = AutoscalingGroupReplicaConfiguration(**replica_configuration)
        if isinstance(timeouts, dict):
            timeouts = AutoscalingGroupTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58053b66870c47f3bc0ab5e617378b61c4bb34d67bb04bc14365e28392ae1fa3)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument datacenter_id", value=datacenter_id, expected_type=type_hints["datacenter_id"])
            check_type(argname="argument location", value=location, expected_type=type_hints["location"])
            check_type(argname="argument max_replica_count", value=max_replica_count, expected_type=type_hints["max_replica_count"])
            check_type(argname="argument min_replica_count", value=min_replica_count, expected_type=type_hints["min_replica_count"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument replica_configuration", value=replica_configuration, expected_type=type_hints["replica_configuration"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datacenter_id": datacenter_id,
            "location": location,
            "max_replica_count": max_replica_count,
            "min_replica_count": min_replica_count,
            "name": name,
            "policy": policy,
            "replica_configuration": replica_configuration,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if id is not None:
            self._values["id"] = id
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def datacenter_id(self) -> builtins.str:
        '''Unique identifier for the resource.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#datacenter_id AutoscalingGroup#datacenter_id}
        '''
        result = self._values.get("datacenter_id")
        assert result is not None, "Required property 'datacenter_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def location(self) -> builtins.str:
        '''Location of the data center.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#location AutoscalingGroup#location}
        '''
        result = self._values.get("location")
        assert result is not None, "Required property 'location' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_replica_count(self) -> jsii.Number:
        '''The maximum value for the number of replicas on a VM Auto Scaling Group.

        Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#max_replica_count AutoscalingGroup#max_replica_count}
        '''
        result = self._values.get("max_replica_count")
        assert result is not None, "Required property 'max_replica_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_replica_count(self) -> jsii.Number:
        '''The minimum value for the number of replicas on a VM Auto Scaling Group.

        Must be >= 0 and <= 200. Will be enforced for both automatic and manual changes

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#min_replica_count AutoscalingGroup#min_replica_count}
        '''
        result = self._values.get("min_replica_count")
        assert result is not None, "Required property 'min_replica_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name for the Autoscaling Group.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def policy(self) -> "AutoscalingGroupPolicy":
        '''policy block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#policy AutoscalingGroup#policy}
        '''
        result = self._values.get("policy")
        assert result is not None, "Required property 'policy' is missing"
        return typing.cast("AutoscalingGroupPolicy", result)

    @builtins.property
    def replica_configuration(self) -> "AutoscalingGroupReplicaConfiguration":
        '''replica_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#replica_configuration AutoscalingGroup#replica_configuration}
        '''
        result = self._values.get("replica_configuration")
        assert result is not None, "Required property 'replica_configuration' is missing"
        return typing.cast("AutoscalingGroupReplicaConfiguration", result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#id AutoscalingGroup#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["AutoscalingGroupTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#timeouts AutoscalingGroup#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["AutoscalingGroupTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "metric": "metric",
        "scale_in_action": "scaleInAction",
        "scale_in_threshold": "scaleInThreshold",
        "scale_out_action": "scaleOutAction",
        "scale_out_threshold": "scaleOutThreshold",
        "unit": "unit",
        "range": "range",
    },
)
class AutoscalingGroupPolicy:
    def __init__(
        self,
        *,
        metric: builtins.str,
        scale_in_action: typing.Union["AutoscalingGroupPolicyScaleInAction", typing.Dict[builtins.str, typing.Any]],
        scale_in_threshold: jsii.Number,
        scale_out_action: typing.Union["AutoscalingGroupPolicyScaleOutAction", typing.Dict[builtins.str, typing.Any]],
        scale_out_threshold: jsii.Number,
        unit: builtins.str,
        range: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric: The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        :param scale_in_action: scale_in_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        :param scale_in_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        :param scale_out_action: scale_out_action block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        :param scale_out_threshold: The upper threshold for the value of the 'metric'. Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        :param unit: Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        :param range: Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        if isinstance(scale_in_action, dict):
            scale_in_action = AutoscalingGroupPolicyScaleInAction(**scale_in_action)
        if isinstance(scale_out_action, dict):
            scale_out_action = AutoscalingGroupPolicyScaleOutAction(**scale_out_action)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68e702088158ad817c233bb2fdb4a934ac0d83af64565b75932648127031421f)
            check_type(argname="argument metric", value=metric, expected_type=type_hints["metric"])
            check_type(argname="argument scale_in_action", value=scale_in_action, expected_type=type_hints["scale_in_action"])
            check_type(argname="argument scale_in_threshold", value=scale_in_threshold, expected_type=type_hints["scale_in_threshold"])
            check_type(argname="argument scale_out_action", value=scale_out_action, expected_type=type_hints["scale_out_action"])
            check_type(argname="argument scale_out_threshold", value=scale_out_threshold, expected_type=type_hints["scale_out_threshold"])
            check_type(argname="argument unit", value=unit, expected_type=type_hints["unit"])
            check_type(argname="argument range", value=range, expected_type=type_hints["range"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric": metric,
            "scale_in_action": scale_in_action,
            "scale_in_threshold": scale_in_threshold,
            "scale_out_action": scale_out_action,
            "scale_out_threshold": scale_out_threshold,
            "unit": unit,
        }
        if range is not None:
            self._values["range"] = range

    @builtins.property
    def metric(self) -> builtins.str:
        '''The Metric that should trigger the scaling actions. Metric values are checked at fixed intervals.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#metric AutoscalingGroup#metric}
        '''
        result = self._values.get("metric")
        assert result is not None, "Required property 'metric' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scale_in_action(self) -> "AutoscalingGroupPolicyScaleInAction":
        '''scale_in_action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_action AutoscalingGroup#scale_in_action}
        '''
        result = self._values.get("scale_in_action")
        assert result is not None, "Required property 'scale_in_action' is missing"
        return typing.cast("AutoscalingGroupPolicyScaleInAction", result)

    @builtins.property
    def scale_in_threshold(self) -> jsii.Number:
        '''The upper threshold for the value of the 'metric'.

        Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scale_out_action' property. The value must have a lower minimum delta to the 'scale_in_threshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_in_threshold AutoscalingGroup#scale_in_threshold}
        '''
        result = self._values.get("scale_in_threshold")
        assert result is not None, "Required property 'scale_in_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def scale_out_action(self) -> "AutoscalingGroupPolicyScaleOutAction":
        '''scale_out_action block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_action AutoscalingGroup#scale_out_action}
        '''
        result = self._values.get("scale_out_action")
        assert result is not None, "Required property 'scale_out_action' is missing"
        return typing.cast("AutoscalingGroupPolicyScaleOutAction", result)

    @builtins.property
    def scale_out_threshold(self) -> jsii.Number:
        '''The upper threshold for the value of the 'metric'.

        Used with the 'greater than' (>) operator. A scale-out action is triggered when this value is exceeded, specified by the 'scaleOutAction' property. The value must have a lower minimum delta to the 'scaleInThreshold', depending on the metric, to avoid competing for actions simultaneously. If 'properties.policy.unit=TOTAL', a value >= 40 must be chosen.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#scale_out_threshold AutoscalingGroup#scale_out_threshold}
        '''
        result = self._values.get("scale_out_threshold")
        assert result is not None, "Required property 'scale_out_threshold' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def unit(self) -> builtins.str:
        '''Units of the applied Metric. Possible values are: PER_HOUR, PER_MINUTE, PER_SECOND, TOTAL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#unit AutoscalingGroup#unit}
        '''
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def range(self) -> typing.Optional[builtins.str]:
        '''Specifies the time range for which the samples are to be aggregated. Must be >= 2 minutes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#range AutoscalingGroup#range}
        '''
        result = self._values.get("range")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b7f459aba3a8708621521fed4b6fdbc83c8c574108f722c3e9b6b267d9a79de)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putScaleInAction")
    def put_scale_in_action(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        cooldown_period: typing.Optional[builtins.str] = None,
        termination_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param delete_volumes: If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted. When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        :param termination_policy_type: The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas. The default termination policy is 'OLDEST_SERVER_FIRST'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        value = AutoscalingGroupPolicyScaleInAction(
            amount=amount,
            amount_type=amount_type,
            delete_volumes=delete_volumes,
            cooldown_period=cooldown_period,
            termination_policy_type=termination_policy_type,
        )

        return typing.cast(None, jsii.invoke(self, "putScaleInAction", [value]))

    @jsii.member(jsii_name="putScaleOutAction")
    def put_scale_out_action(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        cooldown_period: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        value = AutoscalingGroupPolicyScaleOutAction(
            amount=amount, amount_type=amount_type, cooldown_period=cooldown_period
        )

        return typing.cast(None, jsii.invoke(self, "putScaleOutAction", [value]))

    @jsii.member(jsii_name="resetRange")
    def reset_range(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRange", []))

    @builtins.property
    @jsii.member(jsii_name="scaleInAction")
    def scale_in_action(self) -> "AutoscalingGroupPolicyScaleInActionOutputReference":
        return typing.cast("AutoscalingGroupPolicyScaleInActionOutputReference", jsii.get(self, "scaleInAction"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutAction")
    def scale_out_action(self) -> "AutoscalingGroupPolicyScaleOutActionOutputReference":
        return typing.cast("AutoscalingGroupPolicyScaleOutActionOutputReference", jsii.get(self, "scaleOutAction"))

    @builtins.property
    @jsii.member(jsii_name="metricInput")
    def metric_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricInput"))

    @builtins.property
    @jsii.member(jsii_name="rangeInput")
    def range_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rangeInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleInActionInput")
    def scale_in_action_input(
        self,
    ) -> typing.Optional["AutoscalingGroupPolicyScaleInAction"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicyScaleInAction"], jsii.get(self, "scaleInActionInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleInThresholdInput")
    def scale_in_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scaleInThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutActionInput")
    def scale_out_action_input(
        self,
    ) -> typing.Optional["AutoscalingGroupPolicyScaleOutAction"]:
        return typing.cast(typing.Optional["AutoscalingGroupPolicyScaleOutAction"], jsii.get(self, "scaleOutActionInput"))

    @builtins.property
    @jsii.member(jsii_name="scaleOutThresholdInput")
    def scale_out_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scaleOutThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitInput")
    def unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitInput"))

    @builtins.property
    @jsii.member(jsii_name="metric")
    def metric(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metric"))

    @metric.setter
    def metric(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2764da5d65fc915f2a7f0f315e2b9c3725b0991e79391c2ec3b17b384419d949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metric", value)

    @builtins.property
    @jsii.member(jsii_name="range")
    def range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "range"))

    @range.setter
    def range(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa5f2570afc38dd5c1a2eb3f43b50274b24280761b7a3ac5f088f4baccb726b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "range", value)

    @builtins.property
    @jsii.member(jsii_name="scaleInThreshold")
    def scale_in_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scaleInThreshold"))

    @scale_in_threshold.setter
    def scale_in_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6ae6f86524c15798e2b2be53d7412b883d806d85cb08f0b741fb762002c97cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleInThreshold", value)

    @builtins.property
    @jsii.member(jsii_name="scaleOutThreshold")
    def scale_out_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scaleOutThreshold"))

    @scale_out_threshold.setter
    def scale_out_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2df5e1d6d313726a46de06118313eb60eb081ffaf64af4424c4c4dae38a0db25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scaleOutThreshold", value)

    @builtins.property
    @jsii.member(jsii_name="unit")
    def unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "unit"))

    @unit.setter
    def unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd42ad0b6666b52acf4ec9a56d2b7a56b046d162627727f4e01bf8611fbeec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unit", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicy]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[AutoscalingGroupPolicy]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fc8e1835a175893e3aa46a6a9d35b813890d9ba43e8449ce5b5ba63c1aba574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleInAction",
    jsii_struct_bases=[],
    name_mapping={
        "amount": "amount",
        "amount_type": "amountType",
        "delete_volumes": "deleteVolumes",
        "cooldown_period": "cooldownPeriod",
        "termination_policy_type": "terminationPolicyType",
    },
)
class AutoscalingGroupPolicyScaleInAction:
    def __init__(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        cooldown_period: typing.Optional[builtins.str] = None,
        termination_policy_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param delete_volumes: If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted. When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        :param termination_policy_type: The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas. The default termination policy is 'OLDEST_SERVER_FIRST'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df38e3cdf7b235f5f6fe179e59631a45c22f33edab46beae2d4c68ce6235f891)
            check_type(argname="argument amount", value=amount, expected_type=type_hints["amount"])
            check_type(argname="argument amount_type", value=amount_type, expected_type=type_hints["amount_type"])
            check_type(argname="argument delete_volumes", value=delete_volumes, expected_type=type_hints["delete_volumes"])
            check_type(argname="argument cooldown_period", value=cooldown_period, expected_type=type_hints["cooldown_period"])
            check_type(argname="argument termination_policy_type", value=termination_policy_type, expected_type=type_hints["termination_policy_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "amount": amount,
            "amount_type": amount_type,
            "delete_volumes": delete_volumes,
        }
        if cooldown_period is not None:
            self._values["cooldown_period"] = cooldown_period
        if termination_policy_type is not None:
            self._values["termination_policy_type"] = termination_policy_type

    @builtins.property
    def amount(self) -> jsii.Number:
        '''When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are removed.

        The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always removed. Note that for 'SCALE_IN' operations, volumes are not deleted after the server is deleted.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        '''
        result = self._values.get("amount")
        assert result is not None, "Required property 'amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def amount_type(self) -> builtins.str:
        '''The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        '''
        result = self._values.get("amount_type")
        assert result is not None, "Required property 'amount_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delete_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''If set to 'true', when deleting an replica during scale in, any attached volume will also be deleted.

        When set to 'false', all volumes remain in the datacenter and must be deleted manually. Note that every scale-out creates new volumes. When they are not deleted, they will eventually use all of your contracts resource limits. At this point, scaling out would not be possible anymore.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete_volumes AutoscalingGroup#delete_volumes}
        '''
        result = self._values.get("delete_volumes")
        assert result is not None, "Required property 'delete_volumes' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def cooldown_period(self) -> typing.Optional[builtins.str]:
        '''The minimum time that elapses after the start of this scaling action until the following scaling action is started.

        While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        result = self._values.get("cooldown_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def termination_policy_type(self) -> typing.Optional[builtins.str]:
        '''The type of termination policy for the VM Auto Scaling Group to follow a specific pattern for scaling-in replicas.

        The default termination policy is 'OLDEST_SERVER_FIRST'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#termination_policy_type AutoscalingGroup#termination_policy_type}
        '''
        result = self._values.get("termination_policy_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicyScaleInAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyScaleInActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleInActionOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ea303df8e2d25f599cbf66afd9f6bfe4268a8fbe0494ffb893c7fa19160fb62)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCooldownPeriod")
    def reset_cooldown_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldownPeriod", []))

    @jsii.member(jsii_name="resetTerminationPolicyType")
    def reset_termination_policy_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationPolicyType", []))

    @builtins.property
    @jsii.member(jsii_name="amountInput")
    def amount_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "amountInput"))

    @builtins.property
    @jsii.member(jsii_name="amountTypeInput")
    def amount_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amountTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriodInput")
    def cooldown_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cooldownPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteVolumesInput")
    def delete_volumes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deleteVolumesInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationPolicyTypeInput")
    def termination_policy_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "terminationPolicyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="amount")
    def amount(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "amount"))

    @amount.setter
    def amount(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204cfc21e156ebe762e24140c5b9b5b53909fdb1c1504d62b7434077e6403cfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amount", value)

    @builtins.property
    @jsii.member(jsii_name="amountType")
    def amount_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amountType"))

    @amount_type.setter
    def amount_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a981dac662cf18dc8dd7ee59ecb8df8d1001f0779f1d0c741940cc0f06e05a89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amountType", value)

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriod")
    def cooldown_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cooldownPeriod"))

    @cooldown_period.setter
    def cooldown_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__536be0162f40286b13583f2bdff4f1d3342e75965e5abdff6113eb7a33c1bfc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldownPeriod", value)

    @builtins.property
    @jsii.member(jsii_name="deleteVolumes")
    def delete_volumes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "deleteVolumes"))

    @delete_volumes.setter
    def delete_volumes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17c3730c0315324813b2ab8c5b73827c72b8bc5e340b1996a216ab5471d01ead)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteVolumes", value)

    @builtins.property
    @jsii.member(jsii_name="terminationPolicyType")
    def termination_policy_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "terminationPolicyType"))

    @termination_policy_type.setter
    def termination_policy_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a450bf2c72d16cb4f5d97e1e020c1f26b63f43573a0d4c42cc7ff9a9d80c6219)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationPolicyType", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicyScaleInAction]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicyScaleInAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupPolicyScaleInAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555c5ec7b1809bb4d55c43985370defd1502475f8f112eab09150d6d2fbdbd70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleOutAction",
    jsii_struct_bases=[],
    name_mapping={
        "amount": "amount",
        "amount_type": "amountType",
        "cooldown_period": "cooldownPeriod",
    },
)
class AutoscalingGroupPolicyScaleOutAction:
    def __init__(
        self,
        *,
        amount: jsii.Number,
        amount_type: builtins.str,
        cooldown_period: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param amount: When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added. The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        :param amount_type: The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        :param cooldown_period: The minimum time that elapses after the start of this scaling action until the following scaling action is started. While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16787c31ff992b6598a275a4db90ce816824c4ad8fccc7daf7512172120c4a7d)
            check_type(argname="argument amount", value=amount, expected_type=type_hints["amount"])
            check_type(argname="argument amount_type", value=amount_type, expected_type=type_hints["amount_type"])
            check_type(argname="argument cooldown_period", value=cooldown_period, expected_type=type_hints["cooldown_period"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "amount": amount,
            "amount_type": amount_type,
        }
        if cooldown_period is not None:
            self._values["cooldown_period"] = cooldown_period

    @builtins.property
    def amount(self) -> jsii.Number:
        '''When 'amountType=ABSOLUTE' specifies the absolute number of VMs that are added.

        The value must be between 1 to 10. 'amountType=PERCENTAGE' specifies the percentage value that is applied to the current number of replicas of the VM Auto Scaling Group. The value must be between 1 to 200. At least one VM is always added or removed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount AutoscalingGroup#amount}
        '''
        result = self._values.get("amount")
        assert result is not None, "Required property 'amount' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def amount_type(self) -> builtins.str:
        '''The type for the given amount. Possible values are: [ABSOLUTE, PERCENTAGE].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#amount_type AutoscalingGroup#amount_type}
        '''
        result = self._values.get("amount_type")
        assert result is not None, "Required property 'amount_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cooldown_period(self) -> typing.Optional[builtins.str]:
        '''The minimum time that elapses after the start of this scaling action until the following scaling action is started.

        While a scaling action is in progress, no second action is initiated for the same VM Auto Scaling Group. Instead, the metric is re-evaluated after the current scaling action completes (either successfully or with errors). This is currently validated with a minimum value of 2 minutes and a maximum of 24 hours. The default value is 5 minutes if not specified.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cooldown_period AutoscalingGroup#cooldown_period}
        '''
        result = self._values.get("cooldown_period")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupPolicyScaleOutAction(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupPolicyScaleOutActionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupPolicyScaleOutActionOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__165b096930701475659b425b1c1d1b799c5e7d92a4f7696b0117b0a8d44a4e02)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCooldownPeriod")
    def reset_cooldown_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldownPeriod", []))

    @builtins.property
    @jsii.member(jsii_name="amountInput")
    def amount_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "amountInput"))

    @builtins.property
    @jsii.member(jsii_name="amountTypeInput")
    def amount_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "amountTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriodInput")
    def cooldown_period_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cooldownPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="amount")
    def amount(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "amount"))

    @amount.setter
    def amount(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9d5b374cc13b0ad43c9c58ec95707bfb697ea13f24e2616526adca15048e618)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amount", value)

    @builtins.property
    @jsii.member(jsii_name="amountType")
    def amount_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "amountType"))

    @amount_type.setter
    def amount_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ceb1e010f2840fd631a64e69ba9bdcad0f6f88bf01f8283d9bb0f3c2285c23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "amountType", value)

    @builtins.property
    @jsii.member(jsii_name="cooldownPeriod")
    def cooldown_period(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cooldownPeriod"))

    @cooldown_period.setter
    def cooldown_period(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ae6465cbf87029321d558b10af2eeca7a6d03f88ab82ab786f8fcd660e6c0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldownPeriod", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupPolicyScaleOutAction]:
        return typing.cast(typing.Optional[AutoscalingGroupPolicyScaleOutAction], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupPolicyScaleOutAction],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0cca00adac567f779cbb4c62cc55ebdbb7285f2288cabefdea29c0b3565e072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "availability_zone": "availabilityZone",
        "cores": "cores",
        "ram": "ram",
        "cpu_family": "cpuFamily",
        "nic": "nic",
        "volume": "volume",
    },
)
class AutoscalingGroupReplicaConfiguration:
    def __init__(
        self,
        *,
        availability_zone: builtins.str,
        cores: jsii.Number,
        ram: jsii.Number,
        cpu_family: typing.Optional[builtins.str] = None,
        nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationNic", typing.Dict[builtins.str, typing.Any]]]]] = None,
        volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param availability_zone: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        :param cores: The total number of cores for the VMs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        :param ram: The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        :param cpu_family: The zone where the VMs are created using this configuration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        :param nic: nic block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        :param volume: volume block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9753c8e0b92272664f4f8fa7334c36abeafa315c55a3a421d6b61d3d28fc2a)
            check_type(argname="argument availability_zone", value=availability_zone, expected_type=type_hints["availability_zone"])
            check_type(argname="argument cores", value=cores, expected_type=type_hints["cores"])
            check_type(argname="argument ram", value=ram, expected_type=type_hints["ram"])
            check_type(argname="argument cpu_family", value=cpu_family, expected_type=type_hints["cpu_family"])
            check_type(argname="argument nic", value=nic, expected_type=type_hints["nic"])
            check_type(argname="argument volume", value=volume, expected_type=type_hints["volume"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "availability_zone": availability_zone,
            "cores": cores,
            "ram": ram,
        }
        if cpu_family is not None:
            self._values["cpu_family"] = cpu_family
        if nic is not None:
            self._values["nic"] = nic
        if volume is not None:
            self._values["volume"] = volume

    @builtins.property
    def availability_zone(self) -> builtins.str:
        '''The zone where the VMs are created using this configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#availability_zone AutoscalingGroup#availability_zone}
        '''
        result = self._values.get("availability_zone")
        assert result is not None, "Required property 'availability_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cores(self) -> jsii.Number:
        '''The total number of cores for the VMs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cores AutoscalingGroup#cores}
        '''
        result = self._values.get("cores")
        assert result is not None, "Required property 'cores' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def ram(self) -> jsii.Number:
        '''The amount of memory for the VMs in MB, e.g. 2048. Size must be specified in multiples of 256 MB with a minimum of 256 MB; however, if you set ramHotPlug to TRUE then you must use a minimum of 1024 MB. If you set the RAM size more than 240GB, then ramHotPlug will be set to FALSE and can not be set to TRUE unless RAM size not set to less than 240GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#ram AutoscalingGroup#ram}
        '''
        result = self._values.get("ram")
        assert result is not None, "Required property 'ram' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cpu_family(self) -> typing.Optional[builtins.str]:
        '''The zone where the VMs are created using this configuration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#cpu_family AutoscalingGroup#cpu_family}
        '''
        result = self._values.get("cpu_family")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nic(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNic"]]]:
        '''nic block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#nic AutoscalingGroup#nic}
        '''
        result = self._values.get("nic")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationNic"]]], result)

    @builtins.property
    def volume(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]]:
        '''volume block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#volume AutoscalingGroup#volume}
        '''
        result = self._values.get("volume")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNic",
    jsii_struct_bases=[],
    name_mapping={"lan": "lan", "name": "name", "dhcp": "dhcp"},
)
class AutoscalingGroupReplicaConfigurationNic:
    def __init__(
        self,
        *,
        lan: jsii.Number,
        name: builtins.str,
        dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param lan: Lan ID for this replica Nic. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#lan AutoscalingGroup#lan}
        :param name: Name for this replica NIC. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param dhcp: Dhcp flag for this replica Nic. This is an optional attribute with default value of 'true' if not given in the request payload or given as null. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#dhcp AutoscalingGroup#dhcp}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7db78f4556b0eba4b01ccef6c2598a45961bb34cbe79a3e74e1752233cc5380)
            check_type(argname="argument lan", value=lan, expected_type=type_hints["lan"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument dhcp", value=dhcp, expected_type=type_hints["dhcp"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "lan": lan,
            "name": name,
        }
        if dhcp is not None:
            self._values["dhcp"] = dhcp

    @builtins.property
    def lan(self) -> jsii.Number:
        '''Lan ID for this replica Nic.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#lan AutoscalingGroup#lan}
        '''
        result = self._values.get("lan")
        assert result is not None, "Required property 'lan' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name for this replica NIC.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dhcp(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Dhcp flag for this replica Nic.

        This is an optional attribute with default value of 'true' if not given in the request payload or given as null.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#dhcp AutoscalingGroup#dhcp}
        '''
        result = self._values.get("dhcp")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationNic(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationNicList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebf3052063fd3ab488ef7e4e2f592d47d55eed716301ace563fe9ae7dd07af33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationNicOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4bf77b8c96d5a8cdb1de14fc706dcaf1ff03cbecd77b5a331ecc6f44786cd7e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationNicOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d827d67c0b4d0a288bf9d5b489a9b0acb439c094598de6421605a82259156d8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adbf0a00215fc01f03b86f0782a02e23188e89eabd9d6c3bafa10474e093505a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__694fb45fb5662d8a15068c3761890f6b6dc9cf4efd18cf07369f0989b4195490)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080c71c5aa2f339511c040a723332d3070de7124e4050607adbf983c2226804b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AutoscalingGroupReplicaConfigurationNicOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationNicOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c1056ab7fcde8218a157992345e8eea145cb01708657524254c7d191161d2d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDhcp")
    def reset_dhcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDhcp", []))

    @builtins.property
    @jsii.member(jsii_name="dhcpInput")
    def dhcp_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "dhcpInput"))

    @builtins.property
    @jsii.member(jsii_name="lanInput")
    def lan_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lanInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="dhcp")
    def dhcp(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "dhcp"))

    @dhcp.setter
    def dhcp(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3412c9bddf61b5e6eb31daa6abe1d1edfacf59753ea5084489d5efc45c10a7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dhcp", value)

    @builtins.property
    @jsii.member(jsii_name="lan")
    def lan(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lan"))

    @lan.setter
    def lan(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb7e090377b2bb156aeaa591bedef2d760b7b7c8496820d54bbd1c137b6a8341)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lan", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f051c5aea2f72a66830f4f96b577ff4cbb61f62fe6033852a24b8c652b1fe90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__966666570e4b5b7856e18b615f56436d2ccdfb63090907b4dfc4377a01a837aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AutoscalingGroupReplicaConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c98eb701e487a04d289694169f4f1462a1c514bf9f3fe992d38f214f308a046b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putNic")
    def put_nic(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198b6b23b6c02d366401147df266493eb117c9fab0111a9b36b4d435f8ce185a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNic", [value]))

    @jsii.member(jsii_name="putVolume")
    def put_volume(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AutoscalingGroupReplicaConfigurationVolume", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55dcb3fe0650b211894bf7c976ea8efc9db19a70106ef566b10168a2a4a80a1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVolume", [value]))

    @jsii.member(jsii_name="resetCpuFamily")
    def reset_cpu_family(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuFamily", []))

    @jsii.member(jsii_name="resetNic")
    def reset_nic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNic", []))

    @jsii.member(jsii_name="resetVolume")
    def reset_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolume", []))

    @builtins.property
    @jsii.member(jsii_name="nic")
    def nic(self) -> AutoscalingGroupReplicaConfigurationNicList:
        return typing.cast(AutoscalingGroupReplicaConfigurationNicList, jsii.get(self, "nic"))

    @builtins.property
    @jsii.member(jsii_name="volume")
    def volume(self) -> "AutoscalingGroupReplicaConfigurationVolumeList":
        return typing.cast("AutoscalingGroupReplicaConfigurationVolumeList", jsii.get(self, "volume"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="coresInput")
    def cores_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "coresInput"))

    @builtins.property
    @jsii.member(jsii_name="cpuFamilyInput")
    def cpu_family_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuFamilyInput"))

    @builtins.property
    @jsii.member(jsii_name="nicInput")
    def nic_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]], jsii.get(self, "nicInput"))

    @builtins.property
    @jsii.member(jsii_name="ramInput")
    def ram_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ramInput"))

    @builtins.property
    @jsii.member(jsii_name="volumeInput")
    def volume_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AutoscalingGroupReplicaConfigurationVolume"]]], jsii.get(self, "volumeInput"))

    @builtins.property
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ecd5f002c4fb199acb7a64fc64fd7b7eed894c6b4f54f65ff321f07c3505655)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "availabilityZone", value)

    @builtins.property
    @jsii.member(jsii_name="cores")
    def cores(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cores"))

    @cores.setter
    def cores(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ec8e06e2a6463598d1d2f9f050614f917f79b0aa958e6305a38f8091f872a2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cores", value)

    @builtins.property
    @jsii.member(jsii_name="cpuFamily")
    def cpu_family(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuFamily"))

    @cpu_family.setter
    def cpu_family(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__236909ef7417a78ba6fe76c8eb36c9c11ad6ee29e8f7f1d4c7c2527a29c81dcc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cpuFamily", value)

    @builtins.property
    @jsii.member(jsii_name="ram")
    def ram(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ram"))

    @ram.setter
    def ram(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3e42aaed6cfdbc4a7624f2eb9264283c30b57336853ecd053dfa50d4592bdde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ram", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[AutoscalingGroupReplicaConfiguration]:
        return typing.cast(typing.Optional[AutoscalingGroupReplicaConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[AutoscalingGroupReplicaConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c68c26597a550e588bbd9e71cef00a66c4c5c442d4acfc82b7223d8229f5395)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolume",
    jsii_struct_bases=[],
    name_mapping={
        "boot_order": "bootOrder",
        "name": "name",
        "size": "size",
        "type": "type",
        "backup_unit_id": "backupUnitId",
        "bus": "bus",
        "image": "image",
        "image_alias": "imageAlias",
        "image_password": "imagePassword",
        "ssh_keys": "sshKeys",
        "user_data": "userData",
    },
)
class AutoscalingGroupReplicaConfigurationVolume:
    def __init__(
        self,
        *,
        boot_order: builtins.str,
        name: builtins.str,
        size: jsii.Number,
        type: builtins.str,
        backup_unit_id: typing.Optional[builtins.str] = None,
        bus: typing.Optional[builtins.str] = None,
        image: typing.Optional[builtins.str] = None,
        image_alias: typing.Optional[builtins.str] = None,
        image_password: typing.Optional[builtins.str] = None,
        ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param boot_order: Determines whether the volume will be used as a boot volume. Set to NONE, the volume will not be used as boot volume. Set to PRIMARY, the volume will be used as boot volume and set to AUTO will delegate the decision to the provisioning engine to decide whether to use the volume as boot volume. Notice that exactly one volume can be set to PRIMARY or all of them set to AUTO. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#boot_order AutoscalingGroup#boot_order}
        :param name: Name for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        :param size: User-defined size for this replica volume in GB. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#size AutoscalingGroup#size}
        :param type: Storage Type for this replica volume. Possible values: SSD, HDD, SSD_STANDARD or SSD_PREMIUM. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        :param backup_unit_id: The uuid of the Backup Unit that user has access to. The property is immutable and is only allowed to be set on a new volume creation. It is mandatory to provide either 'public image' or 'imageAlias' in conjunction with this property. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#backup_unit_id AutoscalingGroup#backup_unit_id}
        :param bus: The bus type of the volume. Default setting is 'VIRTIO'. The bus type 'IDE' is also supported. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#bus AutoscalingGroup#bus}
        :param image: The image installed on the disk. Currently, only the UUID of the image is supported. Note that either 'image' or 'imageAlias' must be specified, but not both. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image AutoscalingGroup#image}
        :param image_alias: The image installed on the volume. Must be an 'imageAlias' as specified via the images API. Note that one of 'image' or 'imageAlias' must be set, but not both. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image_alias AutoscalingGroup#image_alias}
        :param image_password: Image password for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image_password AutoscalingGroup#image_password}
        :param ssh_keys: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#ssh_keys AutoscalingGroup#ssh_keys}.
        :param user_data: User-data (Cloud Init) for this replica volume. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#user_data AutoscalingGroup#user_data}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f6f15e1974841b2872a9d8ddd17de311f008024ec20bffb1a82b7f01663eb61)
            check_type(argname="argument boot_order", value=boot_order, expected_type=type_hints["boot_order"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument backup_unit_id", value=backup_unit_id, expected_type=type_hints["backup_unit_id"])
            check_type(argname="argument bus", value=bus, expected_type=type_hints["bus"])
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument image_alias", value=image_alias, expected_type=type_hints["image_alias"])
            check_type(argname="argument image_password", value=image_password, expected_type=type_hints["image_password"])
            check_type(argname="argument ssh_keys", value=ssh_keys, expected_type=type_hints["ssh_keys"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "boot_order": boot_order,
            "name": name,
            "size": size,
            "type": type,
        }
        if backup_unit_id is not None:
            self._values["backup_unit_id"] = backup_unit_id
        if bus is not None:
            self._values["bus"] = bus
        if image is not None:
            self._values["image"] = image
        if image_alias is not None:
            self._values["image_alias"] = image_alias
        if image_password is not None:
            self._values["image_password"] = image_password
        if ssh_keys is not None:
            self._values["ssh_keys"] = ssh_keys
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def boot_order(self) -> builtins.str:
        '''Determines whether the volume will be used as a boot volume.

        Set to NONE, the volume will not be used as boot volume.
        Set to PRIMARY, the volume will be used as boot volume and set to AUTO will delegate the decision to the provisioning engine to decide whether to use the volume as boot volume.
        Notice that exactly one volume can be set to PRIMARY or all of them set to AUTO.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#boot_order AutoscalingGroup#boot_order}
        '''
        result = self._values.get("boot_order")
        assert result is not None, "Required property 'boot_order' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#name AutoscalingGroup#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size(self) -> jsii.Number:
        '''User-defined size for this replica volume in GB.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#size AutoscalingGroup#size}
        '''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Storage Type for this replica volume. Possible values: SSD, HDD, SSD_STANDARD or SSD_PREMIUM.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#type AutoscalingGroup#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backup_unit_id(self) -> typing.Optional[builtins.str]:
        '''The uuid of the Backup Unit that user has access to.

        The property is immutable and is only allowed to be set on a new volume creation. It is mandatory to provide either 'public image' or 'imageAlias' in conjunction with this property.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#backup_unit_id AutoscalingGroup#backup_unit_id}
        '''
        result = self._values.get("backup_unit_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def bus(self) -> typing.Optional[builtins.str]:
        '''The bus type of the volume. Default setting is 'VIRTIO'. The bus type 'IDE' is also supported.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#bus AutoscalingGroup#bus}
        '''
        result = self._values.get("bus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        '''The image installed on the disk.

        Currently, only the UUID of the image is supported. Note that either 'image' or 'imageAlias' must be specified, but not both.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image AutoscalingGroup#image}
        '''
        result = self._values.get("image")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_alias(self) -> typing.Optional[builtins.str]:
        '''The image installed on the volume.

        Must be an 'imageAlias' as specified via the images API. Note that one of 'image' or 'imageAlias' must be set, but not both.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image_alias AutoscalingGroup#image_alias}
        '''
        result = self._values.get("image_alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def image_password(self) -> typing.Optional[builtins.str]:
        '''Image password for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#image_password AutoscalingGroup#image_password}
        '''
        result = self._values.get("image_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ssh_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#ssh_keys AutoscalingGroup#ssh_keys}.'''
        result = self._values.get("ssh_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''User-data (Cloud Init) for this replica volume.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#user_data AutoscalingGroup#user_data}
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupReplicaConfigurationVolume(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupReplicaConfigurationVolumeList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolumeList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__991f24dea0804dbb901311fb3f27db77f4184d038526eb9832230701c28da5ae)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AutoscalingGroupReplicaConfigurationVolumeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80dd3d402ba9b006ff1392dd4099eeeaba3c0019078750d781e793ed7d80cc7c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AutoscalingGroupReplicaConfigurationVolumeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8814b4426559baa049e597e6499134643f94242bdbe7ca94b50667cf8dec0d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c4b574519d2ac8197c5b6756153523f66e740c1d0b251162385c53acce078f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__678677ebd665a33ae1f692dda8e7828e2da2812c72a6aacf0525f4a3559538e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__637ae6e6839bf25443b0f38165a5c07dc10703c879fb9c7b746c03b670090603)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class AutoscalingGroupReplicaConfigurationVolumeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupReplicaConfigurationVolumeOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71307a76483f2b83b0d65e5b204e07d5673267c84ffcaf69113dbb92678f2142)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetBackupUnitId")
    def reset_backup_unit_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupUnitId", []))

    @jsii.member(jsii_name="resetBus")
    def reset_bus(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBus", []))

    @jsii.member(jsii_name="resetImage")
    def reset_image(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImage", []))

    @jsii.member(jsii_name="resetImageAlias")
    def reset_image_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImageAlias", []))

    @jsii.member(jsii_name="resetImagePassword")
    def reset_image_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetImagePassword", []))

    @jsii.member(jsii_name="resetSshKeys")
    def reset_ssh_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSshKeys", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @builtins.property
    @jsii.member(jsii_name="backupUnitIdInput")
    def backup_unit_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backupUnitIdInput"))

    @builtins.property
    @jsii.member(jsii_name="bootOrderInput")
    def boot_order_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bootOrderInput"))

    @builtins.property
    @jsii.member(jsii_name="busInput")
    def bus_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "busInput"))

    @builtins.property
    @jsii.member(jsii_name="imageAliasInput")
    def image_alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageAliasInput"))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="imagePasswordInput")
    def image_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imagePasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sshKeysInput")
    def ssh_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="backupUnitId")
    def backup_unit_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backupUnitId"))

    @backup_unit_id.setter
    def backup_unit_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe4ebb5c2b34c15869f2a274dee54ffc22cc698a9f2842c043ef2f81455b98e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupUnitId", value)

    @builtins.property
    @jsii.member(jsii_name="bootOrder")
    def boot_order(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootOrder"))

    @boot_order.setter
    def boot_order(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c15afae5963ab5d9e7128954d25a634c8b3c2177e2d29fcb8d86d340c6a1584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootOrder", value)

    @builtins.property
    @jsii.member(jsii_name="bus")
    def bus(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bus"))

    @bus.setter
    def bus(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__219d3440216754d2e94e8821f2fc2f83e39667fef9c5857c9433212bcd5f52cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bus", value)

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0b9731f9c3928a51ff4ccdb665e43a5a902fe5384b38d1d6fb084a7ad07e2ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "image", value)

    @builtins.property
    @jsii.member(jsii_name="imageAlias")
    def image_alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageAlias"))

    @image_alias.setter
    def image_alias(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b84d56ab1bf338d9fef3b1c89dd50ccb8811468e81fb60da6eb182fff213718)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imageAlias", value)

    @builtins.property
    @jsii.member(jsii_name="imagePassword")
    def image_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imagePassword"))

    @image_password.setter
    def image_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6b372869f3f600bb1e1e43fc22c825bb9a1a69d93ae416719f1f0ad23cc9883)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "imagePassword", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bb2a5fd033dc56a594d9ccefa2d239da84f083906ef193d91bf32d5bee512f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "size"))

    @size.setter
    def size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2bb415086158881298c5a20c485c23e56e52328bf0f732d46b30bdd51e4812b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value)

    @builtins.property
    @jsii.member(jsii_name="sshKeys")
    def ssh_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshKeys"))

    @ssh_keys.setter
    def ssh_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e59c1b77a447d513bc7ed0e6ba267753da0ddb1879792173f7ef44ec3db18dd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshKeys", value)

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4678e5ceae510d3489c714fd8ab3ff18ffa1e98316dfa40cc485febc6e01df82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value)

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0990c43e2fca8b77121558685be394694901ee237e31f3871214252c58a02881)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f32509204ec20a09e0742290af4f8ee8a6429e0d9e2efd21a5b22a33ced9cd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupTimeouts",
    jsii_struct_bases=[],
    name_mapping={
        "create": "create",
        "default": "default",
        "delete": "delete",
        "update": "update",
    },
)
class AutoscalingGroupTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        default: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#create AutoscalingGroup#create}.
        :param default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#default AutoscalingGroup#default}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#update AutoscalingGroup#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c6c5ca22dcf261bc31cfb498b2824237993b5fb4c8044ff4348550c19be06d8)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument default", value=default, expected_type=type_hints["default"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if default is not None:
            self._values["default"] = default
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#create AutoscalingGroup#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#default AutoscalingGroup#default}.'''
        result = self._values.get("default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#delete AutoscalingGroup#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/ionos-cloud/ionoscloud/6.4.14/docs/resources/autoscaling_group#update AutoscalingGroup#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AutoscalingGroupTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AutoscalingGroupTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-ionoscloud.autoscalingGroup.AutoscalingGroupTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b3a8029091ff0c2b48a0aaf882de6820e10cf883b36a02744403e3e07d1a191)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDefault")
    def reset_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefault", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultInput")
    def default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f952ca7731e9f541ac83cb55cd1fc75b92958e3250b06af2383349c4810101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value)

    @builtins.property
    @jsii.member(jsii_name="default")
    def default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "default"))

    @default.setter
    def default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b6dc65d6dc352077be3c8d13aef669b83d4de63fdbd7cffb24a8f136b5de8f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "default", value)

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cc2d786f9f9c08a29add9586eec206bbf8e6cd06c8f46dcd72dd385e618b7ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value)

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d102433a8692d8d1f0456e08f4db778993a0d747d8a999a0843d2c585f3f2e24)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67366fd29382da65b20b101789e84d8f115f72c498f993e335f8497be89d3e55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "AutoscalingGroup",
    "AutoscalingGroupConfig",
    "AutoscalingGroupPolicy",
    "AutoscalingGroupPolicyOutputReference",
    "AutoscalingGroupPolicyScaleInAction",
    "AutoscalingGroupPolicyScaleInActionOutputReference",
    "AutoscalingGroupPolicyScaleOutAction",
    "AutoscalingGroupPolicyScaleOutActionOutputReference",
    "AutoscalingGroupReplicaConfiguration",
    "AutoscalingGroupReplicaConfigurationNic",
    "AutoscalingGroupReplicaConfigurationNicList",
    "AutoscalingGroupReplicaConfigurationNicOutputReference",
    "AutoscalingGroupReplicaConfigurationOutputReference",
    "AutoscalingGroupReplicaConfigurationVolume",
    "AutoscalingGroupReplicaConfigurationVolumeList",
    "AutoscalingGroupReplicaConfigurationVolumeOutputReference",
    "AutoscalingGroupTimeouts",
    "AutoscalingGroupTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__c3146dd62880db8c4a4a679ae36d31172810f23595b23353b8018fae683b4d75(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    datacenter_id: builtins.str,
    location: builtins.str,
    max_replica_count: jsii.Number,
    min_replica_count: jsii.Number,
    name: builtins.str,
    policy: typing.Union[AutoscalingGroupPolicy, typing.Dict[builtins.str, typing.Any]],
    replica_configuration: typing.Union[AutoscalingGroupReplicaConfiguration, typing.Dict[builtins.str, typing.Any]],
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[AutoscalingGroupTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e086ea468bafd4c868fa25a191755facf3c01266c1ff7a5bb47db0a613324ca(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa64c750b5399ce01da6d4e11088ee4c48367961ecf1c44f2ee899a04a021b0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0e3648c651a76707b9cd8410b25e85cc93402e8bdbe2fe2fd1bac10b1541429(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33627bbb96f63f0a19f6b4227fe8e98eb628acf7d6a5d6d5b58402e2e6e7dd28(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13fac770d256340aac888c3ece63afaf41f65d6645126008b33dd5b5ca9532ae(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14d0b42b145f0bdecd33b6a5f6f29c297e8586a933bda594d5a1926807677d46(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5eec38da3536bf995579a222f399ce03f33ff418f4e09671c17c535e2c8d6bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58053b66870c47f3bc0ab5e617378b61c4bb34d67bb04bc14365e28392ae1fa3(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    datacenter_id: builtins.str,
    location: builtins.str,
    max_replica_count: jsii.Number,
    min_replica_count: jsii.Number,
    name: builtins.str,
    policy: typing.Union[AutoscalingGroupPolicy, typing.Dict[builtins.str, typing.Any]],
    replica_configuration: typing.Union[AutoscalingGroupReplicaConfiguration, typing.Dict[builtins.str, typing.Any]],
    id: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[AutoscalingGroupTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68e702088158ad817c233bb2fdb4a934ac0d83af64565b75932648127031421f(
    *,
    metric: builtins.str,
    scale_in_action: typing.Union[AutoscalingGroupPolicyScaleInAction, typing.Dict[builtins.str, typing.Any]],
    scale_in_threshold: jsii.Number,
    scale_out_action: typing.Union[AutoscalingGroupPolicyScaleOutAction, typing.Dict[builtins.str, typing.Any]],
    scale_out_threshold: jsii.Number,
    unit: builtins.str,
    range: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b7f459aba3a8708621521fed4b6fdbc83c8c574108f722c3e9b6b267d9a79de(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2764da5d65fc915f2a7f0f315e2b9c3725b0991e79391c2ec3b17b384419d949(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa5f2570afc38dd5c1a2eb3f43b50274b24280761b7a3ac5f088f4baccb726b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6ae6f86524c15798e2b2be53d7412b883d806d85cb08f0b741fb762002c97cd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2df5e1d6d313726a46de06118313eb60eb081ffaf64af4424c4c4dae38a0db25(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd42ad0b6666b52acf4ec9a56d2b7a56b046d162627727f4e01bf8611fbeec3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fc8e1835a175893e3aa46a6a9d35b813890d9ba43e8449ce5b5ba63c1aba574(
    value: typing.Optional[AutoscalingGroupPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df38e3cdf7b235f5f6fe179e59631a45c22f33edab46beae2d4c68ce6235f891(
    *,
    amount: jsii.Number,
    amount_type: builtins.str,
    delete_volumes: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    cooldown_period: typing.Optional[builtins.str] = None,
    termination_policy_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ea303df8e2d25f599cbf66afd9f6bfe4268a8fbe0494ffb893c7fa19160fb62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204cfc21e156ebe762e24140c5b9b5b53909fdb1c1504d62b7434077e6403cfa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a981dac662cf18dc8dd7ee59ecb8df8d1001f0779f1d0c741940cc0f06e05a89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__536be0162f40286b13583f2bdff4f1d3342e75965e5abdff6113eb7a33c1bfc2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17c3730c0315324813b2ab8c5b73827c72b8bc5e340b1996a216ab5471d01ead(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a450bf2c72d16cb4f5d97e1e020c1f26b63f43573a0d4c42cc7ff9a9d80c6219(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555c5ec7b1809bb4d55c43985370defd1502475f8f112eab09150d6d2fbdbd70(
    value: typing.Optional[AutoscalingGroupPolicyScaleInAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16787c31ff992b6598a275a4db90ce816824c4ad8fccc7daf7512172120c4a7d(
    *,
    amount: jsii.Number,
    amount_type: builtins.str,
    cooldown_period: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165b096930701475659b425b1c1d1b799c5e7d92a4f7696b0117b0a8d44a4e02(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9d5b374cc13b0ad43c9c58ec95707bfb697ea13f24e2616526adca15048e618(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ceb1e010f2840fd631a64e69ba9bdcad0f6f88bf01f8283d9bb0f3c2285c23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ae6465cbf87029321d558b10af2eeca7a6d03f88ab82ab786f8fcd660e6c0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0cca00adac567f779cbb4c62cc55ebdbb7285f2288cabefdea29c0b3565e072(
    value: typing.Optional[AutoscalingGroupPolicyScaleOutAction],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9753c8e0b92272664f4f8fa7334c36abeafa315c55a3a421d6b61d3d28fc2a(
    *,
    availability_zone: builtins.str,
    cores: jsii.Number,
    ram: jsii.Number,
    cpu_family: typing.Optional[builtins.str] = None,
    nic: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]]] = None,
    volume: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationVolume, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7db78f4556b0eba4b01ccef6c2598a45961bb34cbe79a3e74e1752233cc5380(
    *,
    lan: jsii.Number,
    name: builtins.str,
    dhcp: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebf3052063fd3ab488ef7e4e2f592d47d55eed716301ace563fe9ae7dd07af33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4bf77b8c96d5a8cdb1de14fc706dcaf1ff03cbecd77b5a331ecc6f44786cd7e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d827d67c0b4d0a288bf9d5b489a9b0acb439c094598de6421605a82259156d8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adbf0a00215fc01f03b86f0782a02e23188e89eabd9d6c3bafa10474e093505a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__694fb45fb5662d8a15068c3761890f6b6dc9cf4efd18cf07369f0989b4195490(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080c71c5aa2f339511c040a723332d3070de7124e4050607adbf983c2226804b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationNic]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c1056ab7fcde8218a157992345e8eea145cb01708657524254c7d191161d2d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3412c9bddf61b5e6eb31daa6abe1d1edfacf59753ea5084489d5efc45c10a7b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb7e090377b2bb156aeaa591bedef2d760b7b7c8496820d54bbd1c137b6a8341(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f051c5aea2f72a66830f4f96b577ff4cbb61f62fe6033852a24b8c652b1fe90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__966666570e4b5b7856e18b615f56436d2ccdfb63090907b4dfc4377a01a837aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationNic]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c98eb701e487a04d289694169f4f1462a1c514bf9f3fe992d38f214f308a046b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198b6b23b6c02d366401147df266493eb117c9fab0111a9b36b4d435f8ce185a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationNic, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55dcb3fe0650b211894bf7c976ea8efc9db19a70106ef566b10168a2a4a80a1f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AutoscalingGroupReplicaConfigurationVolume, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ecd5f002c4fb199acb7a64fc64fd7b7eed894c6b4f54f65ff321f07c3505655(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ec8e06e2a6463598d1d2f9f050614f917f79b0aa958e6305a38f8091f872a2f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__236909ef7417a78ba6fe76c8eb36c9c11ad6ee29e8f7f1d4c7c2527a29c81dcc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e42aaed6cfdbc4a7624f2eb9264283c30b57336853ecd053dfa50d4592bdde(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c68c26597a550e588bbd9e71cef00a66c4c5c442d4acfc82b7223d8229f5395(
    value: typing.Optional[AutoscalingGroupReplicaConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f6f15e1974841b2872a9d8ddd17de311f008024ec20bffb1a82b7f01663eb61(
    *,
    boot_order: builtins.str,
    name: builtins.str,
    size: jsii.Number,
    type: builtins.str,
    backup_unit_id: typing.Optional[builtins.str] = None,
    bus: typing.Optional[builtins.str] = None,
    image: typing.Optional[builtins.str] = None,
    image_alias: typing.Optional[builtins.str] = None,
    image_password: typing.Optional[builtins.str] = None,
    ssh_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_data: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__991f24dea0804dbb901311fb3f27db77f4184d038526eb9832230701c28da5ae(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80dd3d402ba9b006ff1392dd4099eeeaba3c0019078750d781e793ed7d80cc7c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8814b4426559baa049e597e6499134643f94242bdbe7ca94b50667cf8dec0d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c4b574519d2ac8197c5b6756153523f66e740c1d0b251162385c53acce078f9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__678677ebd665a33ae1f692dda8e7828e2da2812c72a6aacf0525f4a3559538e4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__637ae6e6839bf25443b0f38165a5c07dc10703c879fb9c7b746c03b670090603(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AutoscalingGroupReplicaConfigurationVolume]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71307a76483f2b83b0d65e5b204e07d5673267c84ffcaf69113dbb92678f2142(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe4ebb5c2b34c15869f2a274dee54ffc22cc698a9f2842c043ef2f81455b98e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c15afae5963ab5d9e7128954d25a634c8b3c2177e2d29fcb8d86d340c6a1584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__219d3440216754d2e94e8821f2fc2f83e39667fef9c5857c9433212bcd5f52cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0b9731f9c3928a51ff4ccdb665e43a5a902fe5384b38d1d6fb084a7ad07e2ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b84d56ab1bf338d9fef3b1c89dd50ccb8811468e81fb60da6eb182fff213718(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6b372869f3f600bb1e1e43fc22c825bb9a1a69d93ae416719f1f0ad23cc9883(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bb2a5fd033dc56a594d9ccefa2d239da84f083906ef193d91bf32d5bee512f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2bb415086158881298c5a20c485c23e56e52328bf0f732d46b30bdd51e4812b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e59c1b77a447d513bc7ed0e6ba267753da0ddb1879792173f7ef44ec3db18dd3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4678e5ceae510d3489c714fd8ab3ff18ffa1e98316dfa40cc485febc6e01df82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0990c43e2fca8b77121558685be394694901ee237e31f3871214252c58a02881(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f32509204ec20a09e0742290af4f8ee8a6429e0d9e2efd21a5b22a33ced9cd9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupReplicaConfigurationVolume]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c6c5ca22dcf261bc31cfb498b2824237993b5fb4c8044ff4348550c19be06d8(
    *,
    create: typing.Optional[builtins.str] = None,
    default: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b3a8029091ff0c2b48a0aaf882de6820e10cf883b36a02744403e3e07d1a191(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f952ca7731e9f541ac83cb55cd1fc75b92958e3250b06af2383349c4810101(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b6dc65d6dc352077be3c8d13aef669b83d4de63fdbd7cffb24a8f136b5de8f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc2d786f9f9c08a29add9586eec206bbf8e6cd06c8f46dcd72dd385e618b7ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d102433a8692d8d1f0456e08f4db778993a0d747d8a999a0843d2c585f3f2e24(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67366fd29382da65b20b101789e84d8f115f72c498f993e335f8497be89d3e55(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AutoscalingGroupTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
