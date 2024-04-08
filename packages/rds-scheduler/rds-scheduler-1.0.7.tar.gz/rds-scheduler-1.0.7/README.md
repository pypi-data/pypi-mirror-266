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
