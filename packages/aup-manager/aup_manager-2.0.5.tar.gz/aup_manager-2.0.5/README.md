# AUP Manager

## Instalation

- install `Node.js`
- create configuration file `/etc/aup-manager.yaml`
- installation automatically executes `npm install && npm run compile_sass` in `aup_manager/static`. This is needed for bootstrap installation and compilation of custom css.

### General

```
pip install
```

### With perun connector

```
pip install -e .[perun]
```

### TOAST UI Editor

- editor is currently included from uicdn.toast.com so content security policy has to be adjusted (planned change)
