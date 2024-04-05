# CHANGELOG

## 0.1.23 (2024-04-04)

- [Feature] Pinning `cloudpickle==3.0.0`
- [Feature] Increase default timeout to 5 minutes
- [Feature] Adds `pdf_scanned_to_text`

## 0.1.22 (2024-04-04)

- [Feature] Updates API calls to `[@functions](https://github.com/functions).serverless`

## 0.1.21 (2024-04-04)

- [Feature] Fixed issue when calling the `pdf_to_text` function

## 0.1.20 (2024-04-02)

- [Feature] Add `[@functions](https://github.com/functions).serverless`

## 0.1.19 (2024-03-29)

- [Fix] Rename `env_variables` to `secrets` ([#64](https://github.com/ploomber/ploomber-cloud/issues/64))

## 0.1.18 (2024-03-26)

- [Feature] Add `functions.{pdf_to_text, image_to_text, get_result}`

## 0.1.17 (2024-03-20)

- [Feature] Add `delete` to delete a project ([#41](https://github.com/ploomber/ploomber-cloud/issues/41))
- [Feature] Allow deploying examples from docker ([#61](https://github.com/ploomber/ploomber-cloud/issues/61))

## 0.1.16 (2024-03-11)

- [Feature] Add `pc` as a CLI shortcut for `ploomber-cloud`

## 0.1.15 (2024-03-11)

- [Feature] Deploy `--watch` shows logs ([#38](https://github.com/ploomber/ploomber-cloud/issues/38))

## 0.1.14 (2024-03-07)

- [Feature] Add support for Dash applications ([#58](https://github.com/ploomber/ploomber-cloud/issues/58))
- [Fix] More informative error messages for Ploomber Cloud exceptions ([#55](https://github.com/ploomber/ploomber-cloud/issues/55))
- [Fix] Add smarter project detection for Docker types with informative message ([#47](https://github.com/ploomber/ploomber-cloud/issues/47))

## 0.1.13 (2024-03-04)

- [Feature] Add `ploomber-cloud examples` for downloading example apps ([#36](https://github.com/ploomber/ploomber-cloud/issues/36))

## 0.1.12 (2024-03-04)

- [Feature] Add support for Voila applications ([#50](https://github.com/ploomber/ploomber-cloud/issues/50))

## 0.1.11 (2024-02-27)

- [Feature] Add support for Shiny-R applications ([#51](https://github.com/ploomber/ploomber-cloud/issues/51))

## 0.1.10 (2024-02-16)

- [Feature] Adds anonymous telemetry
- [Feature] Add smarter project detection ([#40](https://github.com/ploomber/ploomber-cloud/issues/40))

## 0.1.9 (2024-02-01)

- [Feature] Add support for Solara applications ([#31](https://github.com/ploomber/ploomber-cloud/issues/31))

## 0.1.8 (2024-01-31)

- [Feature] Add support for secrets via `.env` file ([#26](https://github.com/ploomber/ploomber-cloud/issues/26))
- [Fix] Shorter error when trying to deploy a project that hasn't been initialized
- [Fix] Changed deployment link from `dashboards` to `applications` ([#34](https://github.com/ploomber/ploomber-cloud/issues/34))

## 0.1.7 (2024-01-24)

- [Fix] Checking HTTP code (404) to decide which error message to display

## 0.1.6 (2024-01-23)

- [Feature] Add `github` for creating or updating the GitHub actions file `.github/workflows/ploomber-cloud.yaml` in repository.

## 0.1.5 (2024-01-09)

- [Fix] Fix issue when using `--watch` ([#20](https://github.com/ploomber/ploomber-cloud/issues/20))

## 0.1.4 (2023-12-20)

- [Feature] Add `--force` option to init to re-initialize a project and override the existing `ploomber-cloud.json` file
- [Feature] Add `--version`
- [Fix] Updates API header from `access_token` to `api_key`

## 0.1.3 (2023-12-14)

- [Feature] Add `ploomber-cloud deploy --watch` to watch deploy status from CLI ([#11](https://github.com/ploomber/ploomber-cloud/issues/11))

## 0.1.2 (2023-12-11)

- [Feature] Allow `init` to initialize an existing project

## 0.1.1 (2023-11-17)

- [Feature] Read key from `PLOOMBER_CLOUD_KEY` environment variable, if set

## 0.1.0 (2023-11-17)

- [Feature] Add `ploomber-cloud key` command to set key
- [Feature] Add `ploomber-cloud init` to configure a project
- [Feature] Add `ploomber-cloud deploy` to deploy a project
