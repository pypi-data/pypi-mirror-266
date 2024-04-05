'''
# `data_aws_resourceexplorer2_search`

Refer to the Terraform Registry for docs: [`data_aws_resourceexplorer2_search`](https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search).
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


class DataAwsResourceexplorer2Search(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2Search",
):
    '''Represents a {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search aws_resourceexplorer2_search}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        query_string: builtins.str,
        resource_count: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResourceCount", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        view_arn: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search aws_resourceexplorer2_search} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#query_string DataAwsResourceexplorer2Search#query_string}.
        :param resource_count: resource_count block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resource_count DataAwsResourceexplorer2Search#resource_count}
        :param resources: resources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resources DataAwsResourceexplorer2Search#resources}
        :param view_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#view_arn DataAwsResourceexplorer2Search#view_arn}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7ea22b46e9faaa1316bce00eb2f4e6075ca34e7109d2050850bf2f759cb3a84)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DataAwsResourceexplorer2SearchConfig(
            query_string=query_string,
            resource_count=resource_count,
            resources=resources,
            view_arn=view_arn,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DataAwsResourceexplorer2Search resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataAwsResourceexplorer2Search to import.
        :param import_from_id: The id of the existing DataAwsResourceexplorer2Search that should be imported. Refer to the {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataAwsResourceexplorer2Search to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1967ec0634e8628bab0703e00f1ec8da11192fa52cb83b152b8f8859905c6a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putResourceCount")
    def put_resource_count(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResourceCount", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__573bdca33f8dfa4d2cf002f228c7e2df65f999f7c130a9586651cc75d7625ed6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceCount", [value]))

    @jsii.member(jsii_name="putResources")
    def put_resources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResources", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__868ba4f3dd1fbbb1c9e1d77a85bf0b485512c824fce493d11e6b32895cd269bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResources", [value]))

    @jsii.member(jsii_name="resetResourceCount")
    def reset_resource_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceCount", []))

    @jsii.member(jsii_name="resetResources")
    def reset_resources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResources", []))

    @jsii.member(jsii_name="resetViewArn")
    def reset_view_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViewArn", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="resourceCount")
    def resource_count(self) -> "DataAwsResourceexplorer2SearchResourceCountList":
        return typing.cast("DataAwsResourceexplorer2SearchResourceCountList", jsii.get(self, "resourceCount"))

    @builtins.property
    @jsii.member(jsii_name="resources")
    def resources(self) -> "DataAwsResourceexplorer2SearchResourcesList":
        return typing.cast("DataAwsResourceexplorer2SearchResourcesList", jsii.get(self, "resources"))

    @builtins.property
    @jsii.member(jsii_name="queryStringInput")
    def query_string_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryStringInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceCountInput")
    def resource_count_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourceCount"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourceCount"]]], jsii.get(self, "resourceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="resourcesInput")
    def resources_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResources"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResources"]]], jsii.get(self, "resourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="viewArnInput")
    def view_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "viewArnInput"))

    @builtins.property
    @jsii.member(jsii_name="queryString")
    def query_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "queryString"))

    @query_string.setter
    def query_string(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a82a5c2b8e6b1cf0333aca4d22311c7a5c24bb12d36137caf8473995ebb9344)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "queryString", value)

    @builtins.property
    @jsii.member(jsii_name="viewArn")
    def view_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "viewArn"))

    @view_arn.setter
    def view_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66993de8d6e66c029eb055df431c801fca54b466bc58cad331ec7bb45ecc10bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "viewArn", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "query_string": "queryString",
        "resource_count": "resourceCount",
        "resources": "resources",
        "view_arn": "viewArn",
    },
)
class DataAwsResourceexplorer2SearchConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        query_string: builtins.str,
        resource_count: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResourceCount", typing.Dict[builtins.str, typing.Any]]]]] = None,
        resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        view_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param query_string: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#query_string DataAwsResourceexplorer2Search#query_string}.
        :param resource_count: resource_count block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resource_count DataAwsResourceexplorer2Search#resource_count}
        :param resources: resources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resources DataAwsResourceexplorer2Search#resources}
        :param view_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#view_arn DataAwsResourceexplorer2Search#view_arn}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01e12b722c5c6d6976a7eaf20b2bb2cbab77ac851819352ea6295cfc6e22705e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument query_string", value=query_string, expected_type=type_hints["query_string"])
            check_type(argname="argument resource_count", value=resource_count, expected_type=type_hints["resource_count"])
            check_type(argname="argument resources", value=resources, expected_type=type_hints["resources"])
            check_type(argname="argument view_arn", value=view_arn, expected_type=type_hints["view_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "query_string": query_string,
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
        if resource_count is not None:
            self._values["resource_count"] = resource_count
        if resources is not None:
            self._values["resources"] = resources
        if view_arn is not None:
            self._values["view_arn"] = view_arn

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
    def query_string(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#query_string DataAwsResourceexplorer2Search#query_string}.'''
        result = self._values.get("query_string")
        assert result is not None, "Required property 'query_string' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def resource_count(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourceCount"]]]:
        '''resource_count block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resource_count DataAwsResourceexplorer2Search#resource_count}
        '''
        result = self._values.get("resource_count")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourceCount"]]], result)

    @builtins.property
    def resources(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResources"]]]:
        '''resources block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resources DataAwsResourceexplorer2Search#resources}
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResources"]]], result)

    @builtins.property
    def view_arn(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#view_arn DataAwsResourceexplorer2Search#view_arn}.'''
        result = self._values.get("view_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourceexplorer2SearchConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourceCount",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsResourceexplorer2SearchResourceCount:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourceexplorer2SearchResourceCount(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsResourceexplorer2SearchResourceCountList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourceCountList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf574af5a1a9aa39fa133a7d29bee2d2987c39b33305d4e4cee2ba33aa0315ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsResourceexplorer2SearchResourceCountOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aec893d8eb70aa81af1488a2a476577642264929c9eaa061a6effa74bc5efee1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsResourceexplorer2SearchResourceCountOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__176f2678defd7c5f1cefde186e77a1b67fef195ad88708823b9d68d9af19b7d0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__261f2c83fa6cf29d57743a321389cfb36d38a5bba0016dfabdc84dae4cbd3385)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5fdb01a4fb783b853efb968d328287238a5967f8ae71de645a5bcfa20a8479a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourceCount]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourceCount]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourceCount]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b43bab2df4a5561928546a436a906ade2738142cb84fa9071778cc735c2bba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsResourceexplorer2SearchResourceCountOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourceCountOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc5ae702c23fd0c6e5c24b2e047523385476e5ab8b74618115caa2061db19b52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="complete")
    def complete(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "complete"))

    @builtins.property
    @jsii.member(jsii_name="totalResources")
    def total_resources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalResources"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourceCount]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourceCount]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourceCount]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf52ad66d2d211b01083fe37663c149eced9e6aa0af894e4036fa299cdf1dfa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResources",
    jsii_struct_bases=[],
    name_mapping={"resource_property": "resourceProperty"},
)
class DataAwsResourceexplorer2SearchResources:
    def __init__(
        self,
        *,
        resource_property: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResourcesResourceProperty", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param resource_property: resource_property block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resource_property DataAwsResourceexplorer2Search#resource_property}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d4081446d5acb4d8bcc50c2de6bbf521aec41936c2aae26e4ebb77cabf0b111)
            check_type(argname="argument resource_property", value=resource_property, expected_type=type_hints["resource_property"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if resource_property is not None:
            self._values["resource_property"] = resource_property

    @builtins.property
    def resource_property(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourcesResourceProperty"]]]:
        '''resource_property block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/hashicorp/aws/5.44.0/docs/data-sources/resourceexplorer2_search#resource_property DataAwsResourceexplorer2Search#resource_property}
        '''
        result = self._values.get("resource_property")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourcesResourceProperty"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourceexplorer2SearchResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsResourceexplorer2SearchResourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d90f23e935f48c528fb7c1fe82eb88b62c86a77a049097e6799281ba41f7177)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsResourceexplorer2SearchResourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9151e313484b4ba631345c3714f904cfd3343028e872f43e80ec8a2ff02b70c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsResourceexplorer2SearchResourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d993712d5346b5c931140eac5c123f1dcbc155f130c97819ec25a1d5057d7764)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d1f31d1a955817f6f3c190fd4c0cae8a7742723b548960c4e2b4e24a8f04496)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b77a3e791e8599a024f8c362accd777412f0145cbe5b1c7ac28b4126e83361cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6ba65f1d4b1b1ac1d85739e039f0bb197710adaa0b3f04d712f44c688ca987f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsResourceexplorer2SearchResourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__faca619c5cebb2ec767747632da678e4293ea1ec922de5ac9332dc113cd6a6ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putResourceProperty")
    def put_resource_property(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataAwsResourceexplorer2SearchResourcesResourceProperty", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0c843d2d696012406b282d4dd7b483baa3f6d6a67889a543c202f4d849d044b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putResourceProperty", [value]))

    @jsii.member(jsii_name="resetResourceProperty")
    def reset_resource_property(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceProperty", []))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property
    @jsii.member(jsii_name="lastReportedAt")
    def last_reported_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastReportedAt"))

    @builtins.property
    @jsii.member(jsii_name="owningAccountId")
    def owning_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "owningAccountId"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="resourceProperty")
    def resource_property(
        self,
    ) -> "DataAwsResourceexplorer2SearchResourcesResourcePropertyList":
        return typing.cast("DataAwsResourceexplorer2SearchResourcesResourcePropertyList", jsii.get(self, "resourceProperty"))

    @builtins.property
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceType"))

    @builtins.property
    @jsii.member(jsii_name="service")
    def service(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "service"))

    @builtins.property
    @jsii.member(jsii_name="resourcePropertyInput")
    def resource_property_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourcesResourceProperty"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataAwsResourceexplorer2SearchResourcesResourceProperty"]]], jsii.get(self, "resourcePropertyInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e42ab08713b9e08e8ca6c517c8c10b691d9d504dc4fcf28c31513580394833c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourcesResourceProperty",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataAwsResourceexplorer2SearchResourcesResourceProperty:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataAwsResourceexplorer2SearchResourcesResourceProperty(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataAwsResourceexplorer2SearchResourcesResourcePropertyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourcesResourcePropertyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1af872da2405af95f406d2cae102325765d55f5dfe7e042d2540069f5a37cd92)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataAwsResourceexplorer2SearchResourcesResourcePropertyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b9a93e149316cb28fa917b0961cef35bd039d1389711a757f68511e0f242b85)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataAwsResourceexplorer2SearchResourcesResourcePropertyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dec93c144598201f767a0f92895c6759fe9d0f4afbcdcf53561f8fd206d7488f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__207cc6b493de3878aba19fcffad5f77b2fbdb0f8b33b31aafc5e59d9c247e842)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9676a83c318ba22fb31c6d19395ff052afad190595750085ea05e6051239daef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourcesResourceProperty]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourcesResourceProperty]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourcesResourceProperty]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5aea23085b7bc48205a72549ed56da471f6531f46efc5756258b9f61d3f8cf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class DataAwsResourceexplorer2SearchResourcesResourcePropertyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.dataAwsResourceexplorer2Search.DataAwsResourceexplorer2SearchResourcesResourcePropertyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b22fa65b50917f30c8b546662701e2ecad85a7973eb6e32dc62a47b264016fa1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @builtins.property
    @jsii.member(jsii_name="lastReportedAt")
    def last_reported_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastReportedAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourcesResourceProperty]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourcesResourceProperty]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourcesResourceProperty]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f43d71caaaefd0b3462f0a14c8b20dd338e477f9c2eb3f7c31dd4cef171871)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "DataAwsResourceexplorer2Search",
    "DataAwsResourceexplorer2SearchConfig",
    "DataAwsResourceexplorer2SearchResourceCount",
    "DataAwsResourceexplorer2SearchResourceCountList",
    "DataAwsResourceexplorer2SearchResourceCountOutputReference",
    "DataAwsResourceexplorer2SearchResources",
    "DataAwsResourceexplorer2SearchResourcesList",
    "DataAwsResourceexplorer2SearchResourcesOutputReference",
    "DataAwsResourceexplorer2SearchResourcesResourceProperty",
    "DataAwsResourceexplorer2SearchResourcesResourcePropertyList",
    "DataAwsResourceexplorer2SearchResourcesResourcePropertyOutputReference",
]

