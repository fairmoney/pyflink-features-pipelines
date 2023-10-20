# pyflink-features-pipelines
A set of Python Flink pipelines to enable real time and batch computation of features for ML models.


## High level design
This project follows the [Polylith](https://polylith.gitbook.io/polylith/) architecture. It is highly recommended to 
spend decent amount of time reading documentation about it and understanding it.
The community has developed nice tooling to enable efficient implementation of this architecture in Python projects.
You can read more about it [here](https://davidvujic.github.io/python-polylith-docs/).

The choice of using polylith architecture has been made for the below reasons:
- the structure of a Flink pipeline can be highly modular, mixing different bricks to achieve implementation of 
business logics
- a lot of reusable components will be referenced in each pipeline: source connectors, schemas, 
serialization / deserialization logic, sink connectors, etc...
- some high level data transformations can also be re-used across different pipelines, or even deployed as standalone
pipelines. Example: 3 different ML features pipelines need to join data between `stream_A` and `stream_B` in the same manner,
then it could be a good idea to deploy a pipeline performing this join and emitting results into a dedicated `stream_A_B`.
Then the computation intensive operation of performing the join is done once, and downstream pipelines can directly 
read `stream_A_B`. The polylith architecture allows to easily start by defining the join operation in all 3 pipelines,
and refactor this transformation in a dedicated deployed pipeline when cleaning up technical debt occurs - with very 
minimal code changes.
- The developer experience is improved compared to exporting common code into dedicated libraries. Data Scientists enjoy the
developer experience of monolithic architectures - the polylith architecture allows to enjoy this developer experience,
combined with the flexibility of deploying multiple pipelines that reference just the right amount of code.

This project is designed to allow collaboration between different data teams:
- DataTech provides tools to abstract away the IO operations, serialization / deserialization, deployment
- Business facing data team members (Data Scientists, BI Engineers) implement business logics

All pipelines implemented in this repo will be running with the [Apache Flink](https://flink.apache.org/) distributed 
data processing framework. It is highly recommended that the user takes the proper time to get familiar with
the essential concepts of a distributed streaming data processing application. The goal is that the users of this repo
gradually become autonomous on building their own processing pipelines, keeping in mind costs and performance considerations.
Flink allows to build pretty much anything, but if not designed carefully, pipelines can quickly become expensive and 
complicated to maintain. To start with, the user could read through the below documentations:
- [Streaming Analytics](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/learn-flink/streaming_analytics/) - especially the importance of understanding that dealing with streaming data implies making compromise between latency and completeness.
- [Learn Flink](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/learn-flink/overview/) - a General overview of how Flink works and how work is distributed across the cluster.
- [Stateful Stream Processing](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/concepts/stateful-stream-processing/) - a vast majority of ML feature pipelines are stateful, it's a good idea to understand this one! 
Building stateful applications is not an easy thing but Flink provides very nice and rich features to enable any sort of stateful computation. When designing stateful pipelines, attention should be paid on choosing the correct structure for the state, because it has direct implications on performance and costs.
- [Timely stream processing](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/concepts/time/) - an essential high level view of why it is important to correctly define event times and the trade-offs to be made between latency and completeness.
- [Python Flink Api](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/python/overview/) - the official documentation on Flink Python api:
  - The [DataStream api](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/python/datastream/intro_to_datastream_api/): low level functional way of defining pipelines.
  - The [Table / SQL api](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/python/table/intro_to_table_api/): high level, SQL-style way to define pipelines.
  - NB: 
    - it's easy in Flink to mix and match both APIs, as they can interact within the same job. In this repo, we'll make use of both.
    - Flink is a JVM based framework, the Python API is just a layer on top of the Java / Scala API. Hence its documentation might 
not be as detailed as the Java / Scala one, so you can still refer to [DataStream API](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/overview/) 
and [Table/SQL](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/table/overview/) API for deeper look. [Joining](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/operators/joining/) and [Windows](https://nightlies.apache.org/flink/flink-docs-release-1.17/docs/dev/datastream/operators/windows/) are very useful examples.


## Quickstart

### Installation and set up

#### Dependencies
In order to be able to contribute to this project, you need to have:
- Python 3.9 or higher
- Java 8 or higher
- Python Poetry plugin. All current workflows at FairMoney are using Poetry version 1.4.2. Installation instructions:
```shell
curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.2 python3 -
```
- Poetry plugins: `poetry-multiproject-plugin` and `poetry-polylith-plugin`. Installation instructions [here](https://davidvujic.github.io/python-polylith-docs/installation/).
- Docker and Docker compose. For Mac users, Docker Desktop is recommended.
- [Direnv](https://direnv.net/)

#### Installation
Fetch some external jars needed by the Flink runtime to perform some of the operations:
```shell
source ./scripts.sh
get_jars
```

Once all the dependencies have been installed, run:
```shell
poetry install
```
This will install the current repo and create all necessary virtual environments. You're ready to develop new pipelines!

Run tests:
```shell
export JAVA_HOME=xxx  # your java installation folder
poetry run pytest test --pspec -p no:warnings
```
 
### Polylith usage
You will make use of the `poly` command to manage your polylith repo. Some utils have been made available in `.envrc` file. Run ```direnv allow .``` to enable them.
The Polylith architecture is based on the principle that applications are composed of reusable bricks. So don't be shy, and define as many bricks as possible!
Adding a new component / base:
```shell
# First, create your component|brick:
poly create {component|base} --name my_cool_brick --description "Some description for my cool brick"

# Then sync your top level poetry config, to have your new brick available in the development environment:
poly sync
```

Run ```poly info``` to visualise the structure of the Polylith and the interactions between [bases](./bases), [components](./components) and [projects](./projects).
Check the different [commands](https://davidvujic.github.io/python-polylith-docs/commands/) available with the Poetry Polylith plugin.

### Development workflow
The Polylith architecture allows for quick iteration, via ad-hoc scripts in the [development](./development) folder. You can easily write your pipeline here, then gradually
break it down into bases and components.
As a starter, you can check the different examples of stateless and stateful pipelines, in the [sample_flink_transformations](./bases/pfp/sample_flink_transformations) base.


## Next steps
2023-10-20: 
- This is a very first version of the repo, far from being finished. No project has yet been implemented, Datatech will work on it to deploy pipelines on 
either AWS Managed Flink, or Kubernetes
- Datatech will also work on all the abstractions + design documents that will enable end users to focus only on business logics implementation
- The structure of the bricks will evolve a lot in the short term, when utilities will be added gradually. We'll learn 
the power of Polylith architecture by trying! The target is to be able to deliver all feature computation pipelines 
needed 1 month post IOS MVP release.