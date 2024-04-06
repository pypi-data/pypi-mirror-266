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
import cdk8s._jsii
import constructs._jsii

__jsii_assembly__ = jsii.JSIIAssembly.load(
    "@cdk8s/awscdk-resolver",
    "0.0.77",
    __name__[0:-6],
    "awscdk-resolver@0.0.77.jsii.tgz",
)

__all__ = [
    "__jsii_assembly__",
]

publication.publish()
