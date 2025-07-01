- [ ] Describe the purpose of this pull request (Add a link to the jira issue when possible)
- [ ] Share the command line used to run the test
```console
$ reframe -r ...
```
- You can manually trigger 1 (or more) CI pipelines by adding a `cscs-ci run alps-daint-uenv` comment in the Pull Request
- By default all UENVs will be tested, however you can restrict to a single UENV with: `cscs-ci run alps-daint-uenv;MY_UENV=cp2k/2025.1:v2`

Thank you for taking the time to contribute to `cscs-reframe-tests` !
