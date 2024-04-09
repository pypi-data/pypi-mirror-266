# AkitaCode Python Library

Documentation is pending to be added.

## History log

### Version 2.0.2

- Fixed an issue during the call to a *for* instance, where the evaluated variables were not correctly set as environment constants.

- Deleted some debug print to stdout.

- The conditions for the correct evaluation of arguments dependent on the specified environment when using a *for* instance are modified.

- Fixed an indexing error during export of functions and arguments.

- Support is added for the use of functions within "for" instances, allowing environment constants to be set as the value of the arguments.


### Version 2.0.2-beta

- Fixed problem during *for* line statement. Now, *for* statements can be used as following:
```
for each case of ( BAT_Temperature , BAT_SOH , BAT_SOC ) do
```


### Version 2.0.1

- Library dependencies have been fixed.


### Version 2.0.0

- First version.

