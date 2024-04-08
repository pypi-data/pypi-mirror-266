'''
# CDK RDS Scheduler Construct

[![View on Construct Hub](https://constructs.dev/badge?package=cdk-rds-scheduler)](https://constructs.dev/packages/cdk-rds-scheduler)

This is a CDK construct for creating a schedule to periodically start and stop RDS (Aurora) clusters or instances.
It can be used to reduce billing outside of operational hours.

![Architecture](./image/architecture.png)

[![Open in Visual Studio Code](https://img.shields.io/static/v1?logo=visualstudiocode&label=&message=Open%20in%20Visual%20Studio%20Code&labelColor=2c2c32&color=007acc&logoColor=007acc)](https://open.vscode.dev/badmintoncryer/cdk-rds-scheduler)
[![npm version](https://badge.fury.io/js/cdk-rds-scheduler.svg)](https://badge.fury.io/js/cdk-rds-scheduler)
[![Build Status](https://github.com/badmintoncryer/cdk-rds-scheduler/actions/workflows/build.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-scheduler/actions/workflows/build.yml)
[![Release Status](https://github.com/badmintoncryer/cdk-rds-scheduler/actions/workflows/release.yml/badge.svg)](https://github.com/badmintoncryer/cdk-rds-scheduler/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![npm downloads](https://img.shields.io/npm/dm/cdk-rds-scheduler.svg?style=flat)](https://www.npmjs.com/package/cdk-rds-scheduler)

## Usage

Install it via npm:

```bash
npm install cdk-rds-scheduler
```

Then use it in your CDK stack:

```python
import { RdsScheduler, Cron } from 'cdk-rds-scheduler';
import { TimeZone } from 'aws-cdk-lib/core';

// for DatabaseCluster
declare const databaseCluster: rds.DatabaseCluster;

new RdsScheduler(this, 'RdsClusterScheduler', {
  cluster: databaseCluster,
  schedule: [
    // Operate only during daytime on weekdays
    {
      start: new Cron({ minute: '0', hour: '8', day: '?', weekDay: 'MON-FRI' }),
      stop: new Cron({ minute: '0', hour: '18', day: '?', weekDay: 'MON-FRI' }),
      timeZone: TimeZone.ASIA_TOKYO,
    },
  ],
});

// for DatabaseInstance
declare const databaseInstance: rds.DatabaseInstance;

new RdsScheduler(this, 'RdsInstanceScheduler', {
  instance: databaseInstance,
  schedule: [
    // Put the instance into a dormant state.
    // As a measure for automatic start of Aurora, stop it every day.
    {
      stop: new Cron({ minute: '0', hour: '0', day: '?' }),
      // timeZone is optional, default is UTC
    },
  ],
});
```
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

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import constructs as _constructs_77d1e7e8


class Cron(metaclass=jsii.JSIIMeta, jsii_type="cdk-rds-scheduler.Cron"):
    def __init__(
        self,
        *,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a cron expression.

        :param day: The day of the month to run this rule at. Default: - Every day of the month
        :param hour: The hour to run this rule at. Default: - Every hour
        :param minute: The minute to run this rule at. Default: - Every minute
        :param month: The month to run this rule at. Default: - Every month
        :param week_day: The day of the week to run this rule at. Default: - Any day of the week
        :param year: The year to run this rule at. Default: - Every year
        '''
        options = CronOptions(
            day=day,
            hour=hour,
            minute=minute,
            month=month,
            week_day=week_day,
            year=year,
        )

        jsii.create(self.__class__, self, [options])

    @jsii.member(jsii_name="toString")
    def to_string(self) -> builtins.str:
        '''Return the cron expression.'''
        return typing.cast(builtins.str, jsii.invoke(self, "toString", []))


