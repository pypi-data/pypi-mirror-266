# FREMAKE CANOPY

## How to build the example
```bash
git clone -b 2023.00 https://gitlab.gfdl.noaa.gov/portable_climate/fremake_canopy.git
cd fremake_canopy
sed -i 's:/ncrc/home2/Thomas.Robinson/fremake_canopy:$PWD:g' yamls/am5.yaml
cd yamls
../fremake -y am5.yaml -p ncrc5.intel -t debug-openmp
```

## Current limitations
- This only works on C5.  The modules on C4 are currently a mess.  Hopefully this will be fixed 
 with the upgrade.
- The containers section is currently broken and needs to be fixed.
- The Makefile is currently hardcoded to build in `DEBUG` with no openmp
- Many others I'm sure.

## YAMLS:
experiment yaml: This is the main yaml and gives the path to the other yamls
```yaml
platformYaml: path to yaml containing the platforms
layoutYaml: path to the yaml containing the layouts (not used currently)
compileYaml: path to the yaml with the model source code and build information
experiments: path to the yaml that has information about expeiment configurations (not currently used)

```

compile yaml: Containers information about source code and how to build
```yaml
experiment: name of the model
src: 
     - component: The name of the component model
       requires: [Array of required components]
       repo: scalar URL of the repo --OR-- [array of URLs to the code repos if more than one is required]
       branch: scalar (or array of same size of repo) of the version of the code to clone
       doF90Cpp: True if the F90cpp needs to be done (land)
       cppdefs: a single string containing all CPPDEFs to add during compilations
       paths: [array of paths to build]
```

platform yaml: User defined platform specifications.  This will require more user input that bronx
```yaml
platforms:
   - name: the platform name
     compiler: the compiler you are using
     modulesInit: ["array of commands that are needed to load modules." , "each command must end with a newline character"]
     modules: [array of modules to load including compiler]
     fc: the name of the fortran compiler
     cc: the name of the C compiler
     mkTemplate: The location of the mkmf make template
     modelRoot: The root directory of the model (where src, exec, experiments will go)
     container: True if this is a container platform
     containerBuild: "podman" - the container build program
     containerRun: "apptainer" - the container run program
```
