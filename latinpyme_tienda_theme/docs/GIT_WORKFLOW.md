# Flujo Git para Tienda LatinPyme Theme

Este proyecto usa un repositorio principal y un submodulo Git para los modulos personalizados.

Repositorio principal:

```bash
/d/Odoo/latinpyme-odoo
```

Submodulo de modulos personalizados:

```bash
src/odoo/addons/latinpyme_custom
```

## Reglas importantes

- No hacer `git pull` si hay cambios locales sin commitear.
- Siempre ejecutar `git status` antes de `pull`, `commit` o `push`.
- Los cambios dentro de `latinpyme_custom` se commitean primero en el submodulo.
- Luego se actualiza el puntero del submodulo en el repo principal.
- No hacer `git add .` desde el repo principal sin revisar.
- No modificar `latinpyme_revista_theme` para este desarrollo.

## A. Actualizar repo principal

```bash
cd /d/Odoo/latinpyme-odoo
git checkout production
git status
git pull origin production
git submodule update --init --recursive
```

## B. Actualizar submodulo

```bash
git -C src/odoo/addons/latinpyme_custom checkout main
git -C src/odoo/addons/latinpyme_custom status
git -C src/odoo/addons/latinpyme_custom pull origin main
```

## C. Revisar cambios

```bash
git -C src/odoo/addons/latinpyme_custom status
```

## D. Agregar cambios del futuro modulo tienda

```bash
git -C src/odoo/addons/latinpyme_custom add latinpyme_tienda_theme
```

## E. Commit y push del submodulo

```bash
git -C src/odoo/addons/latinpyme_custom commit -m "Crear estructura inicial de tema tienda LatinPyme"
git -C src/odoo/addons/latinpyme_custom push origin HEAD:main
```

## F. Actualizar puntero del submodulo en el repo principal

```bash
git status
git add src/odoo/addons/latinpyme_custom
git commit -m "Actualizar submodulo latinpyme_custom para tema tienda LatinPyme"
git push origin production
```

## Nota para Odoo.sh

Despues de subir el commit del submodulo y actualizar el puntero en el repositorio principal, Odoo.sh podra tomar la version correcta del submodulo en la rama `production`.

