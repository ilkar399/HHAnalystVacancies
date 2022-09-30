### Запрос

`GET /vacancies` вернёт результаты поиска вакансий.

<a name="search-params"></a>
Принимаемые параметры:

> !! Внимание: неизвестные параметры и параметры с ошибкой в названии игнорируются

Некоторые параметры принимают множественные значения: `key=value&key=value`.

* `text` — текстовое поле.  
Переданное значение ищется в полях вакансии, указанных в параметре `search_field`.  
Доступен язык запросов, как и на основном сайте: [https://hh.ru/article/1175](https://hh.ru/article/1175).
Специально для этого поля есть [автодополнение](suggests.md#vacancy-search-keyword).

* `search_field` — область поиска.  
Справочник с возможными значениями: `vacancy_search_fields` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
По умолчанию, используются все поля.  
Возможно указание нескольких значений.  

* `experience` — опыт работы.  
Необходимо передавать `id` из справочника `experience` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
Возможно указание нескольких значений.

* `employment` — тип занятости.
Необходимо передавать `id` из справочника `employment` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
Возможно указание нескольких значений.  

* `schedule` — график работы.  
Необходимо передавать `id` из справочника `schedule` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
Возможно указание нескольких значений.  

* <a name="field-area"></a> `area` — регион.
Необходимо передавать `id` из справочника [/areas](areas.md).    
Возможно указание нескольких значений.  

* `metro` — ветка или станция метро.  
Необходимо передавать `id` из справочника [/metro](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1metro/get).    
Возможно указание нескольких значений.  

* `specialization` — профобласть или специализация. 
Необходимо передавать `id` из справочника [/specializations](specializations.md).    
Возможно указание нескольких значений. Будет заменен профессиональными ролями (параметр `professional_role`), в настоящее время работает в режиме обратной совместимости.
  
* `professional_role` - профессиональная область. Необходимо передавать `id` из справочника [/professional_roles](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1professional_roles/get)

* `industry` - индустрия компании, разместившей вакансию. 
Необходимо передавать `id` из справочника [/industries](industries.md).
Возможно указание нескольких значений.
  
* `employer_id` — идентификатор [компании](https://api.hh.ru/openapi/redoc#tag/Rabotodatel).  
Возможно указание нескольких значений.  

* `currency` — код валюты.  
Справочник с возможными значениями: `currency` (ключ code) в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
Имеет смысл указывать только совместно с параметром `salary`.

* `salary` — размер заработной платы.  
Если указано это поле, но не указано `currency`, то используется значение RUR у `currency`.  
При указании значения будут найдены вакансии, в которых вилка зарплаты близка к
указанной в запросе. При этом значения пересчитываются по текущим курсам ЦБ РФ.
Например, при указании `salary=100&currency=EUR` будут найдены вакансии, где
вилка зарплаты указана в рублях и после пересчёта в Евро близка к 100 EUR.
По умолчанию будут также найдены вакансии, в которых вилка зарплаты не указана,
чтобы такие вакансии отфильтровать, используйте `only_with_salary=true`.

* `label` — фильтр по меткам вакансий.   
Необходимо передавать `id` из справочника `vacancy_label` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).  
Возможно указание нескольких значений.  

* `only_with_salary` — показывать вакансии только с указанием зарплаты.  
Возможные значения: true или false.  
По умолчанию, используется false.  

* `period` — количество дней, в пределах которых нужно найти вакансии.  
Максимальное значение: 30.

* `date_from` – дата, которая ограничивает снизу диапазон дат публикации
  вакансий.  
  Нельзя передавать вместе с параметром `period`.  
  Значение указывается в формате [ISO 8601](general.md#date-format) -
  `YYYY-MM-DD` или с точность до секунды `YYYY-MM-DDThh:mm:ss±hhmm`.  
  Указанное значение будет округлено до ближайших 5 минут.

* `date_to` – дата, которая ограничивает сверху диапазон дат публикации
  вакансий.  
  Необходимо передавать только в паре с параметром `date_from`.  
  Нельзя передавать вместе с параметром `period`.  
  Значение указывается в формате [ISO 8601](general.md#date-format) -
  `YYYY-MM-DD` или с точность до секунды `YYYY-MM-DDThh:mm:ss±hhmm`.  
  Указанное значение будет округлено до ближайших 5 минут.

* `top_lat`, `bottom_lat`, `left_lng`, `right_lng` — значение гео-координат.  
При поиске используется значение указанного в вакансии адреса.  
Принимаемое значение — градусы в виде десятичной дроби.  
Необходимо передавать одновременно все четыре параметра гео-координат, иначе вернется ошибка.  

* `order_by` — сортировка списка вакансий.  
Справочник с возможными значениями: `vacancy_search_order` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).   
Если выбрана сортировка по удалённости от гео-точки `distance`, необходимо также задать её координаты `sort_point_lat`,`sort_point_lng`.

* `sort_point_lat`, `sort_point_lng` - значение гео-координат точки, по расстоянию от которой будут отсортированы вакансии. Необходимо указывать только, если `order_by` установлено в `distance`.

* `clusters` — возвращать ли [кластеры для данного поиска](clusters.md), по умолчанию: `false`.

* `describe_arguments` — возвращать ли [описание использованных параметров поиска](vacancies_search_arguments.md), по умолчанию: `false`.

* `per_page`, `page` — [параметры пагинации](general.md#pagination). Параметр per_page ограничен значением в 100.

* `no_magic` – Если значение `true` – отключить автоматическое преобразование
  вакансий. По умолчанию – `false`. При включённом автоматическом преобразовании,
  будет предпринята попытка изменить текстовый запрос пользователя на набор
  параметров. Например, запрос `text=москва бухгалтер 100500` будет преобразован
  в `text=бухгалтер&only_with_salary=true&area=1&salary=100500`.

* `premium` – Если значение `true` – в сортировке вакансий будет учтены
  премиум вакансии. Такая сортировка используется на сайте.
  По умолчанию – `false`.

* `responses_count_enabled` — Если значение `true` – включить дополнительное поле `counters` с количеством откликов для вакансии. По-умолчанию – `false`.  

* `part_time` — Вакансии для подработки. Возможные значения:  
  * все элементы из `working_days` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).   
  * все элементы из `working_time_intervals` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).   
  * все элементы из `working_time_modes` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).   
  * элементы `part` или `project` из `employment` в [/dictionaries](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1dictionaries/get).   
  * элемент `accept_temporary`, показывает вакансии только с временным трудоустройством.  
  
   Возможно указание нескольких значений.  
  
* `professional_role` — профессиональная роль. Необходимо передавать `id` из справочника
  [professional_roles](https://api.hh.ru/openapi/redoc#tag/Obshie-spravochniki/paths/~1professional_roles/get).
  Возможно указание нескольких значений. Замена специализациям (параметр `specialization`)

<a name="search-results"></a>

При указании параметров пагинации (page, per_page) работает ограничение: глубина
возвращаемых результатов не может быть больше 2000. Например, возможен запрос
`per_page=10&page=199` (выдача с 1991 по 2000 вакансию), но запрос с
`per_page=10&page=200` вернёт ошибку (выдача с 2001 до 2010 вакансию).

### Ответ

В зависимости от текущей авторизации выдача может отличаться, так как для
соискателей применяется фильтрация по
[списку скрытых вакансий и компаний](blacklisted.md).

Выдача может отличаться при выборе [различных сайтов](hosts.md) (параметр
`host`). Однако выбор регионального сайта, например `hh.kz`, не сужает выборку
до данного региона, для ограничения выборки по региону используйте параметр
[`area`](#field-area).

```json
{
  "per_page": 1,
  "items": [
    {
      "salary": {
        "to": null,
        "from": 30000,
        "currency": "RUR",
        "gross": true
      },
      "name": "Секретарь",
      "insider_interview": {
          "id": "12345",
          "url": "https://hh.ru/interview/12345?employerId=777"
      },
      "area": {
        "url": "https://api.hh.ru/areas/1",
        "id": "1",
        "name": "Москва"
      },
      "url": "https://api.hh.ru/vacancies/8331228",
      "published_at": "2013-07-08T16:17:21+0400",
      "relations": [ ],
      "employer": {
        "logo_urls": {
          "90": "https://hh.ru/employer-logo/289027.png",
          "240": "https://hh.ru/employer-logo/289169.png",
          "original": "https://hh.ru/file/2352807.png"
        },
        "name": "HeadHunter",
        "url": "https://api.hh.ru/employers/1455",
        "alternate_url": "https://hh.ru/employer/1455",
        "id": "1455",
        "trusted": true
      },
      "contacts": {
          "name": "Имя",
          "email": "user@example.com",
          "phones": [
              {
                  "country": "7",
                  "city": "985",
                  "number": "000-00-00",
                  "comment": null
              }
          ]
      },
      "response_letter_required": true,
      "address": {
        "city": "Москва",
        "street": "улица Годовикова",
        "building": "9с10",
        "description": "на проходной потребуется паспорт",
        "lat": 55.807794,
        "lng": 37.638699,
        "metro_stations": [
          {
            "station_id": "6.8",
            "station_name": "Алексеевская",
            "line_id": "6",
            "line_name": "Калужско-Рижская",
            "lat": 55.807794,
            "lng": 37.638699
          }
        ]
      },
      "sort_point_distance": 226.001293,
      "alternate_url": "https://hh.ru/vacancy/8331228",
      "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=8331228",
      "department": {
        "id": "HH-1455-TECH",
        "name": "HeadHunter::Технический департамент"
      },
      "type": {
        "id": "open",
        "name": "Открытая"
      },
      "id": "8331228",
      "has_test": true,
      "response_url": null,
      "snippet": {
          "requirement": "Высшее образование. Опыт работы в качестве <highlighttext>секретаря</highlighttext>, офис-менеджера. Знание делопроизводства, документооборота. Коммуникативные навыки.",
          "responsibility": "Документооборот (регистрация, отправка, контроль исполнения писем, ведение протоколов, отчетность). Распределение корреспонденции. Прием и распределение телефонных звонков."
      },
      "schedule": {
        "id": "fullDay",
        "name": "Полный день"
      },
      "counters": {
        "responses": 0
      }
    }
  ],
  "page": 0,
  "pages": 13,
  "found": 13,
  "clusters": null,
  "arguments": null
}
```