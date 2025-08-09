# Concern Oriented MicroService Architecture
COMSA (Concern Oriented MicroService Architecture) is an Architecture Description Language aiming at representing the architecture of microservice applications.  

Its original proposition is to represent microservice applications not as a list of microservices but through architectural structures represented as constructions in the language.  

Those constructions can be of different nature ranging from design patterns to restart policies or naming patterns. Any relevant architectural structure can be expressed through the `Concern` keyword with the most common being already implemented in the language and ready to use.  

COMSA can be used as a deployment language as it is proposed with an associated toolbox among which compilers targeting Compose and Kubernetes.  

The aim is to drastically reduce redundancy and increase understandability of the application compared to other deployment languages.

## Table of Contents

- [Motivating Example](#Motivating_Example)
  - [Teastore Application: Compose](#teastore-application-compose)
  - [Teastore Application: COMSA](#teastore-application-comsa)
- [Syntax](#Syntax)
  - [File Schema](#file-schema)
  - [Concern Keyword](#concern-keyword)
- [Library of Concerns](#library-of-concerns)
- [Toolbox](#Toolbox)
  - [Installation](#Installation)
  - [Compilers](#Compilers)
  - [Visualization](#Visualization)
  - [Analysis](#Analysis)
- [Dataset](#Dataset)
- [Documentation](#Documentation)
- [References](#References)

## Motivating Example

### Teastore application: Compose

The [Teastore microservice application][teastore-github] topology can be represented through the following graph:  
![Teastore topology](.readme_resources/teastore_complete.png)
  
Patterns can be assumed from the names of the microservices and the links represented in the image. However this image documentation is not a necessity and the application architecture is hardly understandable from its Compose description:  

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

### Teastore Application: COMSA

COMSA proposes to have the architecture at the frontend of the description so that it's understandable at first glance:

```pkl
extends "modulepath:/comsa.pkl"

const DB_PORT = "3306"
const REGISTRY_PORT = "8080"
const BusinessServices = Set("persistence", "auth", "image", "recommender", "webui")

version = "3"
concerns {

  ["WebUI"]
    = new ApiGatewayPattern {
        msid = "webui"
        sids = Set("persistence", "auth", "image", "recommender")
      }

  ["Registry"]
    = new ServiceRegistryPattern {
        msid = "registry"
        sids = BusinessServices
        service_template {
          environment {
            ["REGISTRY_HOST"] = msid
            ["REGISTRY_PORT"] = REGISTRY_PORT
            ["HOST_NAME"] = "{SID}"
          }
        }
        services {
          [BusinessServices + Set("registry")] {
            expose {
              REGISTRY_PORT
            }
          }
        }
      }

  ["Database Per Service Pattern"]
    = new DatabasePerServicePattern {
        msid = "db"
        main_service_template {
          expose {
            DB_PORT
          }
        }
        sid = "persistence"
        service {
          environment {
            ["DB_HOST"] = msid 
            ["DB_PORT"] = DB_PORT
          }
        }
      }

  ["Persistence"]
    = new SharedService {
        msid = "persistence"
        csids = Set("image", "recommender", "auth")
      }

  ["DescartesresearchTeastore Images"]
    = new ImageConcern {
        sids = BusinessServices + Set("registry", "db")
        image = "descartesresearch/teastore-{SID}"
    }

  ["Public Ports"]
    = new PublicPortsConcern {
        ports {
          ["webui"] { "REGISTRY_PORT:REGISTRY_PORT" }
          ["db"] { "DB_PORT:DB_PORT" }
        }
      }
}
```

Without going into the COMSA specific synta we can point out that the application structure is now explicit not only because of the custom identifiers of the structures but because of the classes used to define the application.  
Moreover the redundancy has disapeared from the application so when we modify a value we do it for all the related microservices instead of having to repeat the operation and risk to forget some or do some text replacement and possibly modify more than we wanted.  
Actually the description contains more than before as when compile to Compose, implicit properties implied by the patterns will be injected.  

## Syntax
The COMSA language is based on [Pkl][pkl-website]. Even though COMSA is meant to be used declaratively, all of [Pkl language features](https://pkl-lang.org/main/current/language-reference/index.html) (ex: functions) and [Pkl standard library](https://pkl-lang.org/package-docs/pkl/0.29.0/) can be used in COMSA descriptions.

### File Schema

A `.comsa` file describing a microservice application has the following schema:

```pkl
extends "modulepath:/comsa.pkl"

concerns {
// Concerns are defined here
}

services {
// services with properties not included in a concern can be defined here
}
```

### Concern Keyword
A Concern is a object linking sets of services with sets of properties. The following presents a COMSA file with one concern, named `MyConcern`, assigning, by declaring relation in the concern `services` section, a common image to `service1` and `service2`, a different image to `service3` and setting the `container_name` value with a function concatenating the string `"container_"` and the service identifier, referred to by using the keyword `module.SID`.

```pkl
extends "modulepath:/comsa.pkl"

concerns {
  ["MyConcern"]
  = new Concern {
    services {
  
      [Set("service1", "service2")] {
        image = "image_of_service_1_and_2"
      }
  
      [Set("service3")] {
        image = "image_of_service_3"
      }
  
      [Set("service1", "service2", "service3")] {
        container_name = "container_" + module.SID
      }
  
    }
  }
}
```

Services are declared simply by being part of a `Concern` object, they do not need to be referenced elsewhere to exist.  
Each relation between a set of services and a set of properties define partially the contained services that can appear in any number of `Concern` objects. The service total definition is the aggregation of all its associated properties in the file which is done by to [compilers](#Compilers) when producing a deployable Compose or Kubernetes file.  

Using the `comsa2compose-yaml` tool presented in the [Compilers](#Compilers) section we obtain the following file which is immediately deployable using Docker-Compose.

```yaml
services:
  service1:
    container_name: service1
    image: image_of_service_1_and_2
  service2:
    container_name: service2
    image: image_of_service_1_and_2
  service3:
    container_name: service3
    image: image_of_service_3
```

We have successfully removed some redundancy but to operate the separation of concerns a better `.comsa` file would be:  

```pkl
extends "modulepath:/comsa.pkl"

concerns {
  ["ImageConcern"]
  = new Concern {
    services {
      [Set("service1", "service2")] {
        image = "image_of_service_1_and_2"
      }
      [Set("service3")] {
        image = "image_of_service_3"
      }
    }

  ["ContainerNameConcern"]
    = new Concern {
      services {
        [Set("service1", "service2", "service3")] {
          container_name = module.SID
        }
      }
    }
  }
}
```

Here the different Concerns of the application are properly distinguished, the shared properties are effectively unified thus leaving no redundancy and not necessitating multiple edits on modification.  

## Library of Concerns

## Toolbox
###Installation
##Tools
###Compilers
###Visualization
###Analysis

## Dataset

## Documentation

## References
[teastore-github]: https://github.com/DescartesResearch/TeaStore
[pkl-website]: https://pkl-lang.org/
