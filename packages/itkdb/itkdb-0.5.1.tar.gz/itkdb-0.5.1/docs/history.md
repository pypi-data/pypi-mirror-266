# itkdb history

---

All notable changes to itkdb will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

**_Changed:_**

**_Added:_**

**_Fixed:_**

## [0.5.0](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.5.0) - 2024-03-11 ## {: #itkdb-v0.5.0 }

**_Added:_**

- Command-line interfaces for [`itkdb eos upload`](../reference/cli/itkdb#itkdb-eos-upload) and [`itkdb eos delete`](../reference/cli/itkdb#itkdb-eos-upload)

**_Changed:_**

- Migrated relevant portions of `client.py` to `eos.py` for splitting out the EOS-specific functionality with `pycurl`

## [0.4.14](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.14) - 2024-02-15 ## {: #itkdb-v0.4.14 }

**_Fixed:_**

- Dropped `python-magic` dependency for Windows installations.

## [0.4.13](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.13) - 2023-11-30 ## {: #itkdb-v0.4.13 }

**_Fixed:_**

- Dropped `pylibmagic` dependency for Windows installations.

## [0.4.12](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.12) - 2023-11-15 ## {: #itkdb-v0.4.12 }

**_Fixed:_**

- Handle empty attachments properly, returning a [itkdb.models.BinaryFile][]
  instead of a `requests.models.Response` object, and not crashing with
  content-type / mimetype checks.

## [0.4.11](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.11) - 2023-10-30 ## {: #itkdb-v0.4.11 }

**_Fixed:_**

- Do not attempt to delete attachment from EOS if the token is not returned from
  ITk PD.

## [0.4.10](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.10) - 2023-10-27 ## {: #itkdb-v0.4.10 }

**_Fixed:_**

- Added a new `pycurl` callback `SEEKFUNCTION` to handle `EOS` redirects better
  to resolve errors like

  ```
  pycurl.error: (65, "necessary data rewind wasn't possible")
  ```

## [0.4.9](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.9) - 2023-10-18 ## {: #itkdb-v0.4.9 }

**_Fixed:_**

- Add upper bound on `urllib3` for CentOS7/SL7 machines to match `openssl`.
  Without the fix one gets something like

  ```
  ImportError: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips  26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
  ```

## [0.4.8](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.8) - 2023-09-12 ## {: #itkdb-v0.4.8 }

**_Fixed:_**

- [itkdb.responses.PagedResponse][] reruns authentication when paginating.

## [0.4.7](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.7) - 2023-08-30 ## {: #itkdb-v0.4.7 }

**_Added:_**

- `auth_expiry_threshold` to [itkdb.core.User][], [itkdb.core.Session][], and
  [itkdb.client.Client][] to force reauthentication sooner than when the token
  actually expires

## [0.4.6](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.6) - 2023-08-29 ## {: #itkdb-v0.4.6 }

**_Changed:_**

- Pagination will not keep history by default (see below for how to recover
  existing behavior)

**_Added:_**

- Keyword arguments for keeping pagination history, set to `False` by default to
  not keep previous pages
  - [itkdb.Client][] has a `pagination_history` keyword argument
  - [itkdb.responses.PagedResponse][] has a `history` keyword argument

**_Fixed:_**

- `itkdb authenticate` had a broken f-string

## [0.4.5](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.5) - 2023-07-14 ## {: #itkdb-v0.4.5 }

**_Added:_**

- Dependency on `python-magic-bin` for Windows installations

## [0.4.4](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.4) - 2023-06-02 ## {: #itkdb-v0.4.4 }

**_Added:_**

- Functionality to automatically delete attachments from EOS (if the attachment
  is on EOS)

## [0.4.3](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.3) - 2023-05-04 ## {: #itkdb-v0.4.3 }

**_Changed:_**

- Undo changes in [v0.4.3](#itkdb-v0.4.3)

**_Added:_**

- Upper-bound on `urllib3<2`

**_Fixed:_**

- Handle `json` attachments correctly

## [0.4.2](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.2) - 2023-05-01 ## {: #itkdb-v0.4.2 }

**_Fixed:_**

- Improved caching for later versions of `urllib3` where `HTTPResponse` object
  does not have `strict` attribute

## [0.4.1](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.1) - 2023-04-28 ## {: #itkdb-v0.4.1 }

**_Changed:_**

- Updated CERN TLS chain/certificates

**_Added:_**

- More examples to documentation
  - [Retrieve test type information from component](../examples/#retrieve-test-type-information-from-component)
  - [Retrieve a test run](../examples/#retrieve-a-test-run)
  - [Retrieve multiple tests](../examples/#retrieve-multiple-tests)
  - [Download an attachment from EOS](../examples/#download-an-attachment-from-eos)
  - [Load environment variables from file](../config/#load-environment-variables-from-file)

## [0.4.0](https://gitlab.cern.ch/atlas-itk/sw/db/itkdb/-/tags/v0.4.0) - 2023-03-02 ## {: #itkdb-v0.4.0 }

**_Added:_**

- This documentation website!
- Functionality to upload to EOS (`with_eos` argument to [itkdb.Client][])
- Automatic SSL verification for requests to `.cern.ch`
- `itkdb.utils`
  - [itkdb.utils.is_eos_uploadable][]
  - [itkdb.utils.is_root][]
  - [itkdb.utils.sizeof_fmt][]
- `itkdb.models`
  - [itkdb.models.BinaryFile][] as a base for all file models
  - [itkdb.models.ZipFile][] (!17)
- Configuration
  - audience, site, access scopes [`ITKDB_ACCESS_SCOPE`,
    `ITKDB_ACCESS_AUDIENCE`] (1c18ad6c2729af797eb5ea6c31c45b3517ea2db6,
    1942333f11a50e5a665d2ba00ac4e95954205733)
  - leeway [`ITKDB_LEEWAY`] (3dc7027d74f4966f26072bb75f33fc6664f39193)
- Support for python 3.11 (!19)
- `contrib` feature for rendering exceptions that return HTML (!20)
- [itkdb.data][] for data files (!15 for image/text data files and the CERN SSL
  cert chain, !24 for ROOT file)

**_Changed:_**

- Renamed `itkdb.utilities` to `itkdb.utils`
- `itkdb.models`
  - `itkdb.models.Image` to [itkdb.models.ImageFile][]
  - `itkdb.models.Text` to [itkdb.models.TextFile][]
- Improved handling of large data files by creating a temporary file on disk
  when downloading from ITkPD or EOS
- [itkdb.core.User][] arguments renamed from `accessCode1` / `accessCode2` to
  `access_code1` / `access_code2` to be more pythonic

**_Fixed:_**

- Fix `version` command when the version is dynamic and build dependencies are
  unmet
- Fixed bug in CLI for overriding base configuration settings (!14)
- Fixed bug in duplicated logging when redirects occur (!21)
