# Fortran runtime generators


Generates fortan runtime for given DMT blueprints

The generated fortran code depend on fortran modules from other FPM (fortran-package-manager) packages. Therefore, include this in your manifest file:

```toml
[dependencies]
json-fortran = {git = "https://github.com/jacobwilliams/json-fortran.git", tag = "8.3.0" }
error-handling = { git = "https://github.com/SINTEF/fortran-error-handling.git", tag = "v0.2.0" }
```
