# regmapGen

![regmapGen_logo](docs/img/logo.png)

[![Статус документации](https://readthedocs.org/projects/regmapGen/badge/?version=latest)](https://regmapGen.readthedocs.io/ru/latest/?badge=latest)
[![PyPI версия](https://badge.fury.io/py/regmapGen.svg)](https://badge.fury.io/py/regmapGen)


**regmapGen** - это инструмент, который упрощает создание и поддержку Регистровой Карты для любого проекта на языке описания аппаратуры (HDL). Он позволяет описать карту регистров в одном файле, а затем сгенерировать HDL код, Header файлы, документацию и другие элементы. Это позволяет эффективно устранять расхождения между различными аспектами разработки ИС - hardware, software и документацией, а также автоматизировать процесс разработки, верификации и переиспользования кода IP-блока.

![regmapGen_flow](docs/img/regmapGen_flow.png)

## Особенности

- Человеко-читаемые форматы ввода: JSON, YAML или простая текстовая таблица
- Генерация YAML файл с описанием регистров из Excel таблицы
- Генерация IP-XACT XML описания регистров из Excel таблицы
- Генерация HDL кода: SystemVerilog модуль с картой регистров, SystemVerilog header или SystemVerilog package с define-макросами или параметрами, соответственно
- Генерация UVM регистровой модели и окружения для верификации
- Поддержка нескольких протоколов: APB, AXI-Lite, Avalon-MM, SPI
- Генерация документации: Markdown, AsciiDoc, Docx
- Генерация  файлов, относящихся к software-части: C header, Python модуль
- Расширяемость: поддержка внешних генераторов
- API: cоздание пользовательского рабочего процесса с помощью API regmapGen

regmapGen документация доступна в [ReadTheDocs.io](https://regmapGen.readthedocs.io).

## Установка

В зависимости от вашей систем, исполняемый файл Python 3 может быть `python` или `python3`.
Если имеются ограничения с правами, можно использовать ключ `--user` при установке.

Для установки последней версии:

```sh
python3 -m pip install -U regmapGen
```

## Быстрый старт

Лучший способ быстро начать — создать шаблоны. Вы можете создать карту регистров в удобном для вас формате (выберите один из `json`, `yaml`, `txt`) :

```sh
regmapGen -t yaml
```

Сгенерируется два файла: один файл с описанием регистров в выбранном формате `regs.yaml`, и второй файл конфигурации - `config`.

Карта регистров состоит из набора регистров, отображенных в память (также называемых как Control and Status Regiser - CSR), а регистры в свою очередь состоят из битовых полей. Например, карта регистров одного регистра в YAML выглядит так:

```yaml
regmap:
-   name: CTRL
    description: Control register
    address: 8
    bitfields:
    -   name: BAUD
        description: Baudrate value
        reset: 0
        width: 2
        lsb: 0
        access: rw
        hardware: o
        enums:
        -   name: B9600
            description: 9600 baud
            value: 0
        -   name: B38400
            description: 38400 baud
            value: 1
        -   name: B115200
            description: 115200 baud
            value: 2
```

YAML файл также может быть сгенерирован из Excel таблица. Детали доступны в [примере](https://github.com/PaulMSV/regmapGen/example/excel).

Чтобы узнать больше о регистрах, битовых полях и их атрибутах, пожалуйста, ознакомьтесь с документацией на странице [Регистровая карта](https://regmapGen.readthedocs.io/en/latest/regmap.html).


regmapGen - это инструмент, ориентированный на файлы конфигурации. По умолчанию он использует ini-файл конфигурации под названием config. В этом файле указываются все необходимые параметры для генерации: входной файл карты регистров, глобальные параметры и выходной файл (таргет). Вот пример:

```ini
[globcfg]
data_width = 32
address_width = 16
register_reset = sync_pos

[sv_module]
path = regs.sv
interface = axil
generator = SystemVerilog

[c_header]
path = regs.h
generator = CHeader
```

Для получения более подробной информации о файле `config`, посмотрите страницу [Конфигурационный файл](https://regmapGen.readthedocs.io/en/latest/config.html), а для более общей информации о процессе ознакомтесь с разделом [Введение](https://regmapGen.readthedocs.io/en/latest/introduction.html).

`config` также действует как сценарий сборки для regmapGen, поэтому просто запустите его в директории с файлом `config`:

```sh
regmapGen
```

И далее произойдет "магия".

Есть дополнительные опции для замены рабочей директории, карты регистров или файла конфигурации - для получения справки просто запустите:

```sh
regmapGen -h
```

Если вы ищете дополнительные примеры, пожалуйста, проверьте директорию `examples`.

## Разработка

Пожалуйста, ознакомьтесь с [Руководством разработчика](https://regmapGen.readthedocs.io/en/latest/contributing.html).

Для PyPi:

```bash
rm -rf dist
pip3 install -e .
python3 setup.py sdist
twine upload dist/*
```

## Лицензия

regmapGen лицензирован под [Лицензией MIT](LICENSE).
