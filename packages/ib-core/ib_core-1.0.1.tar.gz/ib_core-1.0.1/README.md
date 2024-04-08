
![Logo](https://ib-elp-it-psg.com/static/admin/img/root_media/icon_psg.svg)


# Integration Bus Module Core

Used in the template, it defines the basic models and methods of working with them


## Description of base components and models

### Models

#### UUIDModel: 
- Base Model of *IB Core*.
- Includes infornation about creator (UUID) and creating date/time.
- Includes *TagManager* for adding additional model properties

#### TagManager:
- A model for creating, updating, and managing tags.

#### TagBinder: 
*Used by *TagManager*, not independent model*
- Binds *Tag* objects to any models by keyword.
- Works directly with *IB Tags Module*.

### Mixins

#### TokenAuthorizationMixin: 
*Uses external authorization, managed by IB Auth Module*
- Supports Base and JsonWeb tokens.
- Automatically checks authorization headers of request and sends error respones.
- Converts user info response from *IB Auth Module* to *AuthUser* class object which can be accessed via *self.user* in views.

### Admin Models

#### UUIDModelAdmin

Base ModelAdmin for UUIDModel instances.

Automatically adds 'creator', 'create_date_time_stamp' and 'tag_manager' fields to 'list_display'.

You can change this behaviour by overriding the following fields to False:
- display_creator;
- display_create_date_time_stamp;
- display_tag_manager.

## Related

Project template for Integration Bus module development

[PSG Django Template](https://github.com/KZN-IT-PSG/psg_django_template)


## Зависимости

| Проект | Индентификатор |
| --- | --- |
|[__Authorization Management Module__](https://github.com/KZN-IT-PSG/auth_management_module)| 1.AuthModule |
|[__IB ELP IT PSG__](https://github.com/KZN-IT-PSG/integration_bus)| 01.1.ООО "ПСГ".IT-PSG.Разработка интеграционной шины IB-ELP |


## Authors

-  [DamirF](https://github.com/DamirF)