publication.publish()

def _typecheckingstub__a7ea22b46e9faaa1316bce00eb2f4e6075ca34e7109d2050850bf2f759cb3a84(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    query_string: builtins.str,
    resource_count: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResourceCount, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResources, typing.Dict[builtins.str, typing.Any]]]]] = None,
    view_arn: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__1e1967ec0634e8628bab0703e00f1ec8da11192fa52cb83b152b8f8859905c6a(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__573bdca33f8dfa4d2cf002f228c7e2df65f999f7c130a9586651cc75d7625ed6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResourceCount, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__868ba4f3dd1fbbb1c9e1d77a85bf0b485512c824fce493d11e6b32895cd269bd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a82a5c2b8e6b1cf0333aca4d22311c7a5c24bb12d36137caf8473995ebb9344(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66993de8d6e66c029eb055df431c801fca54b466bc58cad331ec7bb45ecc10bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01e12b722c5c6d6976a7eaf20b2bb2cbab77ac851819352ea6295cfc6e22705e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    query_string: builtins.str,
    resource_count: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResourceCount, typing.Dict[builtins.str, typing.Any]]]]] = None,
    resources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResources, typing.Dict[builtins.str, typing.Any]]]]] = None,
    view_arn: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf574af5a1a9aa39fa133a7d29bee2d2987c39b33305d4e4cee2ba33aa0315ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aec893d8eb70aa81af1488a2a476577642264929c9eaa061a6effa74bc5efee1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__176f2678defd7c5f1cefde186e77a1b67fef195ad88708823b9d68d9af19b7d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__261f2c83fa6cf29d57743a321389cfb36d38a5bba0016dfabdc84dae4cbd3385(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5fdb01a4fb783b853efb968d328287238a5967f8ae71de645a5bcfa20a8479a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b43bab2df4a5561928546a436a906ade2738142cb84fa9071778cc735c2bba4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourceCount]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc5ae702c23fd0c6e5c24b2e047523385476e5ab8b74618115caa2061db19b52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf52ad66d2d211b01083fe37663c149eced9e6aa0af894e4036fa299cdf1dfa5(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourceCount]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4081446d5acb4d8bcc50c2de6bbf521aec41936c2aae26e4ebb77cabf0b111(
    *,
    resource_property: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResourcesResourceProperty, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d90f23e935f48c528fb7c1fe82eb88b62c86a77a049097e6799281ba41f7177(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9151e313484b4ba631345c3714f904cfd3343028e872f43e80ec8a2ff02b70c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d993712d5346b5c931140eac5c123f1dcbc155f130c97819ec25a1d5057d7764(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1f31d1a955817f6f3c190fd4c0cae8a7742723b548960c4e2b4e24a8f04496(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b77a3e791e8599a024f8c362accd777412f0145cbe5b1c7ac28b4126e83361cb(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6ba65f1d4b1b1ac1d85739e039f0bb197710adaa0b3f04d712f44c688ca987f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faca619c5cebb2ec767747632da678e4293ea1ec922de5ac9332dc113cd6a6ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0c843d2d696012406b282d4dd7b483baa3f6d6a67889a543c202f4d849d044b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataAwsResourceexplorer2SearchResourcesResourceProperty, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e42ab08713b9e08e8ca6c517c8c10b691d9d504dc4fcf28c31513580394833c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af872da2405af95f406d2cae102325765d55f5dfe7e042d2540069f5a37cd92(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b9a93e149316cb28fa917b0961cef35bd039d1389711a757f68511e0f242b85(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dec93c144598201f767a0f92895c6759fe9d0f4afbcdcf53561f8fd206d7488f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__207cc6b493de3878aba19fcffad5f77b2fbdb0f8b33b31aafc5e59d9c247e842(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9676a83c318ba22fb31c6d19395ff052afad190595750085ea05e6051239daef(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5aea23085b7bc48205a72549ed56da471f6531f46efc5756258b9f61d3f8cf2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataAwsResourceexplorer2SearchResourcesResourceProperty]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b22fa65b50917f30c8b546662701e2ecad85a7973eb6e32dc62a47b264016fa1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f43d71caaaefd0b3462f0a14c8b20dd338e477f9c2eb3f7c31dd4cef171871(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataAwsResourceexplorer2SearchResourcesResourceProperty]],
) -> None:
    """Type checking stubs"""
    pass
