'''
# `kubernetes_endpoint_slice_v1`

Refer to the Terraform Registry for docs: [`kubernetes_endpoint_slice_v1`](https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1).
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


class EndpointSliceV1(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1 kubernetes_endpoint_slice_v1}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        address_type: builtins.str,
        endpoint: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Endpoint", typing.Dict[builtins.str, typing.Any]]]],
        metadata: typing.Union["EndpointSliceV1Metadata", typing.Dict[builtins.str, typing.Any]],
        port: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Port", typing.Dict[builtins.str, typing.Any]]]],
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1 kubernetes_endpoint_slice_v1} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param address_type: address_type specifies the type of address carried by this EndpointSlice. All addresses in this slice must be the same type. This field is immutable after creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#address_type EndpointSliceV1#address_type}
        :param endpoint: endpoint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#endpoint EndpointSliceV1#endpoint}
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#metadata EndpointSliceV1#metadata}
        :param port: port block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#port EndpointSliceV1#port}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#id EndpointSliceV1#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0309259eaba5f5e28b0ca475d276c9320e4fbbe0c4d8154c9eedd564c33dd001)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EndpointSliceV1Config(
            address_type=address_type,
            endpoint=endpoint,
            metadata=metadata,
            port=port,
            id=id,
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
        '''Generates CDKTF code for importing a EndpointSliceV1 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EndpointSliceV1 to import.
        :param import_from_id: The id of the existing EndpointSliceV1 that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EndpointSliceV1 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2ac93928db36b2c9962f85bb6e5e886ac5771a5e68a5d1d4911d1eb8d9a11a7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEndpoint")
    def put_endpoint(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Endpoint", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a8b958c04aef43b0d0e51f2ba8e7c553a184801e7efcc1352987e947ec42823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putEndpoint", [value]))

    @jsii.member(jsii_name="putMetadata")
    def put_metadata(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        generate_name: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param annotations: An unstructured key value map stored with the endpoint_slice that may be used to store arbitrary metadata. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#annotations EndpointSliceV1#annotations}
        :param generate_name: Prefix, used by the server, to generate a unique name ONLY IF the ``name`` field has not been provided. This value will also be combined with a unique suffix. More info: https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#idempotency Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#generate_name EndpointSliceV1#generate_name}
        :param labels: Map of string keys and values that can be used to organize and categorize (scope and select) the endpoint_slice. May match selectors of replication controllers and services. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#labels EndpointSliceV1#labels}
        :param name: Name of the endpoint_slice, must be unique. Cannot be updated. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        :param namespace: Namespace defines the space within which name of the endpoint_slice must be unique. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        '''
        value = EndpointSliceV1Metadata(
            annotations=annotations,
            generate_name=generate_name,
            labels=labels,
            name=name,
            namespace=namespace,
        )

        return typing.cast(None, jsii.invoke(self, "putMetadata", [value]))

    @jsii.member(jsii_name="putPort")
    def put_port(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Port", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc7a7c43d8e6f82395731018d25fed4d876d9f55606545b829780229aeed6035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPort", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> "EndpointSliceV1EndpointList":
        return typing.cast("EndpointSliceV1EndpointList", jsii.get(self, "endpoint"))

    @builtins.property
    @jsii.member(jsii_name="metadata")
    def metadata(self) -> "EndpointSliceV1MetadataOutputReference":
        return typing.cast("EndpointSliceV1MetadataOutputReference", jsii.get(self, "metadata"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> "EndpointSliceV1PortList":
        return typing.cast("EndpointSliceV1PortList", jsii.get(self, "port"))

    @builtins.property
    @jsii.member(jsii_name="addressTypeInput")
    def address_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addressTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Endpoint"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Endpoint"]]], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="metadataInput")
    def metadata_input(self) -> typing.Optional["EndpointSliceV1Metadata"]:
        return typing.cast(typing.Optional["EndpointSliceV1Metadata"], jsii.get(self, "metadataInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Port"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Port"]]], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="addressType")
    def address_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addressType"))

    @address_type.setter
    def address_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88f2f475ed44fb5a325523a2d96cabdf9ad3e2eaf669d1572e6236b620b67ecb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addressType", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84d64471fabedb2528c18584df5f49ae6784bd772f42426fc5290931028fae00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1Config",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "address_type": "addressType",
        "endpoint": "endpoint",
        "metadata": "metadata",
        "port": "port",
        "id": "id",
    },
)
class EndpointSliceV1Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        address_type: builtins.str,
        endpoint: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Endpoint", typing.Dict[builtins.str, typing.Any]]]],
        metadata: typing.Union["EndpointSliceV1Metadata", typing.Dict[builtins.str, typing.Any]],
        port: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EndpointSliceV1Port", typing.Dict[builtins.str, typing.Any]]]],
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param address_type: address_type specifies the type of address carried by this EndpointSlice. All addresses in this slice must be the same type. This field is immutable after creation. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#address_type EndpointSliceV1#address_type}
        :param endpoint: endpoint block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#endpoint EndpointSliceV1#endpoint}
        :param metadata: metadata block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#metadata EndpointSliceV1#metadata}
        :param port: port block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#port EndpointSliceV1#port}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#id EndpointSliceV1#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(metadata, dict):
            metadata = EndpointSliceV1Metadata(**metadata)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a49a27d56d297339a85f4200cd9a095f65c9d00f2289895c8fd0e06eaf58a8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument address_type", value=address_type, expected_type=type_hints["address_type"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument metadata", value=metadata, expected_type=type_hints["metadata"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "address_type": address_type,
            "endpoint": endpoint,
            "metadata": metadata,
            "port": port,
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
    def address_type(self) -> builtins.str:
        '''address_type specifies the type of address carried by this EndpointSlice.

        All addresses in this slice must be the same type. This field is immutable after creation.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#address_type EndpointSliceV1#address_type}
        '''
        result = self._values.get("address_type")
        assert result is not None, "Required property 'address_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def endpoint(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Endpoint"]]:
        '''endpoint block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#endpoint EndpointSliceV1#endpoint}
        '''
        result = self._values.get("endpoint")
        assert result is not None, "Required property 'endpoint' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Endpoint"]], result)

    @builtins.property
    def metadata(self) -> "EndpointSliceV1Metadata":
        '''metadata block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#metadata EndpointSliceV1#metadata}
        '''
        result = self._values.get("metadata")
        assert result is not None, "Required property 'metadata' is missing"
        return typing.cast("EndpointSliceV1Metadata", result)

    @builtins.property
    def port(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Port"]]:
        '''port block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#port EndpointSliceV1#port}
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EndpointSliceV1Port"]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#id EndpointSliceV1#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1Endpoint",
    jsii_struct_bases=[],
    name_mapping={
        "addresses": "addresses",
        "condition": "condition",
        "hostname": "hostname",
        "node_name": "nodeName",
        "target_ref": "targetRef",
        "zone": "zone",
    },
)
class EndpointSliceV1Endpoint:
    def __init__(
        self,
        *,
        addresses: typing.Sequence[builtins.str],
        condition: typing.Optional[typing.Union["EndpointSliceV1EndpointCondition", typing.Dict[builtins.str, typing.Any]]] = None,
        hostname: typing.Optional[builtins.str] = None,
        node_name: typing.Optional[builtins.str] = None,
        target_ref: typing.Optional[typing.Union["EndpointSliceV1EndpointTargetRef", typing.Dict[builtins.str, typing.Any]]] = None,
        zone: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param addresses: addresses of this endpoint. The contents of this field are interpreted according to the corresponding EndpointSlice addressType field. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#addresses EndpointSliceV1#addresses}
        :param condition: condition block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#condition EndpointSliceV1#condition}
        :param hostname: hostname of this endpoint. This field may be used by consumers of endpoints to distinguish endpoints from each other. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#hostname EndpointSliceV1#hostname}
        :param node_name: nodeName represents the name of the Node hosting this endpoint. This can be used to determine endpoints local to a Node. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#node_name EndpointSliceV1#node_name}
        :param target_ref: target_ref block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#target_ref EndpointSliceV1#target_ref}
        :param zone: zone is the name of the Zone this endpoint exists in. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#zone EndpointSliceV1#zone}
        '''
        if isinstance(condition, dict):
            condition = EndpointSliceV1EndpointCondition(**condition)
        if isinstance(target_ref, dict):
            target_ref = EndpointSliceV1EndpointTargetRef(**target_ref)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8a8025f4158d291624e0d37a1520ded4ea87fd1f4b2700df6cb832098db39a9)
            check_type(argname="argument addresses", value=addresses, expected_type=type_hints["addresses"])
            check_type(argname="argument condition", value=condition, expected_type=type_hints["condition"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument node_name", value=node_name, expected_type=type_hints["node_name"])
            check_type(argname="argument target_ref", value=target_ref, expected_type=type_hints["target_ref"])
            check_type(argname="argument zone", value=zone, expected_type=type_hints["zone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "addresses": addresses,
        }
        if condition is not None:
            self._values["condition"] = condition
        if hostname is not None:
            self._values["hostname"] = hostname
        if node_name is not None:
            self._values["node_name"] = node_name
        if target_ref is not None:
            self._values["target_ref"] = target_ref
        if zone is not None:
            self._values["zone"] = zone

    @builtins.property
    def addresses(self) -> typing.List[builtins.str]:
        '''addresses of this endpoint. The contents of this field are interpreted according to the corresponding EndpointSlice addressType field.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#addresses EndpointSliceV1#addresses}
        '''
        result = self._values.get("addresses")
        assert result is not None, "Required property 'addresses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def condition(self) -> typing.Optional["EndpointSliceV1EndpointCondition"]:
        '''condition block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#condition EndpointSliceV1#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional["EndpointSliceV1EndpointCondition"], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''hostname of this endpoint. This field may be used by consumers of endpoints to distinguish endpoints from each other.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#hostname EndpointSliceV1#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def node_name(self) -> typing.Optional[builtins.str]:
        '''nodeName represents the name of the Node hosting this endpoint.

        This can be used to determine endpoints local to a Node.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#node_name EndpointSliceV1#node_name}
        '''
        result = self._values.get("node_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_ref(self) -> typing.Optional["EndpointSliceV1EndpointTargetRef"]:
        '''target_ref block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#target_ref EndpointSliceV1#target_ref}
        '''
        result = self._values.get("target_ref")
        return typing.cast(typing.Optional["EndpointSliceV1EndpointTargetRef"], result)

    @builtins.property
    def zone(self) -> typing.Optional[builtins.str]:
        '''zone is the name of the Zone this endpoint exists in.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#zone EndpointSliceV1#zone}
        '''
        result = self._values.get("zone")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1Endpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointCondition",
    jsii_struct_bases=[],
    name_mapping={
        "ready": "ready",
        "serving": "serving",
        "terminating": "terminating",
    },
)
class EndpointSliceV1EndpointCondition:
    def __init__(
        self,
        *,
        ready: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serving: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        terminating: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param ready: ready indicates that this endpoint is prepared to receive traffic, according to whatever system is managing the endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#ready EndpointSliceV1#ready}
        :param serving: serving is identical to ready except that it is set regardless of the terminating state of endpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#serving EndpointSliceV1#serving}
        :param terminating: terminating indicates that this endpoint is terminating. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#terminating EndpointSliceV1#terminating}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a694cc5e301a6ababfcb890ffc05cf07308584d109e0e28b47b9eebcbdf7798d)
            check_type(argname="argument ready", value=ready, expected_type=type_hints["ready"])
            check_type(argname="argument serving", value=serving, expected_type=type_hints["serving"])
            check_type(argname="argument terminating", value=terminating, expected_type=type_hints["terminating"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ready is not None:
            self._values["ready"] = ready
        if serving is not None:
            self._values["serving"] = serving
        if terminating is not None:
            self._values["terminating"] = terminating

    @builtins.property
    def ready(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''ready indicates that this endpoint is prepared to receive traffic, according to whatever system is managing the endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#ready EndpointSliceV1#ready}
        '''
        result = self._values.get("ready")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def serving(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''serving is identical to ready except that it is set regardless of the terminating state of endpoints.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#serving EndpointSliceV1#serving}
        '''
        result = self._values.get("serving")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def terminating(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''terminating indicates that this endpoint is terminating.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#terminating EndpointSliceV1#terminating}
        '''
        result = self._values.get("terminating")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1EndpointCondition(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EndpointSliceV1EndpointConditionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointConditionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a05874a489562f4210337667e2fc3cedd866b8ae25da714c275d4764445db708)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetReady")
    def reset_ready(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReady", []))

    @jsii.member(jsii_name="resetServing")
    def reset_serving(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServing", []))

    @jsii.member(jsii_name="resetTerminating")
    def reset_terminating(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminating", []))

    @builtins.property
    @jsii.member(jsii_name="readyInput")
    def ready_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "readyInput"))

    @builtins.property
    @jsii.member(jsii_name="servingInput")
    def serving_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "servingInput"))

    @builtins.property
    @jsii.member(jsii_name="terminatingInput")
    def terminating_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminatingInput"))

    @builtins.property
    @jsii.member(jsii_name="ready")
    def ready(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ready"))

    @ready.setter
    def ready(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9c100e9d4d4941bb4ab21a3d1cf0bcdebb9a610209f293d88069b25afb79fe5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ready", value)

    @builtins.property
    @jsii.member(jsii_name="serving")
    def serving(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serving"))

    @serving.setter
    def serving(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f622d50764737ad89ba8cb5647e0f75f097b825c50dec6230904e5fabcf08290)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serving", value)

    @builtins.property
    @jsii.member(jsii_name="terminating")
    def terminating(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminating"))

    @terminating.setter
    def terminating(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__614e529575149e313f068396b48403c6d8d5290d2e9c586b77cc27f1fc787e42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminating", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EndpointSliceV1EndpointCondition]:
        return typing.cast(typing.Optional[EndpointSliceV1EndpointCondition], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EndpointSliceV1EndpointCondition],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efa16f27de21fcccb14e7409a1c93bfb46cc037c668ccad73e71dd6ac01fed85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class EndpointSliceV1EndpointList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7c7dda122854adbfd3603d670dd5b2568df142a6acb501c0323a953efa153f2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "EndpointSliceV1EndpointOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3d3d85442f97f6c6f7e56c9cbf4649c007fd34b5f2942671bdf3219d08dfda)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("EndpointSliceV1EndpointOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56e08417499b9f3a32eca91df43ebb49999feb5f3522ec703a1399a866fb263a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d28eb207dc8d5dbfc355b9c04d964c440acf710d01ca94513e5d0c0084b9126a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f5813c27327c87613ddc9a32039b0a38e29d20442e344ad4a0834c8ae30ac79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Endpoint]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Endpoint]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Endpoint]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d38511a836de086ac983b1f80aebfc7da8844c2bb80784e258bf3621af3c0f11)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class EndpointSliceV1EndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de54e7ea95af495f123e251a9391558ef422cf36a37ec19715d5346e79d3c5c2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCondition")
    def put_condition(
        self,
        *,
        ready: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        serving: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        terminating: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param ready: ready indicates that this endpoint is prepared to receive traffic, according to whatever system is managing the endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#ready EndpointSliceV1#ready}
        :param serving: serving is identical to ready except that it is set regardless of the terminating state of endpoints. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#serving EndpointSliceV1#serving}
        :param terminating: terminating indicates that this endpoint is terminating. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#terminating EndpointSliceV1#terminating}
        '''
        value = EndpointSliceV1EndpointCondition(
            ready=ready, serving=serving, terminating=terminating
        )

        return typing.cast(None, jsii.invoke(self, "putCondition", [value]))

    @jsii.member(jsii_name="putTargetRef")
    def put_target_ref(
        self,
        *,
        name: builtins.str,
        field_path: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        resource_version: typing.Optional[builtins.str] = None,
        uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the referent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        :param field_path: If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#field_path EndpointSliceV1#field_path}
        :param namespace: Namespace of the referent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        :param resource_version: Specific resourceVersion to which this reference is made, if any. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#resource_version EndpointSliceV1#resource_version}
        :param uid: If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#uid EndpointSliceV1#uid}
        '''
        value = EndpointSliceV1EndpointTargetRef(
            name=name,
            field_path=field_path,
            namespace=namespace,
            resource_version=resource_version,
            uid=uid,
        )

        return typing.cast(None, jsii.invoke(self, "putTargetRef", [value]))

    @jsii.member(jsii_name="resetCondition")
    def reset_condition(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCondition", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetNodeName")
    def reset_node_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNodeName", []))

    @jsii.member(jsii_name="resetTargetRef")
    def reset_target_ref(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetRef", []))

    @jsii.member(jsii_name="resetZone")
    def reset_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZone", []))

    @builtins.property
    @jsii.member(jsii_name="condition")
    def condition(self) -> EndpointSliceV1EndpointConditionOutputReference:
        return typing.cast(EndpointSliceV1EndpointConditionOutputReference, jsii.get(self, "condition"))

    @builtins.property
    @jsii.member(jsii_name="targetRef")
    def target_ref(self) -> "EndpointSliceV1EndpointTargetRefOutputReference":
        return typing.cast("EndpointSliceV1EndpointTargetRefOutputReference", jsii.get(self, "targetRef"))

    @builtins.property
    @jsii.member(jsii_name="addressesInput")
    def addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "addressesInput"))

    @builtins.property
    @jsii.member(jsii_name="conditionInput")
    def condition_input(self) -> typing.Optional[EndpointSliceV1EndpointCondition]:
        return typing.cast(typing.Optional[EndpointSliceV1EndpointCondition], jsii.get(self, "conditionInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="nodeNameInput")
    def node_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nodeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetRefInput")
    def target_ref_input(self) -> typing.Optional["EndpointSliceV1EndpointTargetRef"]:
        return typing.cast(typing.Optional["EndpointSliceV1EndpointTargetRef"], jsii.get(self, "targetRefInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneInput")
    def zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneInput"))

    @builtins.property
    @jsii.member(jsii_name="addresses")
    def addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "addresses"))

    @addresses.setter
    def addresses(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e991ea8594706e830a4e305f8a1dce12a9be38d46560522388ec8e9dd9699f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addresses", value)

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__664ee9cbc1a49903017c9fe3f5c4c5cb846cceba8f935c45806f9ef9994c811e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value)

    @builtins.property
    @jsii.member(jsii_name="nodeName")
    def node_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nodeName"))

    @node_name.setter
    def node_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4a6aa1160c514e811e8c771187cdb7da6e70c2fd8ad4bbb737d424689677f9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nodeName", value)

    @builtins.property
    @jsii.member(jsii_name="zone")
    def zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zone"))

    @zone.setter
    def zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__398646b53ca9bdde3f1c32bb3be5e266a239b97a25fe713dc42cc6a29d9087dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zone", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Endpoint]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Endpoint]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Endpoint]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f66a4aa4db26de7cb3784b027a1103101f7539e26216caa4a75af886b46b0605)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointTargetRef",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "field_path": "fieldPath",
        "namespace": "namespace",
        "resource_version": "resourceVersion",
        "uid": "uid",
    },
)
class EndpointSliceV1EndpointTargetRef:
    def __init__(
        self,
        *,
        name: builtins.str,
        field_path: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
        resource_version: typing.Optional[builtins.str] = None,
        uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the referent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        :param field_path: If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#field_path EndpointSliceV1#field_path}
        :param namespace: Namespace of the referent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        :param resource_version: Specific resourceVersion to which this reference is made, if any. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#resource_version EndpointSliceV1#resource_version}
        :param uid: If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2]. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#uid EndpointSliceV1#uid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a810a7af2253410bb050371c57c9c7a1a8a0f0c22d2f3a1dc0f1c7963393482)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument field_path", value=field_path, expected_type=type_hints["field_path"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
            check_type(argname="argument resource_version", value=resource_version, expected_type=type_hints["resource_version"])
            check_type(argname="argument uid", value=uid, expected_type=type_hints["uid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if field_path is not None:
            self._values["field_path"] = field_path
        if namespace is not None:
            self._values["namespace"] = namespace
        if resource_version is not None:
            self._values["resource_version"] = resource_version
        if uid is not None:
            self._values["uid"] = uid

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the referent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def field_path(self) -> typing.Optional[builtins.str]:
        '''If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#field_path EndpointSliceV1#field_path}
        '''
        result = self._values.get("field_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace of the referent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_version(self) -> typing.Optional[builtins.str]:
        '''Specific resourceVersion to which this reference is made, if any.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#resource_version EndpointSliceV1#resource_version}
        '''
        result = self._values.get("resource_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uid(self) -> typing.Optional[builtins.str]:
        '''If referring to a piece of an object instead of an entire object, this string should contain a valid JSON/Go field access statement, such as desiredState.manifest.containers[2].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#uid EndpointSliceV1#uid}
        '''
        result = self._values.get("uid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1EndpointTargetRef(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EndpointSliceV1EndpointTargetRefOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1EndpointTargetRefOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b0d69f2b3921d52e6c3405a75f35ca1dcc6f96673533424b4f96ef28ec12b0c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetFieldPath")
    def reset_field_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFieldPath", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @jsii.member(jsii_name="resetResourceVersion")
    def reset_resource_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceVersion", []))

    @jsii.member(jsii_name="resetUid")
    def reset_uid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUid", []))

    @builtins.property
    @jsii.member(jsii_name="fieldPathInput")
    def field_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldPathInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceVersionInput")
    def resource_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="uidInput")
    def uid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uidInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldPath")
    def field_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldPath"))

    @field_path.setter
    def field_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__396b26212322163edfeef8317204b22dbbce865c5bf9874bbfc4d216f4541a6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldPath", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c760e25e250dc1515170debccc311f2d91580ec3776e898f56995032bd3cb609)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4cfb0e25be75f0c3fd7114b90ef8bbbcb135efc33e44dd0d68bda26cf58f487)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property
    @jsii.member(jsii_name="resourceVersion")
    def resource_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceVersion"))

    @resource_version.setter
    def resource_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9000983e4babd4d55583ff742b1a0badec20a2dccb513988f576d3dbe618262)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceVersion", value)

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @uid.setter
    def uid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33db1075597ba20db2cf77643cea6204868defb46fe0ba621c35c787eeab18d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uid", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EndpointSliceV1EndpointTargetRef]:
        return typing.cast(typing.Optional[EndpointSliceV1EndpointTargetRef], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EndpointSliceV1EndpointTargetRef],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f24063a6d0052b51dc419c54284877c27a5b0b731028e09d1376af0ddf0e7f87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1Metadata",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "generate_name": "generateName",
        "labels": "labels",
        "name": "name",
        "namespace": "namespace",
    },
)
class EndpointSliceV1Metadata:
    def __init__(
        self,
        *,
        annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        generate_name: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        name: typing.Optional[builtins.str] = None,
        namespace: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param annotations: An unstructured key value map stored with the endpoint_slice that may be used to store arbitrary metadata. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#annotations EndpointSliceV1#annotations}
        :param generate_name: Prefix, used by the server, to generate a unique name ONLY IF the ``name`` field has not been provided. This value will also be combined with a unique suffix. More info: https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#idempotency Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#generate_name EndpointSliceV1#generate_name}
        :param labels: Map of string keys and values that can be used to organize and categorize (scope and select) the endpoint_slice. May match selectors of replication controllers and services. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#labels EndpointSliceV1#labels}
        :param name: Name of the endpoint_slice, must be unique. Cannot be updated. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        :param namespace: Namespace defines the space within which name of the endpoint_slice must be unique. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46bbaaf4cb82baafa119306c700d940681def81eeb14b1608d1b8584e48150f3)
            check_type(argname="argument annotations", value=annotations, expected_type=type_hints["annotations"])
            check_type(argname="argument generate_name", value=generate_name, expected_type=type_hints["generate_name"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument namespace", value=namespace, expected_type=type_hints["namespace"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if annotations is not None:
            self._values["annotations"] = annotations
        if generate_name is not None:
            self._values["generate_name"] = generate_name
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name
        if namespace is not None:
            self._values["namespace"] = namespace

    @builtins.property
    def annotations(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''An unstructured key value map stored with the endpoint_slice that may be used to store arbitrary metadata.

        More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#annotations EndpointSliceV1#annotations}
        '''
        result = self._values.get("annotations")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def generate_name(self) -> typing.Optional[builtins.str]:
        '''Prefix, used by the server, to generate a unique name ONLY IF the ``name`` field has not been provided.

        This value will also be combined with a unique suffix. More info: https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#idempotency

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#generate_name EndpointSliceV1#generate_name}
        '''
        result = self._values.get("generate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Map of string keys and values that can be used to organize and categorize (scope and select) the endpoint_slice.

        May match selectors of replication controllers and services. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#labels EndpointSliceV1#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the endpoint_slice, must be unique. Cannot be updated. More info: https://kubernetes.io/docs/concepts/overview/working-with-objects/names/#names.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        '''Namespace defines the space within which name of the endpoint_slice must be unique.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#namespace EndpointSliceV1#namespace}
        '''
        result = self._values.get("namespace")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1Metadata(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EndpointSliceV1MetadataOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1MetadataOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1e72927fc6d5d1e3c54e16b3594e95a557147ba1fe975f9e2086dbad702b4be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAnnotations")
    def reset_annotations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnnotations", []))

    @jsii.member(jsii_name="resetGenerateName")
    def reset_generate_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGenerateName", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamespace")
    def reset_namespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamespace", []))

    @builtins.property
    @jsii.member(jsii_name="generation")
    def generation(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "generation"))

    @builtins.property
    @jsii.member(jsii_name="resourceVersion")
    def resource_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceVersion"))

    @builtins.property
    @jsii.member(jsii_name="uid")
    def uid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uid"))

    @builtins.property
    @jsii.member(jsii_name="annotationsInput")
    def annotations_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "annotationsInput"))

    @builtins.property
    @jsii.member(jsii_name="generateNameInput")
    def generate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "generateNameInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="namespaceInput")
    def namespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="annotations")
    def annotations(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "annotations"))

    @annotations.setter
    def annotations(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__253a90d3dcd58f0623d3227209865e1c953000e3e5b707026e6d34e92b101274)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "annotations", value)

    @builtins.property
    @jsii.member(jsii_name="generateName")
    def generate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "generateName"))

    @generate_name.setter
    def generate_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e40822778f58879c4627f5aedf2d6fba00bf61c2062e13e1ed4727c29d835196)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "generateName", value)

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65b96aa903439dff1d569809053f91c7821f170ea05185c0293003236732930c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "labels", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__738180849d12864f9aa579767a2780a8b442fd50083fe34e263e738c7803ad59)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namespace"))

    @namespace.setter
    def namespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b70aa3099f6c9cefff8eb8e0933af763aa6781fd8aacae5d306d5c94448ff2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "namespace", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EndpointSliceV1Metadata]:
        return typing.cast(typing.Optional[EndpointSliceV1Metadata], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[EndpointSliceV1Metadata]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a451eedb56517989989cff3926f6c36b5f1fc060d2e3f17f47b3d2b8c955ae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1Port",
    jsii_struct_bases=[],
    name_mapping={
        "app_protocol": "appProtocol",
        "port": "port",
        "name": "name",
        "protocol": "protocol",
    },
)
class EndpointSliceV1Port:
    def __init__(
        self,
        *,
        app_protocol: builtins.str,
        port: builtins.str,
        name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param app_protocol: The application protocol for this port. This is used as a hint for implementations to offer richer behavior for protocols that they understand. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#app_protocol EndpointSliceV1#app_protocol}
        :param port: port represents the port number of the endpoint. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#port EndpointSliceV1#port}
        :param name: name represents the name of this port. All ports in an EndpointSlice must have a unique name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        :param protocol: protocol represents the IP protocol for this port. Must be UDP, TCP, or SCTP. Default is TCP. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#protocol EndpointSliceV1#protocol}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792f2ea872525855202a886c04b3c96248e01ec472fefcd3d5323fc419703e3a)
            check_type(argname="argument app_protocol", value=app_protocol, expected_type=type_hints["app_protocol"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_protocol": app_protocol,
            "port": port,
        }
        if name is not None:
            self._values["name"] = name
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def app_protocol(self) -> builtins.str:
        '''The application protocol for this port.

        This is used as a hint for implementations to offer richer behavior for protocols that they understand.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#app_protocol EndpointSliceV1#app_protocol}
        '''
        result = self._values.get("app_protocol")
        assert result is not None, "Required property 'app_protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port(self) -> builtins.str:
        '''port represents the port number of the endpoint.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#port EndpointSliceV1#port}
        '''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''name represents the name of this port. All ports in an EndpointSlice must have a unique name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#name EndpointSliceV1#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''protocol represents the IP protocol for this port. Must be UDP, TCP, or SCTP. Default is TCP.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/kubernetes/2.28.0/docs/resources/endpoint_slice_v1#protocol EndpointSliceV1#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EndpointSliceV1Port(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EndpointSliceV1PortList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1PortList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d118674aee2cc3317947e20dfc0b37ae4bfdc68da175a78dde7105bcaf8db487)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "EndpointSliceV1PortOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e76db83408b290f9f4800269e979ba830593f31efe8bf22e0789a5aa4aa4f017)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("EndpointSliceV1PortOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__131aa46faa7f93f0cb6b37539568caf94375a36873cfccdda3e85e09b0ad5e82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__72c05dc412df0ad0b8e0d4277a71069311c1961eaef3d102044348484c4240be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a066fee42c54d6174e4568b10c4d30bae1cb7b2f1e2b63282294bb82a109060e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Port]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Port]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Port]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__295817c1587c623bc1324763ef1a3ac0ac32639488c3f4d98024abd7e52adc5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class EndpointSliceV1PortOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-kubernetes.endpointSliceV1.EndpointSliceV1PortOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__264078449654ee88ece5196bdcef9020ccf690d258767d96f2fcfd88a871ad2e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="appProtocolInput")
    def app_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="appProtocol")
    def app_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appProtocol"))

    @app_protocol.setter
    def app_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a13abd3546ef4024c9fad7c1f87ab57a574510e60c02323c67146406bf3b0424)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appProtocol", value)

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c033c9a90e2a8c23fe971dbce07416da54170e6d7e87ff800cc4ba6cc09457da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value)

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "port"))

    @port.setter
    def port(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71ac7752e862f9605799640797a84ac25bcf05022f20c46532cdcb72f0445412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49cc316f1b72461a743a007189e10b18513351e2f3a01a7273934aad3eed7e32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Port]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Port]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Port]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__889b7a692aac7678a600893eb0986f6cd786e79b33cf9f870a8c3a9428e5dc8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "EndpointSliceV1",
    "EndpointSliceV1Config",
    "EndpointSliceV1Endpoint",
    "EndpointSliceV1EndpointCondition",
    "EndpointSliceV1EndpointConditionOutputReference",
    "EndpointSliceV1EndpointList",
    "EndpointSliceV1EndpointOutputReference",
    "EndpointSliceV1EndpointTargetRef",
    "EndpointSliceV1EndpointTargetRefOutputReference",
    "EndpointSliceV1Metadata",
    "EndpointSliceV1MetadataOutputReference",
    "EndpointSliceV1Port",
    "EndpointSliceV1PortList",
    "EndpointSliceV1PortOutputReference",
]

publication.publish()

def _typecheckingstub__0309259eaba5f5e28b0ca475d276c9320e4fbbe0c4d8154c9eedd564c33dd001(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    address_type: builtins.str,
    endpoint: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Endpoint, typing.Dict[builtins.str, typing.Any]]]],
    metadata: typing.Union[EndpointSliceV1Metadata, typing.Dict[builtins.str, typing.Any]],
    port: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Port, typing.Dict[builtins.str, typing.Any]]]],
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__a2ac93928db36b2c9962f85bb6e5e886ac5771a5e68a5d1d4911d1eb8d9a11a7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a8b958c04aef43b0d0e51f2ba8e7c553a184801e7efcc1352987e947ec42823(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Endpoint, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc7a7c43d8e6f82395731018d25fed4d876d9f55606545b829780229aeed6035(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Port, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88f2f475ed44fb5a325523a2d96cabdf9ad3e2eaf669d1572e6236b620b67ecb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84d64471fabedb2528c18584df5f49ae6784bd772f42426fc5290931028fae00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69a49a27d56d297339a85f4200cd9a095f65c9d00f2289895c8fd0e06eaf58a8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    address_type: builtins.str,
    endpoint: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Endpoint, typing.Dict[builtins.str, typing.Any]]]],
    metadata: typing.Union[EndpointSliceV1Metadata, typing.Dict[builtins.str, typing.Any]],
    port: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EndpointSliceV1Port, typing.Dict[builtins.str, typing.Any]]]],
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8a8025f4158d291624e0d37a1520ded4ea87fd1f4b2700df6cb832098db39a9(
    *,
    addresses: typing.Sequence[builtins.str],
    condition: typing.Optional[typing.Union[EndpointSliceV1EndpointCondition, typing.Dict[builtins.str, typing.Any]]] = None,
    hostname: typing.Optional[builtins.str] = None,
    node_name: typing.Optional[builtins.str] = None,
    target_ref: typing.Optional[typing.Union[EndpointSliceV1EndpointTargetRef, typing.Dict[builtins.str, typing.Any]]] = None,
    zone: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a694cc5e301a6ababfcb890ffc05cf07308584d109e0e28b47b9eebcbdf7798d(
    *,
    ready: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    serving: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    terminating: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a05874a489562f4210337667e2fc3cedd866b8ae25da714c275d4764445db708(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9c100e9d4d4941bb4ab21a3d1cf0bcdebb9a610209f293d88069b25afb79fe5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f622d50764737ad89ba8cb5647e0f75f097b825c50dec6230904e5fabcf08290(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__614e529575149e313f068396b48403c6d8d5290d2e9c586b77cc27f1fc787e42(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efa16f27de21fcccb14e7409a1c93bfb46cc037c668ccad73e71dd6ac01fed85(
    value: typing.Optional[EndpointSliceV1EndpointCondition],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7c7dda122854adbfd3603d670dd5b2568df142a6acb501c0323a953efa153f2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3d3d85442f97f6c6f7e56c9cbf4649c007fd34b5f2942671bdf3219d08dfda(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56e08417499b9f3a32eca91df43ebb49999feb5f3522ec703a1399a866fb263a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28eb207dc8d5dbfc355b9c04d964c440acf710d01ca94513e5d0c0084b9126a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f5813c27327c87613ddc9a32039b0a38e29d20442e344ad4a0834c8ae30ac79(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d38511a836de086ac983b1f80aebfc7da8844c2bb80784e258bf3621af3c0f11(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Endpoint]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de54e7ea95af495f123e251a9391558ef422cf36a37ec19715d5346e79d3c5c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e991ea8594706e830a4e305f8a1dce12a9be38d46560522388ec8e9dd9699f5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__664ee9cbc1a49903017c9fe3f5c4c5cb846cceba8f935c45806f9ef9994c811e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4a6aa1160c514e811e8c771187cdb7da6e70c2fd8ad4bbb737d424689677f9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__398646b53ca9bdde3f1c32bb3be5e266a239b97a25fe713dc42cc6a29d9087dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f66a4aa4db26de7cb3784b027a1103101f7539e26216caa4a75af886b46b0605(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Endpoint]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a810a7af2253410bb050371c57c9c7a1a8a0f0c22d2f3a1dc0f1c7963393482(
    *,
    name: builtins.str,
    field_path: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
    resource_version: typing.Optional[builtins.str] = None,
    uid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b0d69f2b3921d52e6c3405a75f35ca1dcc6f96673533424b4f96ef28ec12b0c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__396b26212322163edfeef8317204b22dbbce865c5bf9874bbfc4d216f4541a6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c760e25e250dc1515170debccc311f2d91580ec3776e898f56995032bd3cb609(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4cfb0e25be75f0c3fd7114b90ef8bbbcb135efc33e44dd0d68bda26cf58f487(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9000983e4babd4d55583ff742b1a0badec20a2dccb513988f576d3dbe618262(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33db1075597ba20db2cf77643cea6204868defb46fe0ba621c35c787eeab18d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f24063a6d0052b51dc419c54284877c27a5b0b731028e09d1376af0ddf0e7f87(
    value: typing.Optional[EndpointSliceV1EndpointTargetRef],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46bbaaf4cb82baafa119306c700d940681def81eeb14b1608d1b8584e48150f3(
    *,
    annotations: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    generate_name: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    name: typing.Optional[builtins.str] = None,
    namespace: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1e72927fc6d5d1e3c54e16b3594e95a557147ba1fe975f9e2086dbad702b4be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__253a90d3dcd58f0623d3227209865e1c953000e3e5b707026e6d34e92b101274(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e40822778f58879c4627f5aedf2d6fba00bf61c2062e13e1ed4727c29d835196(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65b96aa903439dff1d569809053f91c7821f170ea05185c0293003236732930c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__738180849d12864f9aa579767a2780a8b442fd50083fe34e263e738c7803ad59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b70aa3099f6c9cefff8eb8e0933af763aa6781fd8aacae5d306d5c94448ff2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a451eedb56517989989cff3926f6c36b5f1fc060d2e3f17f47b3d2b8c955ae8(
    value: typing.Optional[EndpointSliceV1Metadata],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792f2ea872525855202a886c04b3c96248e01ec472fefcd3d5323fc419703e3a(
    *,
    app_protocol: builtins.str,
    port: builtins.str,
    name: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d118674aee2cc3317947e20dfc0b37ae4bfdc68da175a78dde7105bcaf8db487(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76db83408b290f9f4800269e979ba830593f31efe8bf22e0789a5aa4aa4f017(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__131aa46faa7f93f0cb6b37539568caf94375a36873cfccdda3e85e09b0ad5e82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72c05dc412df0ad0b8e0d4277a71069311c1961eaef3d102044348484c4240be(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a066fee42c54d6174e4568b10c4d30bae1cb7b2f1e2b63282294bb82a109060e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__295817c1587c623bc1324763ef1a3ac0ac32639488c3f4d98024abd7e52adc5c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EndpointSliceV1Port]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__264078449654ee88ece5196bdcef9020ccf690d258767d96f2fcfd88a871ad2e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a13abd3546ef4024c9fad7c1f87ab57a574510e60c02323c67146406bf3b0424(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c033c9a90e2a8c23fe971dbce07416da54170e6d7e87ff800cc4ba6cc09457da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71ac7752e862f9605799640797a84ac25bcf05022f20c46532cdcb72f0445412(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49cc316f1b72461a743a007189e10b18513351e2f3a01a7273934aad3eed7e32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__889b7a692aac7678a600893eb0986f6cd786e79b33cf9f870a8c3a9428e5dc8e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EndpointSliceV1Port]],
) -> None:
    """Type checking stubs"""
    pass
