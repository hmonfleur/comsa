# Concern Oriented MicroService Architecture
COMSA (Concern Oriented MicroService Architecture) is an Architecture Description Language aiming at representing the architecture of microservice applications.  

Its original proposition is to represent microservice applications not as a list of microservices but through architectural structures represented as constructions in the language.  

Those constructions can be of different nature ranging from design patterns to restart policies or naming patterns. Any relevant architectural structure can be expressed through the `Concern` keyword with the most common being already implemented in the language and ready to use.  

COMSA can be used as a deployment language as it is proposed with an associated toolbox among which compilers targeting Compose and Kubernetes.  

The aim is to drastically reduce redundancy and increase understandability of the application compared to other deployment languages.

## Table of Contents

- [Motivating Example](#Motivating_Example)
  - Teastore Application: Compose(#teastore-application-compose)
- [Installation and Toolbox](#installation-and-toolbox)
- [Dataset](#Dataset)
- [Syntax](#Syntax)
- [Library of Concerns](#library-of-concern)
- [Documentation](#Documentation)
- [References](#References)

## Motivating Example

### Teastore application: Compose

The [Teastore microservice application][teastore-github] topology can be represented through the following graph:  
![Teastore topology](.readme_resources/teastore_complete.png)
  
Patterns can be assumed from the names of the microservices and the links represented in the image. Howevers this image documentation is not always aviable and the application architecture is hardly understandable from its Compose description:  

```yaml
version: '3'
services:
  registry:
    image: descartesresearch/teastore-registry
    expose:
      - "8080"
  db:
    image: descartesresearch/teastore-db
    expose:
      - "3306"
    ports:
      - "3306:3306"
  persistence:
    image: descartesresearch/teastore-persistence
    expose:
      - "8080"
    environment:
      HOST_NAME: "persistence"
      REGISTRY_HOST: "registry"
      DB_HOST: "db"
      DB_PORT: "3306"
  auth:
    image: descartesresearch/teastore-auth
    expose:
      - "8080"
    environment:
      HOST_NAME: "auth"
      REGISTRY_HOST: "registry"
  image:
    image: descartesresearch/teastore-image
    expose:
      - "8080"
    environment:
      HOST_NAME: "image"
      REGISTRY_HOST: "registry"
  recommender:
    image: descartesresearch/teastore-recommender
    expose:
      - "8080"
    environment:
      HOST_NAME: "recommender"
      REGISTRY_HOST: "registry"
  webui:
    image: descartesresearch/teastore-webui
    expose:
      - "8080"
    environment:
      HOST_NAME: "webui"
      REGISTRY_HOST: "registry"
    ports:
      - "8080:8080"
```


## Installation and Toolbox

## Dataset

## Syntax

## Library of Concerns

## Documentation

## References
[teastore-github]: https://github.com/DescartesResearch/TeaStore
