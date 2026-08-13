# Changelog

## 0.121.0 (2026-08-07)

Full Changelog: [v0.120.2...v0.121.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.120.2...v0.121.0)

### Features

* **api:** add `mid-conversation-tool-changes-2026-07-01` beta ([c7d1531](https://github.com/anthropics/anthropic-sdk-python/commit/c7d1531d9d63a35430333039f8c975bba4ef0411))
* **api:** add support for session budgets, advisor tool, pinned inference location and skills auto-loading from GitHub ([193bae0](https://github.com/anthropics/anthropic-sdk-python/commit/193bae02806219047d484d7efcb9b91776a6c45c))


### Chores

* **api:** remove retired Claude Opus 4.1 models ([5352a33](https://github.com/anthropics/anthropic-sdk-python/commit/5352a33ade5b62ad782b522f1791b7eeeeff83be))
* **docs:** small updates to descriptions ([b8d4176](https://github.com/anthropics/anthropic-sdk-python/commit/b8d41762e264fe6721847f77daa337eab4905162))
* **docs:** updates to a few documentation strings ([3a5dd69](https://github.com/anthropics/anthropic-sdk-python/commit/3a5dd6971e0f43023533db3ed35f94ceb6c0ebde))
* ensure all dependencies have major version constraints ([#274](https://github.com/anthropics/anthropic-sdk-python/issues/274)) ([d52999b](https://github.com/anthropics/anthropic-sdk-python/commit/d52999b4f66002ffe8263756c59ab0e276c74264))

## 0.120.2 (2026-07-28)

Full Changelog: [v0.120.1...v0.120.2](https://github.com/anthropics/anthropic-sdk-python/compare/v0.120.1...v0.120.2)

### Bug Fixes

* **mcp:** support mcp sdk v2 alongside v1 ([#300](https://github.com/anthropics/anthropic-sdk-python/issues/300)) ([177f88c](https://github.com/anthropics/anthropic-sdk-python/commit/177f88ccd7f966e47b654cb19ad0e9cfa4c58ac2))

## 0.120.1 (2026-07-28)

Full Changelog: [v0.120.0...v0.120.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.120.0...v0.120.1)

### Bug Fixes

* **mcp:** pin mcp extra to &lt;2 ([#1783](https://github.com/anthropics/anthropic-sdk-python/issues/1783)) ([fb66371](https://github.com/anthropics/anthropic-sdk-python/commit/fb66371322621be23a0956f1998da39c4686f4cb))

## 0.120.0 (2026-07-24)

Full Changelog: [v0.119.0...v0.120.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.119.0...v0.120.0)

### Features

* **api:** add claude-opus-5 model ([bf4e31c](https://github.com/anthropics/anthropic-sdk-python/commit/bf4e31c17c43ba2b409bec57e1856b025d159f1a))
* **api:** add tool addition/removal blocks and tool_change events ([bf4e31c](https://github.com/anthropics/anthropic-sdk-python/commit/bf4e31c17c43ba2b409bec57e1856b025d159f1a))
* **api:** expand client-side fallback credit token types and add server-side fallbacks default option ([bf4e31c](https://github.com/anthropics/anthropic-sdk-python/commit/bf4e31c17c43ba2b409bec57e1856b025d159f1a))

## 0.119.0 (2026-07-23)

Full Changelog: [v0.118.0...v0.119.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.118.0...v0.119.0)

### Features

* **api:** add new stop reason 'model_context_window_exceeded' ([d983cde](https://github.com/anthropics/anthropic-sdk-python/commit/d983cdecdea27fb8ae36fd293930b978c9bebf4f))


### Bug Fixes

* **tools:** handle binary files in agent toolset read/edit ([#283](https://github.com/anthropics/anthropic-sdk-python/issues/283)) ([417b76b](https://github.com/anthropics/anthropic-sdk-python/commit/417b76b9adcb69ee9effa2e9af1536dd08e6764e))

## 0.118.0 (2026-07-22)

Full Changelog: [v0.117.1...v0.118.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.117.1...v0.118.0)

### Features

* **api:** add support for Managed Agents model effort, initial session events, and threads delta streaming ([712bc6f](https://github.com/anthropics/anthropic-sdk-python/commit/712bc6f5e07ca7607e13f24fba4eea57c2e73478))

## 0.117.1 (2026-07-21)

Full Changelog: [v0.117.0...v0.117.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.117.0...v0.117.1)

### Bug Fixes

* **aws:** handle credentials correctly when using AnthropicAWS.copy() ([85d3881](https://github.com/anthropics/anthropic-sdk-python/commit/85d3881b2e178dd30b30f9ac4c462f20ea88693d))


### Chores

* **api:** add support for new refusal category ([d1dea0b](https://github.com/anthropics/anthropic-sdk-python/commit/d1dea0b51164c859de1e05a78468f5be2b6a67de))
* **client:** docs updates ([b14f94c](https://github.com/anthropics/anthropic-sdk-python/commit/b14f94c231f9adc6bb2ad96eddfc27cc1a4cfea7))
* **deps:** bump http-snapshot to 0.1.9 ([#275](https://github.com/anthropics/anthropic-sdk-python/issues/275)) ([434b657](https://github.com/anthropics/anthropic-sdk-python/commit/434b65772633f1c0d1899de64d40a67b7cb943fe))
* **deps:** pin httpx_aiohttp major version ([#271](https://github.com/anthropics/anthropic-sdk-python/issues/271)) ([924487f](https://github.com/anthropics/anthropic-sdk-python/commit/924487f7c8b3afd69ec382af78326ba224779141))
* **docs:** small updates ([c48db8b](https://github.com/anthropics/anthropic-sdk-python/commit/c48db8b6cdd800a98bf57088f530de8fe4dc82e8))
* **docs:** small updates ([755c06c](https://github.com/anthropics/anthropic-sdk-python/commit/755c06cc06161ccdf9b28b77d5e6de58adb462ce))
* **internal:** codegen related update ([a4fbecf](https://github.com/anthropics/anthropic-sdk-python/commit/a4fbecf6a2b002c8807da2336a75ddef7864f47c))

## 0.117.0 (2026-07-16)

Full Changelog: [v0.116.0...v0.117.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.116.0...v0.117.0)

### Features

* **api:** add support for dreaming ([642eee7](https://github.com/anthropics/anthropic-sdk-python/commit/642eee707b0fe3c35c21917f60b06846b2a3b291))
* **api:** add support for MCP Tunnels ([d716df6](https://github.com/anthropics/anthropic-sdk-python/commit/d716df6edb1df7de25f1b5e14dcab33b9aafc2ff))


### Bug Fixes

* **credentials:** keep credential material out of traceback frame locals via SecretStr ([aa93a4d](https://github.com/anthropics/anthropic-sdk-python/commit/aa93a4dbf383f7fdab1404c136e86d4679d644c1))


### Chores

* **docs:** small updates to field descriptions ([75d8dcc](https://github.com/anthropics/anthropic-sdk-python/commit/75d8dcc0ac8cb381fa327a61a9ac84022b3a1677))
* **docs:** update model example ([a57e30a](https://github.com/anthropics/anthropic-sdk-python/commit/a57e30ac1bafb54387bf631be2081bfdb3782911))
* **docs:** updates to descriptions and examples ([e1535b6](https://github.com/anthropics/anthropic-sdk-python/commit/e1535b6919441448dddf00e2636cb8c60a721a43))

## 0.116.0 (2026-07-02)

Full Changelog: [v0.115.1...v0.116.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.115.1...v0.116.0)

### Features

* **api:** add agent-memory-2026-07-22 beta header ([e181d5c](https://github.com/anthropics/anthropic-sdk-python/commit/e181d5c1b233d5b0b313c78b27cf1dd27f620e74))

## 0.115.1 (2026-07-01)

Full Changelog: [v0.115.0...v0.115.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.115.0...v0.115.1)

### Chores

* **api:** remove some nonfunctional types from the SDKs ([5e7c431](https://github.com/anthropics/anthropic-sdk-python/commit/5e7c431ef31b72b3f1f59902e678316fea14d983))

## 0.115.0 (2026-06-30)

Full Changelog: [v0.114.0...v0.115.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.114.0...v0.115.0)

### Features

* **api:** add support for Managed Agents event delta streaming, agent overrides, reverse pagination, vault credential injection scoping, and agent and deployment webhook events ([8c23f7e](https://github.com/anthropics/anthropic-sdk-python/commit/8c23f7ef103c287362364c12503de85eb31f07fb))

## 0.114.0 (2026-06-30)

Full Changelog: [v0.113.0...v0.114.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.113.0...v0.114.0)

### Features

* **api:** add support for claude-sonnet-5 ([b893033](https://github.com/anthropics/anthropic-sdk-python/commit/b893033b32951e0e2e04afa36a3a7eb016ae4b99))


### Bug Fixes

* **agent_toolset:** allow absolute paths that resolve inside workdir ([#121](https://github.com/anthropics/anthropic-sdk-python/issues/121)) ([0105529](https://github.com/anthropics/anthropic-sdk-python/commit/0105529fe15b1f80bbf9c56f4ae684fdfa10e2b3))

## 0.113.0 (2026-06-29)

Full Changelog: [v0.112.0...v0.113.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.112.0...v0.113.0)

### Features

* **api:** add support for 20260318 web fetch and support tools ([88dbfb1](https://github.com/anthropics/anthropic-sdk-python/commit/88dbfb14a2a838eda889469ad7fe07a47618e85f))


### Bug Fixes

* async count_tokens missing output_format/output_config merge block ([#162](https://github.com/anthropics/anthropic-sdk-python/issues/162)) ([122c958](https://github.com/anthropics/anthropic-sdk-python/commit/122c95811566bf6f5cbc682ae0a74972ae75a223))


### Chores

* **api:** accept user profile ID's when counting tokens ([0b4d17a](https://github.com/anthropics/anthropic-sdk-python/commit/0b4d17a49d39e8224adbee6a97be0e8b1b7ebff5))
* **docs:** updates to descriptions and example values ([f3ab694](https://github.com/anthropics/anthropic-sdk-python/commit/f3ab694453326a2765623b9aafeb7588ea296325))

## 0.112.0 (2026-06-24)

Full Changelog: [v0.111.0...v0.112.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.111.0...v0.112.0)

### Features

* **client:** add support for system.message streaming events ([2450d59](https://github.com/anthropics/anthropic-sdk-python/commit/2450d595731f9532080bb94eb8a43c0bd5189659))


### Bug Fixes

* **memory tool:** create parent directories with the correct permissions ([#135](https://github.com/anthropics/anthropic-sdk-python/issues/135)) ([f2fc2a9](https://github.com/anthropics/anthropic-sdk-python/commit/f2fc2a9e0ad8507e4108e9a6b85d023416c2f14c))


### Chores

* **api:** add support for new refusal category ([5ab533e](https://github.com/anthropics/anthropic-sdk-python/commit/5ab533e58ee99bcd2e5071bab91d99caee66aa6a))
* **api:** add support for sending User Profile ID in request headers ([83319be](https://github.com/anthropics/anthropic-sdk-python/commit/83319bed74f4414d54e0f4237d70b945ed671008))

## 0.111.0 (2026-06-18)

Full Changelog: [v0.110.0...v0.111.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.110.0...v0.111.0)

### Features

* **helpers:** tag refusal-fallback middleware requests with fallback-refusal-middleware ([#96](https://github.com/anthropics/anthropic-sdk-python/issues/96)) ([2f8ac78](https://github.com/anthropics/anthropic-sdk-python/commit/2f8ac789506efc0719b06f1f646c9a98bb25ce7b))

## 0.110.0 (2026-06-18)

Full Changelog: [v0.109.2...v0.110.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.109.2...v0.110.0)

### Features

* **api:** add support for new code_execution_20260120 tool ([5e23212](https://github.com/anthropics/anthropic-sdk-python/commit/5e23212dc0883174c879b97ef8e7e33ead4e8da5))


### Bug Fixes

* append x-stainless-helper across header merges instead of clobbering ([#105](https://github.com/anthropics/anthropic-sdk-python/issues/105)) ([922558e](https://github.com/anthropics/anthropic-sdk-python/commit/922558e2ce52e18863dab27bcc04067068827364))
* **bedrock:** preserve stream event type ([#1682](https://github.com/anthropics/anthropic-sdk-python/issues/1682)) ([b27e343](https://github.com/anthropics/anthropic-sdk-python/commit/b27e3439699174dbc41e34e2d6ef5cb1e2930c18))
* **helpers:** single source of truth for x-stainless-helper key + closed value vocabulary ([#95](https://github.com/anthropics/anthropic-sdk-python/issues/95)) ([e6f7a56](https://github.com/anthropics/anthropic-sdk-python/commit/e6f7a56bb624f4c946cb15ba7973fd6fe052e10f))

## 0.109.2 (2026-06-15)

Full Changelog: [v0.109.1...v0.109.2](https://github.com/anthropics/anthropic-sdk-python/compare/v0.109.1...v0.109.2)

### Chores

* **api:** remove retired models from API and SDKs ([d4bcfcc](https://github.com/anthropics/anthropic-sdk-python/commit/d4bcfcc257bd0c97d5e75060bd19c97abddd9f49))

## 0.109.1 (2026-06-09)

Full Changelog: [v0.109.0...v0.109.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.109.0...v0.109.1)

### Bug Fixes

* **api:** add `frontier_llm` refusal category ([d3a806b](https://github.com/anthropics/anthropic-sdk-python/commit/d3a806b454d8aaf5806db11c651deebe61836131))

## 0.109.0 (2026-06-09)

Full Changelog: [v0.108.0...v0.109.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.108.0...v0.109.0)

### Features

* **api:** add support for Managed Agents deployments and environment variable credentials ([47633bf](https://github.com/anthropics/anthropic-sdk-python/commit/47633bff658d4aaced3cd920ef6782c48cf31a9a))

## 0.108.0 (2026-06-09)

Full Changelog: [v0.107.1...v0.108.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.107.1...v0.108.0)

### Features

* **api:** add support for claude-mythos-5 and claude-fable-5, with support for server-side fallbacks on refusal ([6b76649](https://github.com/anthropics/anthropic-sdk-python/commit/6b76649f99bd782d2300f2a6aa3f4a3f040af324))
* **client:** adds client-side fallbacks middleware for API providers that do not support server-side fallbacks ([6b76649](https://github.com/anthropics/anthropic-sdk-python/commit/6b76649f99bd782d2300f2a6aa3f4a3f040af324))

## 0.107.1 (2026-06-07)

Full Changelog: [v0.107.0...v0.107.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.107.0...v0.107.1)

### Bug Fixes

* **foundry:** send x-api-key header for API-key auth ([#62](https://github.com/anthropics/anthropic-sdk-python/issues/62)) ([1338141](https://github.com/anthropics/anthropic-sdk-python/commit/13381413d22ad14d85e66836c67cc8a13bd2b7bd)), closes [#1661](https://github.com/anthropics/anthropic-sdk-python/issues/1661)

## 0.107.0 (2026-06-06)

Full Changelog: [v0.106.0...v0.107.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.106.0...v0.107.0)

### Features

* **api:** small updates to Managed Agents types ([72923f9](https://github.com/anthropics/anthropic-sdk-python/commit/72923f986f808597f86482a7eae4fba9a791e6ae))

## 0.106.0 (2026-06-05)

Full Changelog: [v0.105.2...v0.106.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.105.2...v0.106.0)

### Features

* **api:** mark Claude Opus 4.1 as deprecated ([85068cc](https://github.com/anthropics/anthropic-sdk-python/commit/85068cc4cb42feecb80a378942cec71e1baa8dcf))


### Bug Fixes

* **client:** make Foundry client copy() and with_options() work ([94146ac](https://github.com/anthropics/anthropic-sdk-python/commit/94146acdc1c6f66f187d5a42e4afbb911e692fe8))
* **transform schema:** preserve $defs when schema root is a $ref ([#1642](https://github.com/anthropics/anthropic-sdk-python/issues/1642)) ([fc58e06](https://github.com/anthropics/anthropic-sdk-python/commit/fc58e06b78407b447c50dfea109c6fb300f4b97d))


### Chores

* **internal:** fix artifact url ([a6ed0c4](https://github.com/anthropics/anthropic-sdk-python/commit/a6ed0c4124d29989a568a27293dadf66e7ebcd6f))
* **internal:** fix branch names ([3b03370](https://github.com/anthropics/anthropic-sdk-python/commit/3b0337074f0bbab47bf7f5a2b76b4d240cff719a))
* **internal:** update private repo name ([7dbcb05](https://github.com/anthropics/anthropic-sdk-python/commit/7dbcb05706f1865afeee62fb06e400f5c4bf619e))


### Documentation

* point security reports to Anthropic's HackerOne program ([#10](https://github.com/anthropics/anthropic-sdk-python/issues/10)) ([80f2c97](https://github.com/anthropics/anthropic-sdk-python/commit/80f2c97b8e9534f9879945de11c11aba00cf8704))

## 0.105.2 (2026-05-29)

Full Changelog: [v0.105.1...v0.105.2](https://github.com/anthropics/anthropic-sdk-python/compare/v0.105.1...v0.105.2)

## 0.105.1 (2026-05-29)

Full Changelog: [v0.105.0...v0.105.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.105.0...v0.105.1)

### Chores

* **internal:** use Trusted Publishing for PyPI releases ([1d04fc5](https://github.com/anthropics/anthropic-sdk-python/commit/1d04fc52d2dd1f88e22808de2c53b0d66913631f))

## 0.105.0 (2026-05-28)

Full Changelog: [v0.104.1...v0.105.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.104.1...v0.105.0)

### Features

* **api:** Add support for claude-opus-4-8, mid-conversation system blocks, and usage.output_tokens_details ([f18b014](https://github.com/anthropics/anthropic-sdk-python/commit/f18b01414b21b49943a6ba2cdaa30ff7dd6a3025))
* support custom file size caps ([#1825](https://github.com/anthropics/anthropic-sdk-python/issues/1825)) ([7e5f944](https://github.com/anthropics/anthropic-sdk-python/commit/7e5f944ad85bd99526d9df30dc034f657472adaa))


### Chores

* **examples:** rename managed-agents private-sandbox-worker to self-hosted-sandbox-worker ([#1822](https://github.com/anthropics/anthropic-sdk-python/issues/1822)) ([750f956](https://github.com/anthropics/anthropic-sdk-python/commit/750f956a535b9e4772951d6bf1abd81203f27d4e))


### Documentation

* replace literal newlines ([8f7f6c0](https://github.com/anthropics/anthropic-sdk-python/commit/8f7f6c0d1b5ffb9563affdcf3dd2410dc72ed1b4))

## 0.104.1 (2026-05-21)

Full Changelog: [v0.104.0...v0.104.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.104.0...v0.104.1)

### Bug Fixes

* **streaming:** carry encrypted_content through beta compaction accumulator ([#1821](https://github.com/anthropics/anthropic-sdk-python/issues/1821)) ([f7a720c](https://github.com/anthropics/anthropic-sdk-python/commit/f7a720c514cc5e428b310f46249ca1c807894c2e))

## 0.104.0 (2026-05-21)

Full Changelog: [v0.103.1...v0.104.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.103.1...v0.104.0)

### Features

* **api:** Add support for thinking-token-count beta for estimated tokens in thinking block deltas when streaming ([80d0fdf](https://github.com/anthropics/anthropic-sdk-python/commit/80d0fdf460d6cd4f190681fd2241baf8ed76cc5f))

## 0.103.1 (2026-05-19)

Full Changelog: [v0.103.0...v0.103.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.103.0...v0.103.1)

### Bug Fixes

* **runner:** skip tool calls SessionToolRunner does not own ([#1817](https://github.com/anthropics/anthropic-sdk-python/issues/1817)) ([9425c6a](https://github.com/anthropics/anthropic-sdk-python/commit/9425c6a0c6ff5e1d459ac081914f3df496365884))

## 0.103.0 (2026-05-19)

Full Changelog: [v0.102.0...v0.103.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.102.0...v0.103.0)

### Features

* **client:** Add support for self-hosted sandboxes in CMA with sandbox helpers ([e5625b0](https://github.com/anthropics/anthropic-sdk-python/commit/e5625b0ae2a1e9d25847a53217c8fd70fa67c5ed))

## 0.102.0 (2026-05-13)

Full Changelog: [v0.101.0...v0.102.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.101.0...v0.102.0)

### Features

* **api:** Add BetaManagedAgentsSearchResultBlock types ([3681f10](https://github.com/anthropics/anthropic-sdk-python/commit/3681f1042608b6be4e5a56e8b52e6a619b9210f4))
* **api:** Add support for cache diagnostics beta ([db51c6c](https://github.com/anthropics/anthropic-sdk-python/commit/db51c6caabb1bede4c2d671a96e6ef88e90ffaba))
* **internal/types:** support eagerly validating pydantic iterators ([68dabb0](https://github.com/anthropics/anthropic-sdk-python/commit/68dabb0e9b11ecd8745b231019e9bf788b72101a))


### Chores

* **api:** spec updates ([d579133](https://github.com/anthropics/anthropic-sdk-python/commit/d5791337776ba9d4876d3683e6ab9419365be9d3))

## 0.101.0 (2026-05-11)

Full Changelog: [v0.100.0...v0.101.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.100.0...v0.101.0)

### Features

* **aws:** Add AWS client for Claude Platform on AWS ([1e70e3a](https://github.com/anthropics/anthropic-sdk-python/commit/1e70e3a21d57a96721685c1eca9cedd10cdd5b63))


### Bug Fixes

* **client:** add missing f-string prefix in file type error message ([06d109a](https://github.com/anthropics/anthropic-sdk-python/commit/06d109aaf36629ec15c8fb076c96aed722933600))


### Chores

* **examples:** bump tools_runner.py to claude-sonnet-4-5-20250929 ([#1473](https://github.com/anthropics/anthropic-sdk-python/issues/1473)) ([1aa8e41](https://github.com/anthropics/anthropic-sdk-python/commit/1aa8e410fd34d4c4971234a3ae7c7b11a5fadaf9))
* **examples:** update shebang from poetry to uv ([#1497](https://github.com/anthropics/anthropic-sdk-python/issues/1497)) ([ace8f38](https://github.com/anthropics/anthropic-sdk-python/commit/ace8f38dccd587efc0528aba14ec09b50480b514))

## 0.100.0 (2026-05-06)

Full Changelog: [v0.99.0...v0.100.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.99.0...v0.100.0)

### Features

* **api:** add support for Managed Agents multiagents and outcomes, webhooks, vault validation ([3b3deee](https://github.com/anthropics/anthropic-sdk-python/commit/3b3deee9c479ce5b54411a8572b66c5a90f1d50f))


### Bug Fixes

* **api:** Adjust webhook configuration ([8c3339e](https://github.com/anthropics/anthropic-sdk-python/commit/8c3339e532458e93585f2faf4f284ccbb5829717))

## 0.99.0 (2026-05-05)

Full Changelog: [v0.98.1...v0.99.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.98.1...v0.99.0)

### Features

* **client:** allow targeting a workspace for OIDC federation token exchange ([4ba8067](https://github.com/anthropics/anthropic-sdk-python/commit/4ba8067daa634691ea8c8a3b970d42bdaf5f04eb))

## 0.98.1 (2026-05-04)

Full Changelog: [v0.98.0...v0.98.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.98.0...v0.98.1)

### Chores

* fix typo in example ([#1754](https://github.com/anthropics/anthropic-sdk-python/issues/1754)) ([de8ba13](https://github.com/anthropics/anthropic-sdk-python/commit/de8ba13769837f92ff00be8a1b1e9ad0749eae2f))

## 0.98.0 (2026-05-04)

Full Changelog: [v0.97.0...v0.98.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.97.0...v0.98.0)

### Features

* **api:** improve Managed Agents APIs ([7faf393](https://github.com/anthropics/anthropic-sdk-python/commit/7faf3939a803420e7efd85cc18b67b97b429c172))
* **client:** add Workload Identity Federation, interactive OAuth, and auth profiles ([6458bcc](https://github.com/anthropics/anthropic-sdk-python/commit/6458bcc28e83adcd96cd084ed19ec113d5462c80))
* support setting headers via env ([52eb8cd](https://github.com/anthropics/anthropic-sdk-python/commit/52eb8cdd6e9a899519010d7e6ebc4a74a88f82cd))


### Bug Fixes

* **streaming:** propagate stop_details from message_delta onto accumulated Message ([#1725](https://github.com/anthropics/anthropic-sdk-python/issues/1725)) ([900dd9b](https://github.com/anthropics/anthropic-sdk-python/commit/900dd9b4376fd7a32d6e59d028b143558340d619))
* use correct field name format for multipart file arrays ([8350bdc](https://github.com/anthropics/anthropic-sdk-python/commit/8350bdced9599d023565c0cca93ff2d05560f991))
* **vertex:** async client missing us/eu multi-region base_url branches ([#1734](https://github.com/anthropics/anthropic-sdk-python/issues/1734)) ([3e78f71](https://github.com/anthropics/anthropic-sdk-python/commit/3e78f71c0ab3f3ff0e5402477cff06771c94864c))


### Chores

* **internal:** reformat pyproject.toml ([5a9d5fd](https://github.com/anthropics/anthropic-sdk-python/commit/5a9d5fd106c52643b87881d341b27dc7b12d5975))

## 0.97.0 (2026-04-23)

Full Changelog: [v0.96.0...v0.97.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.96.0...v0.97.0)

### Features

* **api:** CMA Memory public beta ([fc30ebe](https://github.com/anthropics/anthropic-sdk-python/commit/fc30ebe5ca81204faa0b1d756b61dad176e37dcb))


### Bug Fixes

* **api:** fix errors in api spec ([f946de8](https://github.com/anthropics/anthropic-sdk-python/commit/f946de8da00748b472489e93ab4920d64d1cb22d))
* **api:** restore missing features ([72212ab](https://github.com/anthropics/anthropic-sdk-python/commit/72212ab8408af389981e9e6b111c00460b2b17e4))


### Performance Improvements

* **client:** optimize file structure copying in multipart requests ([1f9eed3](https://github.com/anthropics/anthropic-sdk-python/commit/1f9eed3a953c8cef0967df8470e04f7ac8fe3235))


### Chores

* add missing import ([4b12f5e](https://github.com/anthropics/anthropic-sdk-python/commit/4b12f5e0f4c29a234cd05f93c603b9cae2011aaa))
* **internal:** more robust bootstrap script ([7ed7370](https://github.com/anthropics/anthropic-sdk-python/commit/7ed737089d1f28385ee827f601ba81f1935d0b6a))
* **tests:** bump steady to v0.22.1 ([a4b7184](https://github.com/anthropics/anthropic-sdk-python/commit/a4b7184e57410ae92a409db5ee6fec90edceaa51))

## 0.96.0 (2026-04-16)

Full Changelog: [v0.95.0...v0.96.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.95.0...v0.96.0)

### Features

* **api:** add claude-opus-4-7, token budgets and user_profiles ([0aa2a0d](https://github.com/anthropics/anthropic-sdk-python/commit/0aa2a0d4388a39984134d1dfc2bcbd6b206f7184))


### Chores

* **ci:** remove release-doctor workflow ([1d9add3](https://github.com/anthropics/anthropic-sdk-python/commit/1d9add35d0bd4c71f2bca3b0d494d1d0a348817a))

## 0.95.0 (2026-04-14)

Full Changelog: [v0.94.1...v0.95.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.94.1...v0.95.0)

### Features

* **api:** mark Sonnet and Opus 4 as deprecated ([0c1e773](https://github.com/anthropics/anthropic-sdk-python/commit/0c1e7736394585dd021b53c1f87383c4fae29a6b))
* **bedrock:** use auth header for mantle client ([#1644](https://github.com/anthropics/anthropic-sdk-python/issues/1644)) ([3b93090](https://github.com/anthropics/anthropic-sdk-python/commit/3b93090e121861462f21a7621484cda66c139997))

## 0.94.1 (2026-04-13)

Full Changelog: [v0.94.0...v0.94.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.94.0...v0.94.1)

### Bug Fixes

* **streaming:** add missing events ([c6a06d8](https://github.com/anthropics/anthropic-sdk-python/commit/c6a06d80b7e87bc034bd6ade950c735da02a0be3))

## 0.94.0 (2026-04-10)

Full Changelog: [v0.93.0...v0.94.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.93.0...v0.94.0)

### Features

* vertex eu region ([#1658](https://github.com/anthropics/anthropic-sdk-python/issues/1658)) ([b7e157d](https://github.com/anthropics/anthropic-sdk-python/commit/b7e157d85f50b2900ddf896e8e80882dd7311bfd))


### Bug Fixes

* ensure file data are only sent as 1 parameter ([837b25b](https://github.com/anthropics/anthropic-sdk-python/commit/837b25bb6262186a5bae92aa70eb73c3cf8c90af))


### Documentation

* improve examples ([48089fd](https://github.com/anthropics/anthropic-sdk-python/commit/48089fdb788500d00718b9d4ae24cd34e5e91beb))
* update examples ([0f3c28b](https://github.com/anthropics/anthropic-sdk-python/commit/0f3c28b973026d135f91f38c4ad82ae2b1131522))

## 0.93.0 (2026-04-09)

Full Changelog: [v0.92.0...v0.93.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.92.0...v0.93.0)

### Features

* **api:** Add beta advisor tool ([4297dca](https://github.com/anthropics/anthropic-sdk-python/commit/4297dca285441b185ea9e3d18b7f912102b54be2))

## 0.92.0 (2026-04-08)

Full Changelog: [v0.91.0...v0.92.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.91.0...v0.92.0)

### Features

* **api:** add support for Claude Managed Agents ([5b879a7](https://github.com/anthropics/anthropic-sdk-python/commit/5b879a7d929bd93332d777bed067be680819dfac))

## 0.91.0 (2026-04-07)

Full Changelog: [v0.90.0...v0.91.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.90.0...v0.91.0)

### Features

* **client:** Create Bedrock Mantle client ([#1616](https://github.com/anthropics/anthropic-sdk-python/issues/1616)) ([fd195a2](https://github.com/anthropics/anthropic-sdk-python/commit/fd195a2fa2cd44ebf4513e69f671def88d2b6ec9))

## 0.90.0 (2026-04-07)

Full Changelog: [v0.89.0...v0.90.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.89.0...v0.90.0)

### Features

* **api:** Add support for claude-mythos-preview ([fc7ddd8](https://github.com/anthropics/anthropic-sdk-python/commit/fc7ddd8e0296a578f09c7fa2baf00e50d81cf980))


### Bug Fixes

* **client:** preserve hardcoded query params when merging with user params ([32d35e0](https://github.com/anthropics/anthropic-sdk-python/commit/32d35e0ae67ab0d076a60d38fa5177b5635e9c0c))

## 0.89.0 (2026-04-03)

Full Changelog: [v0.88.0...v0.89.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.88.0...v0.89.0)

### Features

* **vertex:** add support for US multi-region endpoint ([4e732da](https://github.com/anthropics/anthropic-sdk-python/commit/4e732dada087146cfeff1f4afdf90513590e248d))


### Bug Fixes

* **client:** preserve hardcoded query params when merging with user params ([e7f4a3c](https://github.com/anthropics/anthropic-sdk-python/commit/e7f4a3cada266e9719e5c3b9ba09514c3842a638))


### Chores

* **client:** deprecate client-side compaction helpers ([e60affc](https://github.com/anthropics/anthropic-sdk-python/commit/e60affc656e4165de7cb15f73351175507b0b441))

## 0.88.0 (2026-04-01)

Full Changelog: [v0.87.0...v0.88.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.87.0...v0.88.0)

### Features

* **api:** add structured stop_details to message responses ([fd82d6b](https://github.com/anthropics/anthropic-sdk-python/commit/fd82d6b87ef0db5b2970d8f27ccc6d5981745572))
* bedrock api key auth ([#1623](https://github.com/anthropics/anthropic-sdk-python/issues/1623)) ([a95a3fc](https://github.com/anthropics/anthropic-sdk-python/commit/a95a3fc586b8de63e3c2b386cee5e312d96bf5d8))
* prepare aws package ([#1615](https://github.com/anthropics/anthropic-sdk-python/issues/1615)) ([6875fab](https://github.com/anthropics/anthropic-sdk-python/commit/6875fab38ac27ab3a09b97088a49925abe011bdc))


### Chores

* **tests:** bump steady to v0.20.2 ([1bc4e9f](https://github.com/anthropics/anthropic-sdk-python/commit/1bc4e9ffc160eb1ded6294652936caafd6dfc64a))

## 0.87.0 (2026-03-31)

Full Changelog: [v0.86.0...v0.87.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.86.0...v0.87.0)

### Features

* **client:** add error type field to APIStatusError ([#1587](https://github.com/anthropics/anthropic-sdk-python/issues/1587)) ([dd563c0](https://github.com/anthropics/anthropic-sdk-python/commit/dd563c031c2a0be75ccb6175246685abd5806d7d))
* **internal:** implement indices array format for query and form serialization ([11a6244](https://github.com/anthropics/anthropic-sdk-python/commit/11a624467bd44175bc602f0135ff354895bdebdd))


### Bug Fixes

* honor __api_exclude__ in async transform path ([#1612](https://github.com/anthropics/anthropic-sdk-python/issues/1612)) ([8172232](https://github.com/anthropics/anthropic-sdk-python/commit/8172232a8bb19e0d0bf10df1c3c21ed492784585)), closes [#1610](https://github.com/anthropics/anthropic-sdk-python/issues/1610)
* **memory:** return resolved path from async _validate_path ([7b0add3](https://github.com/anthropics/anthropic-sdk-python/commit/7b0add32bd5fc59ad0fa277ef6982ee1df1eed7a))
* **memory:** use restrictive file mode for memory files ([47ba5b8](https://github.com/anthropics/anthropic-sdk-python/commit/47ba5b8f5f74beb1e1babef249754e1312b9dddf))
* sanitize endpoint path params ([98f60e4](https://github.com/anthropics/anthropic-sdk-python/commit/98f60e42039392a133d83c8673d659f514c15a35))
* **transform schema:** support enums ([#1275](https://github.com/anthropics/anthropic-sdk-python/issues/1275)) ([5c088ab](https://github.com/anthropics/anthropic-sdk-python/commit/5c088ab1d162b1c1a18f566688b31bfbd7610825))


### Chores

* **ci:** run builds on CI even if only spec metadata changed ([194c050](https://github.com/anthropics/anthropic-sdk-python/commit/194c05029403cef820897c3c6b2c26d4df0736f7))
* **ci:** skip lint on metadata-only changes ([03e2ab9](https://github.com/anthropics/anthropic-sdk-python/commit/03e2ab9e95ec452d7d519e0b419c8881f3ae3a08))
* **internal:** update gitignore ([94ede14](https://github.com/anthropics/anthropic-sdk-python/commit/94ede14b443c78b51931c185d1cd44f4ef201eae))
* **tests:** bump steady to v0.19.4 ([2d6d58f](https://github.com/anthropics/anthropic-sdk-python/commit/2d6d58fa0101930c8f5cd9e9a94e7e988055f371))
* **tests:** bump steady to v0.19.5 ([8fb439a](https://github.com/anthropics/anthropic-sdk-python/commit/8fb439afeadaf608cbf7d4630d01735f97227e3e))
* **tests:** bump steady to v0.19.6 ([76da5fd](https://github.com/anthropics/anthropic-sdk-python/commit/76da5fdd03b7ffc65a8b58b9f2a0df3e03c587c9))
* **tests:** bump steady to v0.19.7 ([bfa40e5](https://github.com/anthropics/anthropic-sdk-python/commit/bfa40e5c5bed65da0f3f664082e58e85c26b9c66))
* **tests:** bump steady to v0.20.1 ([4fd9446](https://github.com/anthropics/anthropic-sdk-python/commit/4fd9446332ae114072dac968134e6451c62138bb))

## 0.86.0 (2026-03-18)

Full Changelog: [v0.85.0...v0.86.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.85.0...v0.86.0)

### Features

* add support for filesystem memory tools ([#1247](https://github.com/anthropics/anthropic-sdk-python/issues/1247)) ([235d218](https://github.com/anthropics/anthropic-sdk-python/commit/235d218211ac4b8f1aa37e29bedc998bfb6ce77d))
* **api:** manual updates ([86dbe4a](https://github.com/anthropics/anthropic-sdk-python/commit/86dbe4aa58386bfb8d1497debf342e929e9bb5e5))
* **api:** manual updates ([45d9cc0](https://github.com/anthropics/anthropic-sdk-python/commit/45d9cc0914200a43743ab11aa311392e9d8c1b4f))


### Bug Fixes

* AsyncAnthropic._make_status_error missing 529 and 413 cases ([#1244](https://github.com/anthropics/anthropic-sdk-python/issues/1244)) ([05220bc](https://github.com/anthropics/anthropic-sdk-python/commit/05220bc1c1079fe01f5c4babc007ec7a990859d9))
* **deps:** bump minimum typing-extensions version ([09ab112](https://github.com/anthropics/anthropic-sdk-python/commit/09ab112289815ba6f19d8fb3da1e715748182799))
* **pydantic:** do not pass `by_alias` unless set ([b17480e](https://github.com/anthropics/anthropic-sdk-python/commit/b17480e9d06613aa597dd40d5a47f4f1250ac762))


### Chores

* **internal:** tweak CI branches ([3c0308c](https://github.com/anthropics/anthropic-sdk-python/commit/3c0308c97804ababfd3f37330e129e68ccfe4bbc))

## 0.85.0 (2026-03-16)

Full Changelog: [v0.84.0...v0.85.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.84.0...v0.85.0)

### Features

* **api:** chore(config): clean up model enum list ([#31](https://github.com/anthropics/anthropic-sdk-python/issues/31)) ([cce1a5b](https://github.com/anthropics/anthropic-sdk-python/commit/cce1a5b9e6fce4f269cec42803f37ce5e2ac2f76))
* **api:** GA thinking-display-setting ([207340c](https://github.com/anthropics/anthropic-sdk-python/commit/207340cc621855928f53e8ddd58f216ac0d8150d))
* **tests:** update mock server ([7dc86a4](https://github.com/anthropics/anthropic-sdk-python/commit/7dc86a4ffc9e70533a58065496c78394c6a6e97a))


### Bug Fixes

* **client:** add missing 413 and 529 error handlers to async client ([#1554](https://github.com/anthropics/anthropic-sdk-python/issues/1554)) ([9c2986f](https://github.com/anthropics/anthropic-sdk-python/commit/9c2986fb9c046b4cffa1b03ca8762f9c9dea0bab))
* **tool runner:** propagate container_id for programmatic tool calling ([#1462](https://github.com/anthropics/anthropic-sdk-python/issues/1462)) ([3ae7ff6](https://github.com/anthropics/anthropic-sdk-python/commit/3ae7ff6ff7af8a881706ae8068b1040a23c96fbd))
* **tools:** use filtered messages list in async compaction ([#1124](https://github.com/anthropics/anthropic-sdk-python/issues/1124)) ([710d666](https://github.com/anthropics/anthropic-sdk-python/commit/710d666f80b7667e3551c1a68d7c0ffaad115de1))


### Chores

* **ci:** bump uv version ([09656ac](https://github.com/anthropics/anthropic-sdk-python/commit/09656acef77fa459d30d811bd51aa780a567182b))
* **internal:** codegen related update ([c9e9fc2](https://github.com/anthropics/anthropic-sdk-python/commit/c9e9fc240334fc466426646d7acd64904f881a80))
* **internal:** codegen related update ([77f77d1](https://github.com/anthropics/anthropic-sdk-python/commit/77f77d19b4657a7ad0d31de42504c25cf4ed76ef))
* **tests:** unskip tests that are now supported in steady ([827330b](https://github.com/anthropics/anthropic-sdk-python/commit/827330b527b4af299af084752a7317b0596956af))

## 0.84.0 (2026-02-25)

Full Changelog: [v0.83.0...v0.84.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.83.0...v0.84.0)

### Features

* **api:** change array_format to brackets ([925d2ad](https://github.com/anthropics/anthropic-sdk-python/commit/925d2ad6b76ad7c15de07b9b2768738775f71631))
* **api:** remove publishing section from cli target ([7bc7ceb](https://github.com/anthropics/anthropic-sdk-python/commit/7bc7cebc68db70f08fce23e7e0b24acbc9ff37a7))
* **helpers:** add conversion helpers for MCP tools, prompts, and resources ([#1383](https://github.com/anthropics/anthropic-sdk-python/issues/1383)) ([9489751](https://github.com/anthropics/anthropic-sdk-python/commit/9489751386d1540bf80eff63ab47ca2b3cc18fa1))


### Chores

* add missing raw jsonl results method ([1009d4a](https://github.com/anthropics/anthropic-sdk-python/commit/1009d4aca8be42973ca39104bc9bd8087f51ff9c))
* **internal:** add request options to SSE classes ([4f4bc8e](https://github.com/anthropics/anthropic-sdk-python/commit/4f4bc8e6241c2ccee8dfe4cdbc522081e3e30f08))
* **internal:** make `test_proxy_environment_variables` more resilient ([f7056e0](https://github.com/anthropics/anthropic-sdk-python/commit/f7056e09411a45798a678be5766a7b7d6dcbc7a9))
* **internal:** make `test_proxy_environment_variables` more resilient to env ([143efcc](https://github.com/anthropics/anthropic-sdk-python/commit/143efccfcc20c12f920b6ba242eff7c0feeea7c4))
* **internal:** simplify http snapshots ([#1092](https://github.com/anthropics/anthropic-sdk-python/issues/1092)) ([4a4dc9f](https://github.com/anthropics/anthropic-sdk-python/commit/4a4dc9f6b36ab0224095790f4311c7f60c9845f7))
* **internal:** update jsonl tests ([a8e6a6e](https://github.com/anthropics/anthropic-sdk-python/commit/a8e6a6e5544b9f1626e3fb5faa31a1accfc81441))


### Documentation

* rebrand to Claude SDK and streamline README ([6b54405](https://github.com/anthropics/anthropic-sdk-python/commit/6b544058ab19e55e1c76a4ba9816205d1eedc630))

## 0.83.0 (2026-02-19)

Full Changelog: [v0.82.0...v0.83.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.82.0...v0.83.0)

### Features

* **api:** Add top-level cache control (automatic caching) ([a940123](https://github.com/anthropics/anthropic-sdk-python/commit/a940123da34ac33f0b6f20ce91807829451d1233))


### Chores

* update mock server docs ([34ef48c](https://github.com/anthropics/anthropic-sdk-python/commit/34ef48ceb0f1734d6b695890f689dc42eb0b004e))

## 0.82.0 (2026-02-18)

Full Changelog: [v0.81.0...v0.82.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.81.0...v0.82.0)

### Features

* **api:** fix shared UserLocation and error code types ([da3b931](https://github.com/anthropics/anthropic-sdk-python/commit/da3b931a2be768d77c228a4804d2f7f75caeb71c))


### Bug Fixes

* add backward-compat aliases for removed nested UserLocation classes ([#1409](https://github.com/anthropics/anthropic-sdk-python/issues/1409)) ([56db1e3](https://github.com/anthropics/anthropic-sdk-python/commit/56db1e3db6108e1c0f4e9363a5f23b54976dc877))

## 0.81.0 (2026-02-18)

Full Changelog: [v0.80.0...v0.81.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.80.0...v0.81.0)

### Features

* **api:** manual updates ([0a385c2](https://github.com/anthropics/anthropic-sdk-python/commit/0a385c29d26981f846b7394aefc89eebb43a4b60))

## 0.80.0 (2026-02-17)

Full Changelog: [v0.79.0...v0.80.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.79.0...v0.80.0)

### Features

* **api:** Releasing claude-sonnet-4-6 ([d518d6e](https://github.com/anthropics/anthropic-sdk-python/commit/d518d6ecede3d0638f0b14950dc2be8efa0b4ff4))


### Bug Fixes

* **api:** fix spec errors ([1413a76](https://github.com/anthropics/anthropic-sdk-python/commit/1413a76f905e590fab583417f5cb1eef9f537c2c))
* remove speed from ga messages ([#1402](https://github.com/anthropics/anthropic-sdk-python/issues/1402)) ([f6ce67c](https://github.com/anthropics/anthropic-sdk-python/commit/f6ce67c3ed5f2fc4a2fc48fb9d7bc6f1bbb5bd4a))


### Chores

* format all `api.md` files ([28a0eb5](https://github.com/anthropics/anthropic-sdk-python/commit/28a0eb55c031a9ed584eafe7f9096b32f9883e6f))
* **internal:** bump dependencies ([99f3014](https://github.com/anthropics/anthropic-sdk-python/commit/99f301460a3933229768d19fa7ae725072012592))
* **internal:** fix lint error on Python 3.14 ([a90d71b](https://github.com/anthropics/anthropic-sdk-python/commit/a90d71bfcdef5592f0f7f9a176cf347163ee2137))


### Refactors

* **vertex:** remove redundant isinstance check in `load_auth` ([#1387](https://github.com/anthropics/anthropic-sdk-python/issues/1387)) ([6b7a7dc](https://github.com/anthropics/anthropic-sdk-python/commit/6b7a7dce065b7bfbf6c5d8ed41825f36b36fc402))

## 0.79.0 (2026-02-07)

Full Changelog: [v0.78.0...v0.79.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.78.0...v0.79.0)

### Features

* **api:** enabling fast-mode in claude-opus-4-6 ([5953ba7](https://github.com/anthropics/anthropic-sdk-python/commit/5953ba7b425ba113595de570bc8c639ff4dc4047))


### Bug Fixes

* pass speed parameter through in sync beta count_tokens ([1dd6119](https://github.com/anthropics/anthropic-sdk-python/commit/1dd6119daca6de7a6eb730eb2494f368889ea050))

## 0.78.0 (2026-02-05)

Full Changelog: [v0.77.1...v0.78.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.77.1...v0.78.0)

### Features

* **api:** Release Claude Opus 4.6, adaptive thinking, and other features ([3ef1529](https://github.com/anthropics/anthropic-sdk-python/commit/3ef1529b45c55645646cc6043784f999fda088de))

## 0.77.1 (2026-02-03)

Full Changelog: [v0.77.0...v0.77.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.77.0...v0.77.1)

### Bug Fixes

* **structured outputs:** send structured output beta header when format is omitted ([#1158](https://github.com/anthropics/anthropic-sdk-python/issues/1158)) ([258494e](https://github.com/anthropics/anthropic-sdk-python/commit/258494e2b814a6a096b01e50f83560b4cf4a98ad))


### Chores

* remove claude-code-review workflow ([#1338](https://github.com/anthropics/anthropic-sdk-python/issues/1338)) ([aec4512](https://github.com/anthropics/anthropic-sdk-python/commit/aec4512305e8dce41df8ef0ab225f4939e099bcf))

## 0.77.0 (2026-01-29)

Full Changelog: [v0.76.0...v0.77.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.76.0...v0.77.0)

### Features

* **api:** add support for Structured Outputs in the Messages API ([ad56677](https://github.com/anthropics/anthropic-sdk-python/commit/ad5667774ad2e7efd181bcfda03fab3ea50630b9))
* **api:** migrate sending message format in output_config rather than output_format ([af405e4](https://github.com/anthropics/anthropic-sdk-python/commit/af405e473f7cf6091cb8e711264227b9b0508528))
* **client:** add custom JSON encoder for extended type support ([7780e90](https://github.com/anthropics/anthropic-sdk-python/commit/7780e90bd2fe4c1116d59bc0ad543aa609fc643d))
* use output_config for structured outputs ([82d669d](https://github.com/anthropics/anthropic-sdk-python/commit/82d669db652ed3d9aede61fd500fabb291b8f035))


### Bug Fixes

* **client:** run formatter ([2e4ff86](https://github.com/anthropics/anthropic-sdk-python/commit/2e4ff86d7b8bef8fe5c4b7e62bf47dfff79f0577))
* remove class causing breaking change ([#1333](https://github.com/anthropics/anthropic-sdk-python/issues/1333)) ([81ee953](https://github.com/anthropics/anthropic-sdk-python/commit/81ee9533d14f9dc3753a4a1320ea744825b17e92))
* **structured outputs:** avoid including beta header if `output_format` is missing ([#1121](https://github.com/anthropics/anthropic-sdk-python/issues/1121)) ([062077e](https://github.com/anthropics/anthropic-sdk-python/commit/062077e50d182719637403576f59761999b3b2f5))


### Chores

* **ci:** upgrade `actions/github-script` ([34df616](https://github.com/anthropics/anthropic-sdk-python/commit/34df6160ad386a7e8848e3435b22bd18bd726702))
* **internal:** update `actions/checkout` version ([ea50de9](https://github.com/anthropics/anthropic-sdk-python/commit/ea50de95bd1e43b8f00a45ef472330a3c8b396c8))

## 0.76.0 (2026-01-13)

Full Changelog: [v0.75.0...v0.76.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.75.0...v0.76.0)

### Features

* allow raw JSON schema to be passed to messages.stream() ([955c61d](https://github.com/anthropics/anthropic-sdk-python/commit/955c61dd5aae4c8a2c7b8fab1f97a0b88c0ef03b))
* **client:** add support for binary request streaming ([5302f27](https://github.com/anthropics/anthropic-sdk-python/commit/5302f2724c9890340c1b0dd042a1e670ed00eb93))
* **tool runner:** add support for server-side tools ([#1086](https://github.com/anthropics/anthropic-sdk-python/issues/1086)) ([1521316](https://github.com/anthropics/anthropic-sdk-python/commit/15213160a016a70538c81163c49ce5948fe06879))


### Bug Fixes

* **client:** loosen auth header validation ([5a0b89b](https://github.com/anthropics/anthropic-sdk-python/commit/5a0b89bb2c808cd0a413697a1141d4835ce00181))
* ensure streams are always closed ([388bd0c](https://github.com/anthropics/anthropic-sdk-python/commit/388bd0cbc53c4d8d8884d17a3051623728588eb4))
* **types:** allow pyright to infer TypedDict types within SequenceNotStr ([ede3242](https://github.com/anthropics/anthropic-sdk-python/commit/ede32426043273f9b31e70893207ad6519240591))
* use async_to_httpx_files in patch method ([718fa8e](https://github.com/anthropics/anthropic-sdk-python/commit/718fa8e62aa939dd8c5d46430aa1d1b05a5906d9))


### Chores

* add missing docstrings ([d306605](https://github.com/anthropics/anthropic-sdk-python/commit/d306605103649320e900ab3a2413d0dbd6b118c5))
* bump required `uv` version ([90634f3](https://github.com/anthropics/anthropic-sdk-python/commit/90634f3ef0a9d7ae5a1945f005b13aad245f6b32))
* **ci:** Add Claude Code GitHub Workflow ([#1293](https://github.com/anthropics/anthropic-sdk-python/issues/1293)) ([83d1c4a](https://github.com/anthropics/anthropic-sdk-python/commit/83d1c4aef1ae34b1aebe4ca25de8b0cd2d37a493))
* **deps:** mypy 1.18.1 has a regression, pin to 1.17 ([21c6374](https://github.com/anthropics/anthropic-sdk-python/commit/21c6374f3825f43e104bad4a5df71941bcf09844))
* **docs:** use environment variables for authentication in code snippets ([87aa378](https://github.com/anthropics/anthropic-sdk-python/commit/87aa378f13f64099bec9513cba85ba9723773ec4))
* fix docstring ([51fca79](https://github.com/anthropics/anthropic-sdk-python/commit/51fca7942b4e74e1357fb72828e8e39a8b8eea6a))
* **internal:** add `--fix` argument to lint script ([8914b7a](https://github.com/anthropics/anthropic-sdk-python/commit/8914b7abe9b98565f08f4965f7fd0da8cd9f1f08))
* **internal:** add missing files argument to base client ([6285abc](https://github.com/anthropics/anthropic-sdk-python/commit/6285abcba9945a7c6c6b713940ee0478dfe25008))
* **internal:** avoid using unstable Python versions in tests ([4547171](https://github.com/anthropics/anthropic-sdk-python/commit/4547171aba17e41ff2f2e2c13d319b6bc1a13e85))
* update lockfile ([d7ae1fc](https://github.com/anthropics/anthropic-sdk-python/commit/d7ae1fc9c06d7565b909e5c2d48ebeb63ee9d8c9))
* update uv.lock ([746ac05](https://github.com/anthropics/anthropic-sdk-python/commit/746ac05cbb18c7d596a381e2fe89d0ee3e4e94b9))

## 0.75.0 (2025-11-24)

Full Changelog: [v0.74.1...v0.75.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.74.1...v0.75.0)

### Features

* **api:** adds support for Claude Opus 4.5, Effort, Advance Tool Use Features, Autocompaction, and Computer Use v5 ([5c3e633](https://github.com/anthropics/anthropic-sdk-python/commit/5c3e633395acc100c45e8a403f1b5be4d17a3b32))


### Bug Fixes

* **internal:** small fixes ([36c82f7](https://github.com/anthropics/anthropic-sdk-python/commit/36c82f72b588bd549770a89072dd52d6f9e5b6a5))


### Chores

* fix lint issues ([4f1fd54](https://github.com/anthropics/anthropic-sdk-python/commit/4f1fd54143b79a4a7976dfb332ec7bfc666d1598))

## 0.74.1 (2025-11-19)

Full Changelog: [v0.74.0...v0.74.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.74.0...v0.74.1)

### Bug Fixes

* **structured outputs:** use correct beta header ([e90d347](https://github.com/anthropics/anthropic-sdk-python/commit/e90d347dfd80adc5ae2a412ebfe2eb55351ce08e))


### Chores

* **examples:** update model references ([e09461d](https://github.com/anthropics/anthropic-sdk-python/commit/e09461da36405bbb1a7ef616b9281457b2a6e20f))

## 0.74.0 (2025-11-18)

Full Changelog: [v0.73.0...v0.74.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.73.0...v0.74.0)

### Features

* add Foundry SDK ([3ae9e45](https://github.com/anthropics/anthropic-sdk-python/commit/3ae9e45451d3ff85b25ba5f5f9f8786ea35e3cc9))


### Bug Fixes

* **examples/memory:** properly add assistant_content to messages ([#1049](https://github.com/anthropics/anthropic-sdk-python/issues/1049)) ([9c7141b](https://github.com/anthropics/anthropic-sdk-python/commit/9c7141b887bbde251b6b740405a91d1726308c32))
* use posix paths in file collection for cross-platform compatibility ([d9c6f40](https://github.com/anthropics/anthropic-sdk-python/commit/d9c6f4006a43fe094acbf652a8dbd4234853ed70)), closes [#1051](https://github.com/anthropics/anthropic-sdk-python/issues/1051)


### Chores

* **internal:** remove unnecessary wrapper around external snapshots ([19eceac](https://github.com/anthropics/anthropic-sdk-python/commit/19eceac2406e4c71db14f9e870aaa901b4249219))


### Documentation

* explain snapshot update process ([#1040](https://github.com/anthropics/anthropic-sdk-python/issues/1040)) ([b61fd87](https://github.com/anthropics/anthropic-sdk-python/commit/b61fd87986a90105c20d4f35e34a9f69ec73645f))

## 0.73.0 (2025-11-14)

Full Changelog: [v0.72.1...v0.73.0](https://github.com/anthropics/anthropic-sdk-python/compare/v0.72.1...v0.73.0)

### Features

* **api:** add support for structured outputs beta ([688da81](https://github.com/anthropics/anthropic-sdk-python/commit/688da8126df8a304c5f01f0dc63cda437a62c217))

## 0.72.1 (2025-11-11)

Full Changelog: [v0.72.0...v0.72.1](https://github.com/anthropics/anthropic-sdk-python/compare/v0.72.0...v0.72.1)

### Bug Fixes

* **client:** close streams without requiring full consumption ([109b771](https://github.com/anthropics/anthropic-sdk-python/commit/109b77175c844c37e6e57899a732a0ba293a2942))
* compat with Python 3.14 ([bd2a137](https://github.com/anthropics/anthropic-sdk-python/commit/bd2a137a46cd899e28e81dd8d445dad23440674c))
* **compat:** update signatures of `model_dump` and `model_dump_json` for Pydantic v1 ([540f0f8](https://github.com/anthropics/anthropic-sdk-python/commit/540f0f8fdb0aa5d0d104259a59a0ee359296953e))


### Chores
