## Librería para la creación de tramas para Robot Framework

Esta librería de Robot Framework proporciona una serie de funciones para crear tramas a partir de datos proporcionados. La función principal de la librería es generar tramas en formato  hexadecimal con un checksum válido, facilitnando el envio de datos estructurados en proyectos de automatización.

## Requisitos

Antes de usar esta librería, asegurate de tener instalado lo siguuiente:
- Python > 3.8
- Robot Framework
- pip (para instalar libreria)

## Instalación
Puedes instalar esta librería a través de pip:
* ` pip install --upgrade robotframework-creartramas`

## Uso 

``` RobotFramework

 Aquí tienes un ejemplo de cómo crear una trama utilizando esta librería:

*** Settings ***
Library    mi_libreria_de_tramas.TRAMAS

*** Test Cases ***
Crear y enviar trama
    ${direccion_origen}=    Set Variable    0x01
    ${direccion_destino}=    Set Variable    0x02
    ${numero_bits}=    Set Variable    0x08
    ${comando}=    Set Variable    0xFE
    ${datos}=    Create List    0x41    0x5A    0x4B
    ¡¡DATOS ES UNA LISTA!!

    ${trama}=    Crear Trama    ${direccion_origen}    ${direccion_destino}    ${numero_bits}    ${comando}    ${datos}
    Log    Trama creada: ${trama}
```

## Funciones Disponibles

`calcular_checksum(trama)`

Esta función calcula el checksum de una trama en hexadecimal.

- `trama`: La trama en hexadecimal para la cual se calculará el checksum.


`crear_trama(direccion_origen, direccion_destino, numero_bits, comando, datos)`

Esta función construye una trama según la estructura proporcionada.
TODO EN FORMATO HEXADECIMAL: 0XAB   

- `direccion_origen`: La dirección de origen de la trama.
- `direccion_destino`: La dirección de destino de la trama.
- `numero_bits`: El número de datos enviados.
- `comando`: El comando a enviar.
- `datos`: Los datos a enviar, proporcionados COMO UNA LISTA


## Licencia
Este proyecto esta licenciado bajo la licencia Apache-2.0