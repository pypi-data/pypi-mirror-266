# Sub-commands

## submit

`submit` is a subcommand for submitting bake build request using build definition.

```shell
tuxsuite build submit build-definition
```

## cancel

`cancel` is a subcommand for cancelling submitted build identified by its `uid`.
Cancelling is available for any build state, except `finished`.

```shell
tuxsuite build cancel 1t2giSA1sSKFADKPrl0YI1gjMLb
```
