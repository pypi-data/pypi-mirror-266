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

import aws_cdk._jsii
import constructs._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "cdk-internal-gateway",
    "1.4.9",
    __name__[0:-6],
    "cdk-internal-gateway@1.4.9.jsii.tgz",
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