@jsii.data_type(
    jsii_type="cdk-rds-scheduler.CronOptions",
    jsii_struct_bases=[],
    name_mapping={
        "day": "day",
        "hour": "hour",
        "minute": "minute",
        "month": "month",
        "week_day": "weekDay",
        "year": "year",
    },
)
class CronOptions:
    def __init__(
        self,
        *,
        day: typing.Optional[builtins.str] = None,
        hour: typing.Optional[builtins.str] = None,
        minute: typing.Optional[builtins.str] = None,
        month: typing.Optional[builtins.str] = None,
        week_day: typing.Optional[builtins.str] = None,
        year: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Options to configure a cron expression.

        All fields are strings so you can use complex expressions. Absence of
        a field implies '*' or '?', whichever one is appropriate.

        :param day: The day of the month to run this rule at. Default: - Every day of the month
        :param hour: The hour to run this rule at. Default: - Every hour
        :param minute: The minute to run this rule at. Default: - Every minute
        :param month: The month to run this rule at. Default: - Every month
        :param week_day: The day of the week to run this rule at. Default: - Any day of the week
        :param year: The year to run this rule at. Default: - Every year

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cron-expressions.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3461c1032436321a0219d817654c9ce8a178b1280b4eb7f7a46f960e3d675c66)
            check_type(argname="argument day", value=day, expected_type=type_hints["day"])
            check_type(argname="argument hour", value=hour, expected_type=type_hints["hour"])
            check_type(argname="argument minute", value=minute, expected_type=type_hints["minute"])
            check_type(argname="argument month", value=month, expected_type=type_hints["month"])
            check_type(argname="argument week_day", value=week_day, expected_type=type_hints["week_day"])
            check_type(argname="argument year", value=year, expected_type=type_hints["year"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if day is not None:
            self._values["day"] = day
        if hour is not None:
            self._values["hour"] = hour
        if minute is not None:
            self._values["minute"] = minute
        if month is not None:
            self._values["month"] = month
        if week_day is not None:
            self._values["week_day"] = week_day
        if year is not None:
            self._values["year"] = year

    @builtins.property
    def day(self) -> typing.Optional[builtins.str]:
        '''The day of the month to run this rule at.

        :default: - Every day of the month
        '''
        result = self._values.get("day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hour(self) -> typing.Optional[builtins.str]:
        '''The hour to run this rule at.

        :default: - Every hour
        '''
        result = self._values.get("hour")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def minute(self) -> typing.Optional[builtins.str]:
        '''The minute to run this rule at.

        :default: - Every minute
        '''
        result = self._values.get("minute")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def month(self) -> typing.Optional[builtins.str]:
        '''The month to run this rule at.

        :default: - Every month
        '''
        result = self._values.get("month")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def week_day(self) -> typing.Optional[builtins.str]:
        '''The day of the week to run this rule at.

        :default: - Any day of the week
        '''
        result = self._values.get("week_day")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def year(self) -> typing.Optional[builtins.str]:
        '''The year to run this rule at.

        :default: - Every year
        '''
        result = self._values.get("year")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CronOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RdsScheduler(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-rds-scheduler.RdsScheduler",
):
    '''A scheduler for RDS instances or clusters.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        schedule: typing.Sequence[typing.Union["Schedule", typing.Dict[builtins.str, typing.Any]]],
        cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
        instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param schedule: The schedule for starting and stopping the RDS instance or cluster.
        :param cluster: The RDS cluster to start and stop. If you specify a cluster, you cannot specify an instance. Default: - no cluster is specified and you must specify an instance
        :param instance: The RDS instance to start and stop. If you specify an instance, you cannot specify a cluster. Default: - no instance is specified and you must specify a cluster
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f614cce21132174d064340e92d2aae06833a0c8909806218b6600200f83c0ce5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = RdsSchedulerProps(
            schedule=schedule, cluster=cluster, instance=instance
        )

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdk-rds-scheduler.RdsSchedulerProps",
    jsii_struct_bases=[],
    name_mapping={
        "schedule": "schedule",
        "cluster": "cluster",
        "instance": "instance",
    },
)
class RdsSchedulerProps:
    def __init__(
        self,
        *,
        schedule: typing.Sequence[typing.Union["Schedule", typing.Dict[builtins.str, typing.Any]]],
        cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
        instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
    ) -> None:
        '''Properties for the RdsScheduler.

        :param schedule: The schedule for starting and stopping the RDS instance or cluster.
        :param cluster: The RDS cluster to start and stop. If you specify a cluster, you cannot specify an instance. Default: - no cluster is specified and you must specify an instance
        :param instance: The RDS instance to start and stop. If you specify an instance, you cannot specify a cluster. Default: - no instance is specified and you must specify a cluster
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d18407cb1812b29a1bfb48871e5bb9431819f365c2151db43c9c91d2f425348)
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument instance", value=instance, expected_type=type_hints["instance"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "schedule": schedule,
        }
        if cluster is not None:
            self._values["cluster"] = cluster
        if instance is not None:
            self._values["instance"] = instance

    @builtins.property
    def schedule(self) -> typing.List["Schedule"]:
        '''The schedule for starting and stopping the RDS instance or cluster.'''
        result = self._values.get("schedule")
        assert result is not None, "Required property 'schedule' is missing"
        return typing.cast(typing.List["Schedule"], result)

    @builtins.property
    def cluster(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster]:
        '''The RDS cluster to start and stop.

        If you specify a cluster, you cannot specify an instance.

        :default: - no cluster is specified and you must specify an instance
        '''
        result = self._values.get("cluster")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster], result)

    @builtins.property
    def instance(self) -> typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance]:
        '''The RDS instance to start and stop.

        If you specify an instance, you cannot specify a cluster.

        :default: - no instance is specified and you must specify a cluster
        '''
        result = self._values.get("instance")
        return typing.cast(typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RdsSchedulerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-rds-scheduler.Schedule",
    jsii_struct_bases=[],
    name_mapping={"start": "start", "stop": "stop", "timezone": "timezone"},
)
class Schedule:
    def __init__(
        self,
        *,
        start: typing.Optional[Cron] = None,
        stop: typing.Optional[Cron] = None,
        timezone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
    ) -> None:
        '''
        :param start: The start schedule. Default: - no start schedule. The RDS instance or cluster will not be started automatically.
        :param stop: The stop schedule. Default: - no stop schedule. The RDS instance or cluster will not be stopped automatically.
        :param timezone: The timezone for the cron expression. Default: UTC
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbb57ffdf00e2e9705e7e71515c760bb5ef12327ac6c82b5b97c07bff94a7a2a)
            check_type(argname="argument start", value=start, expected_type=type_hints["start"])
            check_type(argname="argument stop", value=stop, expected_type=type_hints["stop"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if start is not None:
            self._values["start"] = start
        if stop is not None:
            self._values["stop"] = stop
        if timezone is not None:
            self._values["timezone"] = timezone

    @builtins.property
    def start(self) -> typing.Optional[Cron]:
        '''The start schedule.

        :default: - no start schedule. The RDS instance or cluster will not be started automatically.
        '''
        result = self._values.get("start")
        return typing.cast(typing.Optional[Cron], result)

    @builtins.property
    def stop(self) -> typing.Optional[Cron]:
        '''The stop schedule.

        :default: - no stop schedule. The RDS instance or cluster will not be stopped automatically.
        '''
        result = self._values.get("stop")
        return typing.cast(typing.Optional[Cron], result)

    @builtins.property
    def timezone(self) -> typing.Optional[_aws_cdk_ceddda9d.TimeZone]:
        '''The timezone for the cron expression.

        :default: UTC
        '''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.TimeZone], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Schedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Cron",
    "CronOptions",
    "RdsScheduler",
    "RdsSchedulerProps",
    "Schedule",
]

publication.publish()

def _typecheckingstub__3461c1032436321a0219d817654c9ce8a178b1280b4eb7f7a46f960e3d675c66(
    *,
    day: typing.Optional[builtins.str] = None,
    hour: typing.Optional[builtins.str] = None,
    minute: typing.Optional[builtins.str] = None,
    month: typing.Optional[builtins.str] = None,
    week_day: typing.Optional[builtins.str] = None,
    year: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f614cce21132174d064340e92d2aae06833a0c8909806218b6600200f83c0ce5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    schedule: typing.Sequence[typing.Union[Schedule, typing.Dict[builtins.str, typing.Any]]],
    cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
    instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d18407cb1812b29a1bfb48871e5bb9431819f365c2151db43c9c91d2f425348(
    *,
    schedule: typing.Sequence[typing.Union[Schedule, typing.Dict[builtins.str, typing.Any]]],
    cluster: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster] = None,
    instance: typing.Optional[_aws_cdk_aws_rds_ceddda9d.IDatabaseInstance] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbb57ffdf00e2e9705e7e71515c760bb5ef12327ac6c82b5b97c07bff94a7a2a(
    *,
    start: typing.Optional[Cron] = None,
    stop: typing.Optional[Cron] = None,
    timezone: typing.Optional[_aws_cdk_ceddda9d.TimeZone] = None,
) -> None:
    """Type checking stubs"""
    pass
