# This file contains all notable changes to the AVC-VersionFileValidator

## master (not included in any release yet)


## v1
## v1.4.0
* Point workflow examples to master branch 
* Annotate warnings and errors in PR "Changes" overview (#17 by: DasSkelett)
* Raise exception for bad HTTP codes of remote version files
* Update Dockerfile to Python 3.10

## v1.3.1
* Fix TypeError when formatting logging messages that don't have any args (#15 by: DasSkelett)
* Add 'only' parameter to Action; Changes to this repo's workflow setup (#16 by: DasSkelett)

## v1.3.0
* Don't fail validation for invalid remote files (#11 by: DasSkelett)
* Update requirements (#12 by: DasSkelett)
* Allow specifying list of files to validate in console (#13 by: DasSkelett)
* Check version range for possible simplification (#14 by: DasSkelett)

### v1.2.1
* Convert to GitHub raw URIs before downloading remote files (#7 by: DasSkelett)
* Fix incorrect compatibility warning for `"KSP_VERSION": "any"` (#8: by DasSkelett)
* Download schema + build map only once during tests (#9 by: DasSkelett)

### v1.2.0
* Validate remote version file if specified with `URL` property.
* Make the validator importable as a package (#4 by: DasSkelett)
* Use logging instead of print(), make use of the Action logging syntax (#4 by: DasSkelett)
* Implement KSP version comparison logic + warn for outdated KSP compatibilities (#5 by: DasSkelett)
* Throw validation errors only once; format 'requests' debug logging (#6 by: DasSkelett)

### v1.1.1
* Add requirements.txt for easier dev env setup.
* Add examples in the examples/ folder. The standard.yml should cover most use cases.
* Do not overwrite requirements.txt if it exists in the triggering repo.

### v1.1.0
* Allow wildcards in the exclusion input arguments. They are evaluated according to Python3's pathlib.Glob() function,
    so recursive exclusions (`**/*.version`) are supported. The exclusion value has to be a JSON array now!
* Output handy details when finishing validation (number of failed, successful, ignored)
* Add CHANGELOG.md
* Push PyCharm IDE settings into repository.
    Includes configurations for running the tests in a container or on the host directly,
    running the validator itself in one of the test workspaces (container or host).
* Unit test setup

### v1.0.0
Initial release.
Supports basic functionality as well as excluding specific files, specified in the input.exclude parameter.
See README.md for usage information.
