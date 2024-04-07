# League Shop Base

Reusable Django app

## Quick start

Add "lsb" to your INSTALLED_APPS setting like this::

```
    INSTALLED_APPS = [
        ...
        'lsb',
    ]
```

## To specify top sold skin values parser, add the following settings:

```
LSB_SETTINGS = {
    'top_sold_skin_values': {
        'func': <dotted_module_string_path>,
        'args': <args>,
        'kwargs': <kwargs>
    }
}
For example:

LSB_SETTINGS = {
    'top_sold_skin_values': {
        'func': 'lsb.utils.skins.get_top_sold_skin_values',
        'args': [0, 150],
        'kwargs': {}
    }
}

```

## Changelog (1.0.49)

- Renamed is_bare_metal to is_premium in admin
- Make rank field non nullable
- Added valid account and old stock filter. Needs `old_stock_max_date` in LSB_SETTINGS for old stock filter.
  ```
  LSB_SETTINGS = {
  ...
  "old_stock_max_date": "yyyy-mm-dd",
  ...
  }
  ```
