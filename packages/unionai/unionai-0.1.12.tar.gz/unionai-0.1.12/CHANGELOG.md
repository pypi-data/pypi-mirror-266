# Changelog

## [Unreleased] - TBA

## [v0.1.12] - 2024-04-04

- Adds support for `flytekit`'s StructuredDatasets
- Update to `serverless-1.us-east-2.s.union.ai` tenant
- Update HTML callback page.

## [v0.1.11] - 2024-03-29

- Changes image builder name to `unionai`.
- Fixes issue with multiple callbacks when authenticating.

## [v0.1.10] - 2024-03-26

- Fixes project issue when switching between `pyflyte` and `unionai`.

## [v0.1.9] - 2024-03-26

- Adds `verbose` and `x-request-id` for debugging.

## [v0.1.8] - 2024-03-25

- Install `unionai` by default in the image builder.

## [v0.1.7] - 2024-03-25

* Adds Image Build related mapping of Union serverless FQDN to Google Artifact registry base URLs.
- Adds `unionai create login device-flow` and `unionai delete login` to enable device flow authentication.
- `unionai` ignores `FLYTECTL_CONFIG`. Please use `UNIONAI_CONFIG` instead.
- Only require auth when running `unionai run --remote`.
- Make sure `project` is set to `"default"` for serverless.

## [v0.1.6] - 2024-03-13

- Updates Artifacts with `OnTrigger` and sync up with `flytekit`
- Adds Time Granularity
- Add model/data cards

## [v0.1.5] - 2024-02-29

- Fixes bug with `FlyteDirectory` such that multiple files can be downloaded

## [v0.1.4] - 2024-02-27

- Fixes circular reference issue when importing `UnionRemote`

## [v0.1.3] - 2024-02-27

- Adds support for `FlyteDirectory`

## [v0.1.2] - 2024-02-27

- Runs Image builder in the system project
- Adds `is_container()` to ImageSpec

## [v0.1.1] - 2024-02-16

- Fixes default images when passing `--config` in CLI
- Redesigned OAuth success HTML page: Requires `flytekit>=1.10.8`

## [v0.1.0] - 2024-02-15

- Adds UnionAI's ImageBuilder plugin for `ImageSpec`
- Adds Secrets CLI
- Adds Application management CLI
- Adds `--org` to configure the organization in every grpc request
- Adds Artifacts and Triggers (`unionai.artifacts`)
- Adds PersistentDirectory for on-node persistent storage (`unionai.persist`)
