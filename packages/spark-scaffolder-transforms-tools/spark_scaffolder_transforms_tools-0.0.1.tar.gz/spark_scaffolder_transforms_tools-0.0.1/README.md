# spark_scaffolder_transforms_tools


[![Github License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Updates](https://pyup.io/repos/github/woctezuma/google-colab-transfer/shield.svg)](pyup)
[![Python 3](https://pyup.io/repos/github/woctezuma/google-colab-transfer/python-3-shield.svg)](pyup)
[![Code coverage](https://codecov.io/gh/woctezuma/google-colab-transfer/branch/master/graph/badge.svg)](codecov)




spark_scaffolder_transforms_tools is a Python library that implements transforms Kirby3x
## Installation

> The code is packaged for PyPI, so that the installation consists in running:

```sh
pip install spark-scaffolder-transforms-tools --upgrade
```


## Usage


## CacheTransformation (type = "cache")

example:
```hocon
    {
        type = "cache"
        inputs = ["input1", "input2"]
    }
```

## UnpersistTransformation (type = "unpersist")
example:

```hocon
    {
        type = "unpersist"
        inputs = ["input1", "input2"]
    }
```

## InitalizeNullsTransformation (type = "initialize-nulls")
Permite inicializar valores *null* en las columnas indicadas con un valor por defecto.

Su configuración se ajusta a los siguientes parámetros:


|    Parámetro    | Descripción                                                |      Tipo       |          Obligatoria          |
|:---------------:|:-----------------------------------------------------------|:---------------:|:-----------------------------:|
|    **field**    | nombre de columna donde se buscan valores *null*           |     string      | SI, excluyente con **fields** |
|   **fields**    | lista de nombres de columna donde se buscan valores *null* | lista de string | SI, excluyente con **field**  |
|   **default**   | configuración de la lógica de datos                        |     string      |              SI               |

Ejemplos de uso:

```hocon
    {
        type = "initialize-nulls"
        field = "col1"
        default = "value1"
    }
```

```hocon
    {
        type = "initialize-nulls"
        fields = ["col1","col2","col3"]
        default = "value"
    }
```

## JoinTransformation (type = "join")
Realiza operaciones tipo *join* sobre multiples dataframes:

Su configuración se ajusta a los siguientes parámetros:

|    Parámetro    | Descripción                                                                                         |      Tipo       | Obligatoria |
|:---------------:|:----------------------------------------------------------------------------------------------------|:---------------:|:-----------:|
|  **joinType**   | indica el tipo de join                                                                              |     string      |     SI      |
|   **inputs**    | lista de nombres de **input**, al menos deben tener dos elementos                                   | lista de string |     SI      |
| **joinColumns** | lista de configs, donde se relacion cada **input** con la lista de columnas para realizar el *join* | lista de config |     SI      |
|   **output**    | nombre del **output** asociado al resultado del *join*                                              |     string      |     SI      |

Ejemplo de uso, en este caso realiza un join de tipo *leftanti* sobre dos dataframes asociados a *t_users* y
*t_people* por medio de las columnas *id2* e *id* respectivamente, el resultado del join se asigna al output *t_users_people*:

```hocon
    {
        type = "join"
        inputs = ["t_users", "t_people"]
        joinType = "leftanti"
        joinColumns = [
            { 
                "t_users" = ["id2"] 
            },
            { 
                "t_people" = ["id"] 
            }
        ]
        output = "t_users_people"
    }
```

**Atención**: Si se desea utilizar la transformación type = "join" nativa Kirby, esta debe registrar en los ficheros *Shifu*
mediante **type = "kirby-join"**

## PipelineTransformation (type = "pipeline")
Aplica un *pipeline* de transformaciones a uno o varios **inputs**, permitiendo asi ficheros de configuración más simples

Su configuración se ajusta a los siguientes parámetros:


|  Parámetro   | Descripción                                  |      Tipo       | Obligatoria |
|:------------:|:---------------------------------------------|:---------------:|:-----------:|
| **pipeline** | lista de configuraciones de transformaciones | lista de config |     SI      |

Ejemplos de uso:

```hocon
    {
        type = "pipe"
        inputs = ["t_users","t_people"]
        pipeline = [
            {
                type = "literal"
                field = "status"
                default = "registered"
                defaultType = "string"
            },
            {
                type = "filter"
                filters = [
                    {
                        field = "gf_odate_date"
                        op = "eq"
                        value = "20210110"
                    }
                ]
            }
        ]
    }
```

## UnionTransformation (type = "union")
Aplica una operación *union* entre multiples **inputs**, es condición que los **inputs** deban tener el mismo esquema
o la operación fallará

Su configuración se ajusta a los siguientes parámetros:


| Parámetro  | Descripción                                               |      Tipo       | Obligatoria |
|:----------:|:----------------------------------------------------------|:---------------:|:-----------:|
| **inputs** | lista de **inputs** que se van a unir                     | lista de string |     SI      |
| **output** | nombre del **output** asociado al resultado de la *union* |     string      |     SI      |

Ejemplos de uso:

```hocon
    {
        type = "union"
        inputs = ["t_users_es","t_users_mx"]
        output = "t_users"
    }
```


## License

[Apache License 2.0](https://www.dropbox.com/s/8t6xtgk06o3ij61/LICENSE?dl=0).


## New features v1.0

 
## BugFix
- choco install visualcpp-build-tools



## Reference

 - Jonathan Quiza [github](https://github.com/jonaqp).
 - Jonathan Quiza [RumiMLSpark](http://rumi-ml.herokuapp.com/).
 - Jonathan Quiza [linkedin](https://www.linkedin.com/in/jonaqp/).
