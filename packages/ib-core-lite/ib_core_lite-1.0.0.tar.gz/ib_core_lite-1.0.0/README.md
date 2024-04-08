# Integration Bus Module Core Lite <img alt="Logo" height="25" src="https://ib-elp-it-psg.com/static/admin/img/root_media/icon_psg.svg" width="25"/>

Used in the FastAPI Applications, it defines the basic models and methods of working with them

## Description of base components and models

### Mixins

#### TokenAuthorizationMixin:

*Uses external authorization, managed by IB Auth Module*

- Supports Base and JsonWeb tokens.
- Automatically checks authorization headers of request and sends error respones.
- Converts user info response from *IB Auth Module* to *AuthUser* class object which can be accessed via *self.user* in
  views.

## Authors

- [DamirF](https://github.com/DamirF)
- [IT-PSG Solutions](https://it-psg.com)

