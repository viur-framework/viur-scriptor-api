---
covers: [viur.scriptor.file.File, viur.scriptor.file.File.upload, viur.scriptor.file.File._upload_to_gcs, viur.scriptor.requests.WebResponse]
status: accepted
---
## Seam
`File` is both the user-facing file object and the base class of `WebResponse` - every
HTTP response *is* a `File`, which is why `response.as_object_from_json()` and
`response.as_list_table()` exist. Uploading is a three-step handshake with the ViUR file
module, implemented in `File.upload`.

## Rules
- Do not assemble the upload yourself: `SECURE_POST /file/getUploadURL` ->
  PUT/POST the bytes to the returned `uploadUrl` -> `SECURE_POST /file/add/leaf` with the
  upload key. Skipping the third step leaves an orphaned blob in the bucket that the file
  module never learns about.
- `filename` must be set before `upload()`; it raises `ValueError` otherwise.
- Only `.csv` and `.xlsx` are supported for tables. On write the **extension** decides, on
  read the **sniffed mime type** does.

## Traps
- The mime type comes from the content (`magic.detect_from_content`), never from the
  filename. A `.csv` holding something else is uploaded under the sniffed type, and
  `as_list_table()` raises `ValueError`.
- `text/plain` is mapped to csv, so any plain text file is happily parsed as a
  single-column table instead of failing.
- `as_text()` without an explicit encoding guesses with `chardet`. On short files that
  guess is unreliable - pass the encoding when you know it.
- In the browser the bucket upload is sent with `mode: "no-cors"`; the response is opaque,
  so a failed upload cannot be detected there. Only the following `/file/add/leaf` reveals
  it.
- `File.from_url` goes through `modules.viur_request(raw=True)` and therefore needs an
  initialised session even for a foreign URL.
- `append()` silently does nothing for anything that is neither `bytes` nor `str`.

## See also
`module`, `dialog/open-file`, `dialog/save-file`, `runtime-split`
