# Komodo Package

This is Komodo SDK package.

## Package hierarchy

- komodo/server: FastApi server for the Komodo Appliances
- komodo/models: Implementation of LLM model access and runners to get responses.
-
- komodo/loaders: Loaders for komodo classes and objects.
- komodo/core: Implementation of komodo agents, tools, data sources and other core components.
- komodo/framework: KomodoApp, KomodoAgents, KomodoTool that form the Komodo AI platform.
-
- komodo/shared: Shared utilities and classes used by other komodo packages.
- komodo/data:  Folder for all data files for testing purposes

- komodo/store: Layer that stores and load proto objects from redis database.
- komodo/proto: Protobuf files that define the basic data structures and services.

## Programming Principles

1. Do not use global variables or settings. They are hard to navigate and debug and change.
2. Use dependency injection to pass the settings and other objects to the classes and functions.
3. Pass in the paths, urls, connection strings, and other settings as arguments to the classes and functions.
